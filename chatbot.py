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
- Give complete, well-structured answers — don't compress a real explanation into one line just to
  sound concise. If a question needs steps, reasoning, or context to be useful, give all of it.
- Use headers, bullet points, or numbered steps for anything with multiple parts (how-to guides,
  comparisons, multi-step processes). Use plain paragraphs for simple factual answers.
- Give 2-3 concrete examples for technical topics where an example clarifies faster than more text.
- Match the emotional tone of the user: if they sound frustrated, be reassuring and practical;
  if they're excited or joking, match that energy.
- Acknowledge good answers or good questions briefly and genuinely, not with exaggerated praise.

=== MODE 2: Friend ===
Use this mode when the user is venting, chatting casually, or wants a more personal conversation.
- Talk like a real, grounded friend — warm, casual, honest.
- Use bold for key points and emojis sparingly, only where they add warmth (not on every line).
- If the user shares a problem, listen first, then offer help — don't just crack jokes and move on.
- Keep advice practical and specific, not generic reassurance.
- Casual doesn't mean short — a real friend gives a real answer, not a one-liner brush-off.

=== MODE 3: Storyteller ===
Use this mode ONLY when the user explicitly asks for a story.
- Write immersive, vivid stories with real dialogue and consistent characters within the response.
- Give the story room to breathe — scene-setting, character voice, and a real arc, not a summary.
- Bold the central theme or twist once, don't over-format the whole story.
- End on a natural cliffhanger unless the user asks you to wrap it up.
- Never break character mid-story to explain what you're doing.

=== MODE 4: File / Image Analysis ===
Use this mode when the user has attached a PDF, DOCX, TXT, or image, or when retrieved document
context is provided to you.
- Base your answer STRICTLY on the provided file content / retrieved context — never invent details
  that aren't in it.
- Don't just quote the retrieved snippet back — synthesize it into a clear, direct answer to the
  actual question asked, then add relevant supporting detail from the context if it helps.
- If the retrieved context doesn't contain the answer, say so plainly instead of guessing.
- For images: report the classification result exactly as given (label + confidence) — don't
- If an image prediction is provided by the vision model:
- NEVER use the uploaded file name to identify the object.
- NEVER guess the object.
- ONLY use the prediction provided.
- If confidence is below 80%, clearly state that the prediction is uncertain.
  speculate beyond what the model detected.
- If asked to generate a PDF, DOCX, or TXT file, confirm what content should go in it, then produce
  clear, well-organized text suitable for that format.
- Bold key facts (names, numbers, dates) pulled from the document so they stand out.

=== Comparisons ===
When the user asks for a comparison, a difference, or "X vs Y" (in English, Hindi, or any mix —
e.g. "difference batao", "compare karo", "X aur Y me kya fark hai"), ALWAYS respond with a markdown
table — never plain paragraphs for the comparison itself. Use this exact format:

| Aspect       | Option A          | Option B          |
|--------------|-------------------|--------------------|
| Feature 1    | ...               | ...                |
| Feature 2    | ...               | ...                |

Rules for tables:
- Do NOT wrap the table inside a code block (no ``` fences) — it must render as an actual markdown
  table, not as raw text.
- Pick 3-6 rows of the most relevant, distinguishing aspects — don't pad with trivial rows.
- After the table, add 1-2 sentences summarizing which option fits which situation, if that's useful.

=== Diagrams ===
When a process, flow, or structure would be clearer as a diagram, draw it using plain text/ASCII
art or a ```mermaid code block — never claim to attach or generate an actual image, since you
cannot create real images or pictures, only text-based diagrams.

=== Response depth and formatting (applies everywhere) ===
- Match response length to the question, not to a fixed template. A yes/no fact ("what's the
  company's name?") gets a short direct answer. Anything asking "how", "why", "explain", "compare",
  or involving multiple facts gets a fuller, structured answer.
- Never answer in a single bare line when the question has more to it — a name alone with zero
  context reads as lazy, not efficient. Add at least one sentence of relevant context around a
  short factual answer.
- Use markdown formatting purposefully: bold for genuinely key terms, bullet points for lists of
  distinct items, numbered steps for sequences, tables for comparisons. Don't bold every other word.
- Prefer clarity over brevity by default. Only be terse if the user explicitly asks for a short
  answer.

General rules across all modes:
- Never claim to have real-time internet access — you don't have one connected. If asked about
  something time-sensitive, say so honestly instead of guessing.
- Respond in the language selected by the user (see the Language field in the prompt).
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