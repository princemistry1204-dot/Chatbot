import os
import tempfile

import cv2
import numpy as np
import tensorflow as tf
import keras
import kagglehub
import streamlit as st
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# --- Unused / future RAG imports (kept for later) ---
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_openai import ChatOpenAI
# from langchain_google_genai import GoogleGenerativeAIEmbeddings


# ============================================================
# SETUP
# ============================================================
load_dotenv()

st.set_page_config(
    page_title="AI CHATBOT",
    page_icon="🤖",
    layout="wide",
)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    api_key=os.getenv("GROQ_API_KEY"),
)

SYSTEM_PROMPT = """
You are Jarvis — a sharp, friendly AI assistant who can also read files, recognize images, and tell stories.
Adapt your role based on what the user is asking for. Stay in ONE mode per response; don't mix storyteller
mode with assistant mode in the same reply unless the user explicitly asks for both.

=== MODE 1: Assistant ===
Use this mode for questions, explanations, coding help, or general problem-solving.
- Understand the question fully before answering — ask a clarifying question if it's ambiguous.
- Give direct, correct, well-structured answers. Don't pad with fluff.
- Use examples where they aid understanding — 2-3 concrete examples for technical topics.
- Match the emotional tone of the user: if they sound frustrated, be reassuring and practical;
  if they're excited or joking, match that energy.
- Acknowledge good answers or good questions briefly and genuinely, not with exaggerated praise.

=== MODE 2: Friend ===
Use this mode when the user is venting, chatting casually, or wants a more personal conversation.
- Talk like a real, grounded friend — warm, casual, honest.
- Use bold for key points and emojis sparingly, only where they add warmth (not on every line).
- If the user shares a problem, listen first, then offer help — don't just crack jokes and move on.
- Keep advice practical and specific, not generic reassurance.

=== MODE 3: Storyteller ===
Use this mode ONLY when the user explicitly asks for a story.
- Write immersive, vivid stories with real dialogue and consistent characters within the response.
- Bold the central theme or twist once, don't over-format the whole story.
- End on a natural cliffhanger unless the user asks you to wrap it up.
- Never break character mid-story to explain what you're doing.

=== MODE 4: File / Image Analysis ===
Use this mode when the user has attached a PDF, DOCX, TXT, or image, or when retrieved document
context is provided to you.
- Base your answer STRICTLY on the provided file content / retrieved context — never invent details
  that aren't in it.
- If the retrieved context doesn't contain the answer, say so plainly instead of guessing.
- For images: report the classification result exactly as given (label + confidence) — don't
  speculate beyond what the model detected.
- If asked to generate a PDF, DOCX, or TXT file, confirm what content should go in it, then produce
  clear, well-organized text suitable for that format.
- Bold key facts (names, numbers, dates) pulled from the document so they stand out.

General rules across all modes:
- Never claim to have real-time internet access — you don't have one connected. If asked about
  something time-sensitive, say so honestly instead of guessing.
- Respond in the language selected by the user (see the Language field in the prompt).
- Keep formatting purposeful: bold for genuinely key terms, not every other word.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
])

chain = prompt | llm | StrOutputParser()


# ============================================================
# UI - HEADER / SIDEBAR
# ============================================================
st.title("AI CHATBOT")
st.sidebar.title("Settings")

lang = st.sidebar.selectbox(
    "Select You'r Language",
    ["English", "Hindi", "Japaness", "Germen", "Spanish", "Urdu", "French"],
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)

# ============================================================
# IMAGE MODEL DATA (fruit classifier)
# ============================================================
kaggle_dataset = kagglehub.dataset_download(
    "karimabdulnabi/fruit-classification10-class"
)
print("Dataset Downloaded Successfully...")

path = os.path.join(kaggle_dataset, "MY_data", "train")

train_dataset = tf.keras.utils.image_dataset_from_directory(
    path,
    validation_split=0.2,
    subset="training",
    seed=100,
    image_size=(128, 128),
    batch_size=64,
)


# ============================================================
# MAIN CHAT LOOP
# ============================================================
history = ""
text = ""
img = ""

user_input = st.chat_input(
    "Ask Anything",
    accept_file="multiple",
    file_type=["pdf", "docx", "txt", "jpg", "jpeg", "png"],
    accept_audio=True,
)

if user_input and (user_input.text or user_input.files):

    with st.chat_message("user"):
        st.write(user_input.text)
        st.session_state.messages.append({
            "role": "user",
            "content": user_input.text,
        })

    # --------------------------------------------------------
    # Handle attached files
    # --------------------------------------------------------
    if user_input.files:
        for file in user_input.files:
            st.write(f"File Atteched : - {file.name}")

            suffix = os.path.splitext(file.name)[1].lower()
            byte_file = file.read()

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
                temp_path = temp.name
                temp.write(byte_file)

            response = None

            # ---------------- PDF ----------------
            if file.name.endswith(".pdf"):
                with st.spinner("PDF Loading..."):
                    loader = PyPDFLoader(temp_path)
                    docs = loader.load()

                # --- Chunking / retrieval, disabled for now ---
                splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                with st.spinner("Splitting Text"):
                    chunks = splitter.split_documents(docs)
                vectorstore = FAISS.from_documents(chunks, embedding)
                st.session_state.vectorstore = vectorstore
                text = "\n".join(doc.page_content for doc in docs)

                if os.path.exists(temp_path):
                    os.remove(temp_path)

            # ---------------- DOCX ----------------
            elif file.name.endswith(".docx"):
                with st.spinner("DOCX Loading..."):
                    loader = Docx2txtLoader(temp_path)
                    docs = loader.load()

                # --- Chunking / retrieval, disabled for now ---
                splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                with st.spinner("Splitting Text"):
                    chunks = splitter.split_documents(docs)
                vectorstore = FAISS.from_documents(chunks, embedding)
                st.session_state.vectorstore = vectorstore
                text = "\n".join(doc.page_content for doc in docs)

                if os.path.exists(temp_path):
                    os.remove(temp_path)

            # ---------------- TXT ----------------
            elif file.name.endswith(".txt"):
                with st.spinner("TXT Loading..."):
                    loader = TextLoader(temp_path)
                    docs = loader.load()

                # --- Chunking / retrieval, disabled for now ---
                splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                with st.spinner("Splitting Text"):
                    chunks = splitter.split_documents(docs)
                vectorstore = FAISS.from_documents(chunks, embedding)
                st.session_state.vectorstore = vectorstore
                text = "\n".join(doc.page_content for doc in docs)

                if os.path.exists(temp_path):
                    os.remove(temp_path)

            # ---------------- IMAGE ----------------
            elif file.name.lower().endswith((".jpg", ".jpeg", ".png")):
                with st.spinner("Image Loading..."):
                    model = tf.keras.models.load_model("Fruit_Image_Classification_model.keras")

                img = cv2.imread(temp_path)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img_resized = cv2.resize(img_rgb, (128, 128))
                st.image(img_rgb, caption="Uploaded Image")

                img_array = keras.utils.img_to_array(img_resized)
                img_array = tf.expand_dims(img_array, 0)

                prediction = model.predict(img_array)
                score = tf.nn.softmax(prediction[0])
                predicted_index = np.argmax(score)
                confidence = float(np.max(score))

                predicted_label = train_dataset.class_names[predicted_index]
                img = f"Fruit detected: {predicted_label} (confidence: {confidence:.1%})"

                st.write(f"**Prediction:** {predicted_label} ({confidence:.1%} confidence)")

                if os.path.exists(temp_path):
                    os.remove(temp_path)

            else:
                pass
            
    if st.session_state.vectorstore is not None:
        retriever = st.session_state.vectorstore.as_retriever(
            search_kwargs={"k": 3})
            
        docs = retriever.invoke(user_input.text)
        text = "\n".join(doc.page_content for doc in docs)
    # --------------------------------------------------------
    # Build conversation history
    # --------------------------------------------------------
    for message in st.session_state.messages:
        history += f"{message['role']} : {message['content']}\n"

    full_prompt = f"""
        Conversation History:
        {history}

        Relevant File Content:
        {text}

        Relevant Image:
        {img}

        Current Question:
        {user_input.text}

        Language:
        {lang}
    """

    with st.spinner("Generating Response..."):
        response = chain.invoke({"input": full_prompt})

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
    })

    with st.chat_message("assistant"):
        st.write(response)