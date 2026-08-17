import os
import tempfile
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from RAG.pdf import ask_pdf
from RAG.docx import ask_docx
from RAG.txt import ask_txt
from RAG.img import ask_image
from RAG.websearch import live_search, web_search, wiki_search , get_current_datetime
import prommpt
from pagestyle import page_layout , header , welcome_benner

# ============================================================
# SETUP & CONFIGURATION
# ============================================================
load_dotenv()

st.set_page_config(
    page_title="Jarvis AI | Multimodal Workspace",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Modern Styling (Glassmorphism & Gradients)
page_style = page_layout()

# Model & Chain Setup
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=os.getenv("GEMINI_API_KEY"),
    max_tokens=1000
)

SYSTEM_PROMPT = prommpt.get_system_prompt()

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
])

chain = prompt | llm | StrOutputParser()


# ============================================================
# UI - HEADER & SIDEBAR
# ============================================================

# Header Component
header = header()

# Sidebar Configuration
st.sidebar.title("⚙️ Settings")

lang = st.sidebar.selectbox(
    "Select Your Language",
    ["English", "Hindi", "Japanese", "German", "Spanish", "Urdu", "French"],
    index=0
)

st.sidebar.markdown("""
<div class="sidebar-card">
    <div class="sidebar-card-title">Capabilities</div>
    <div style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.6;">
        🔹 <b>Multi-turn Chat:</b> Contextual conversation<br/>
        🔹 <b>Document RAG:</b> PDF, DOCX, TXT Q&A<br/>
        🔹 <b>Vision Model:</b> Fruit & Object detection<br/>
        🔹 <b>Table Synthesis:</b> Automated comparison tables </br>
        🔹 <b>Web Search:</b> Internet Information Retrieval <br/>
    </div>
</div>
""", unsafe_allow_html=True)

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None


# Display Welcome Banner if Chat is Empty
if len(st.session_state.messages) == 0:
    welcome_benner()

# Render Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ============================================================
# MAIN CHAT INPUT & PROCESSING LOOP
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
    user_text = user_input.text.strip() if user_input.text else "Please analyze the attached files."

    # Render User Message
    with st.chat_message("user"):
        st.write(user_text)
        st.session_state.messages.append({
            "role": "user",
            "content": user_text,
        })

    # Handle Attached Files
    file_results = []
    if user_input.files:
        for file in user_input.files:
            st.markdown(f'<div class="file-tag">📎 Attached File: <b>{file.name}</b></div>', unsafe_allow_html=True)

            suffix = os.path.splitext(file.name)[1].lower()
            byte_file = file.read()

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
                temp_path = temp.name
                temp.write(byte_file)

            try:
                # ---------------- PDF ----------------
                if file.name.lower().endswith(".pdf"):
                    result = ask_pdf(temp_path, user_text)
                    file_results.append(f"PDF ({file.name}) Content:\n{result}")

                # ---------------- DOCX ----------------
                elif file.name.lower().endswith(".docx"):
                    result = ask_docx(temp_path, user_text)
                    file_results.append(f"DOCX ({file.name}) Content:\n{result}")

                # ---------------- TXT ----------------
                elif file.name.lower().endswith(".txt"):
                    result = ask_txt(temp_path, user_text)
                    file_results.append(f"TXT ({file.name}) Content:\n{result}")

                # ---------------- IMAGE ----------------
                elif file.name.lower().endswith((".jpg", ".jpeg", ".png")):
                    img_result = ask_image(temp_path, user_text)
                    img_info += f"\nImage ({file.name}):\n{img_result}\n"


            except Exception as e:
                st.error(f"Error reading {file.name}: {str(e)}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        if file_results:
            text = "\n\n".join(file_results)
    
    # ============================================================
    # Web Search / Real-Time Information Retrieval
    GREETINGS = {"hi", "hello", "hey", "namaste", "hola", "sup", "good morning", "good evening", "bye"}
    clean_prompt = user_text.lower().strip("!?., ")

    should_search = (
        clean_prompt not in GREETINGS
        and len(clean_prompt) > 3
    )

    web_search_result = ""
    wiki_search_result = ""
    current_time_str = ""

    if should_search:
        with st.spinner("Searching the web via DuckDuckGo..."):
            web_search_result = live_search(user_text)
            wiki_search_result = wiki_search(user_text)
            current_time_str = get_current_datetime()


    # Context Retrieval from Active Vectorstore (if present)
    if st.session_state.vectorstore is not None:
        try:
            retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 3})
            docs = retriever.invoke(user_text)
            text = "\n".join(doc.page_content for doc in docs)
        except Exception:
            pass

    # Build Conversation History
    history = ""
    for message in st.session_state.messages[:-1]:
        history += f"{message['role']} : {message['content']}\n"

    # Build Full Prompt
    full_prompt = f"""
        Conversation History:
        {history}

        Relevant File Content:
        {text}

        Relevant Image:
        {img_info}

        Current Question:
        {user_text}
        
        Recent Web Search Results:
        {web_search_result}

        Recent Wikipedia Search Results:
        {wiki_search_result}

        Current Date & Time:
        {current_time_str}

        Language:
        {lang}
    """

    # Generate Assistant Response
    with st.spinner("Generating Response..."):
        try:
            response = chain.invoke({"input": full_prompt})
        except Exception as e:
            response = f"An error occurred while communicating with the AI model: {str(e)}"

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
    })

    with st.chat_message("assistant"):
        st.markdown(response)