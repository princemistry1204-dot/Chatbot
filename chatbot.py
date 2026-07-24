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
    "Select Your Language",
    ["English", "Hindi", "Japanese", "German", "Spanish", "Urdu", "French"],
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
user_input = st.chat_input(
    "Ask Anything",
    accept_file="multiple",
    file_type=["pdf", "docx", "txt", "jpg", "jpeg", "png"],
    accept_audio=True,
)

if user_input and (user_input.text or user_input.files):
    user_text = user_input.text.strip() if user_input.text else "Attached file analysis request"

    with st.chat_message("user"):
        st.write(user_text)
        st.session_state.messages.append({
            "role": "user",
            "content": user_text,
        })

    context = ""
    img_info = ""
    file_results = []

    # --------------------------------------------------------
    # Handle attached files
    # --------------------------------------------------------
    if user_input.files:
        for file in user_input.files:
            st.write(f"File Attached: {file.name}")

            suffix = os.path.splitext(file.name)[1].lower()
            byte_file = file.read()

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
                temp_path = temp.name
                temp.write(byte_file)

                # ---------------- PDF ----------------
                if file.name.lower().endswith(".pdf"):
                    result = ask_pdf(temp_path, user_text)
                    file_results.append(f"PDF ({file.name}) Content:\n{result}")
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

                # ---------------- DOCX ----------------
                elif file.name.lower().endswith(".docx"):
                    result = ask_docx(temp_path, user_text)
                    file_results.append(f"DOCX ({file.name}) Content:\n{result}")
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

                # ---------------- TXT ----------------
                elif file.name.lower().endswith(".txt"):
                    result = ask_txt(temp_path, user_text)
                    file_results.append(f"TXT ({file.name}) Content:\n{result}")
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

                # ---------------- IMAGE ----------------
                elif file.name.lower().endswith((".jpg", ".jpeg", ".png")):
                    img_result = ask_image(temp_path, user_text)
                    img_info += f"\nImage ({file.name}):\n{img_result}\n"
                
                else:
                    st.write(f"Unsupported file type: {file.name}")
                

        if file_results:
            context = "\n\n".join(file_results)

    # --------------------------------------------------------
    # Build conversation history
    # --------------------------------------------------------
    history = ""
    for msg in st.session_state.messages[:-1]: 
        history += f"{msg['role']} : {msg['content']}\n"

    full_prompt = f"""
Conversation History:
{history}

Relevant File Content:
{context}

Relevant Image:
{img_info}

Current Question:
{user_text}

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
