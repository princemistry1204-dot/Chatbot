import os
import tempfile


import streamlit as st
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from RAG.pdf import ask_pdf
from RAG.docx import ask_docx
from RAG.txt import ask_txt
from RAG.img import ask_image

import prommpt

# --- Unused / future RAG imports (kept for later) ---
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_openai import ChatOpenAI


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

SYSTEM_PROMPT = ()

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


# ============================================================
# MAIN CHAT LOOP
# ============================================================
history = ""
text = ""
img_info = ""

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
                ask_pdf(temp_path, user_input.text)
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                

            # ---------------- DOCX ----------------
            elif file.name.endswith(".docx"):
                ask_docx(temp_path, user_input.text)
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            # ---------------- TXT ----------------
            elif file.name.endswith(".txt"):
                ask_txt(temp_path, user_input.text)
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            # ---------------- IMAGE ----------------
            elif file.name.lower().endswith((".jpg", ".jpeg", ".png")):
                img_info = ask_image(temp_path, user_input.text)
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
        {img_info}

        Current Question:
        {user_input}

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