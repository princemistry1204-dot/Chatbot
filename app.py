import os
from dotenv import load_dotenv
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


load_dotenv()

st.set_page_config(
    page_title="AI Story Teller",
    page_icon="📖",
    layout="wide"
)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.8
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert storyteller.

Rules:
- Tell immersive stories.
- Keep characters consistent within a single response.
- Use dialogue.
- End with a cliffhanger unless user asks to finish.
- Never break character.
"""
        ),
        ("human", "{input}")
    ]
)

chain = prompt | llm | StrOutputParser()    

st.sidebar.title("Story Settings")

genre = st.sidebar.selectbox(
    "Genre",
    ["Realistic", "Fantasy", "Sci-Fi", "Mystery", "Adventure", "Horror", "Romance", "Historical", "Comedy"]
)

hero = st.sidebar.text_input("Main Character", "Naruto")
place = st.sidebar.text_input("Place", "Leaf Village")

st.title("📖 AI Story Teller")
st.write("Generate story with conversation memory.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Continue the story...")

if user_input:
    # Build conversation history before appending the current input
    history = ""
    for msg in st.session_state.messages:
        history += f"{msg['role']}: {msg['content']}\n"

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    full_prompt = f"""
Create a {genre} story continuation.

Main character: {hero}
Place: {place}

Conversation History:
{history}

User input:
{user_input}
"""

    with st.spinner("Writing continuation..."):
        response = chain.invoke({"input": full_prompt})

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    with st.chat_message("assistant"):
        st.write(response)


    