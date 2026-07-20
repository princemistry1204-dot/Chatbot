import keras
import kagglehub
import streamlit as st
from dotenv import load_dotenv
import tempfile
import os
from reportlab.pdfgen import canvas
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
# from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader , Docx2txtLoader , TextLoader
from langchain_core.output_parsers import StrOutputParser
import tensorflow as tf
import numpy as np
import cv2
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_community.vectorstores import FAISS

load_dotenv()

st.set_page_config(
    page_title="AI CHATBOT",
    page_icon="🤖",
    layout="wide"
)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    api_key=os.getenv("GROQ_API_KEY")
)
prompt = ChatPromptTemplate.from_messages(
    [
    
        (
            "system",
            """
Hey Jarvis i'am you'r friend Prince Mistry , you are a code assistant You'r Name is Jarvis ,image recognizer, and a friend, a storyteller, and a docx , txt or pdf question answerer and Generator.

Rules as assistant.
    - Understand the Question First.
    - You have to help the user.
    - Answer the question.
    - Work Smart.
    - Give Multiple Examples.
    - Ask Questions
    - Understand his emotions by the way te talk.
    - Appreciate him when he/she answer correct.
Rules as friend.
    - Talk as a best friend.
    - Help the friend if he is in a problem.
    - Highlight and bold the main topic.
    - Use Diagrams.
    - Use Different Font style and size.
    - Tell him jokes.
    - Be polite.
    - Be friendly.
    - Use Emojis
    - Understand his emotions by the way te talk.
    - Appreciate him when he/she answer correct.
Rules as storyteller.
    - Tell the story only when asked.
    - Tell immersive stories.
    - Keep characters consistent within a single response.
    - Use dialogue.
    - Use Emojis
    - End with a cliffhanger unless user asks to finish.
    - Never break character.
    - Highlight and bold the main topic.                               
Rules as a images recognizer, docx or txt or pdf reader.
    - Understand what the user attached with the question.
    - Open the file and read it carefully.
    - Understand the context.
    - Display the question in bigger font.
    - Answer the question correctly.
    - Read the file content and answer the question.
    - Generate pdf or docx or txt if user ask to Generate. 
    - Highlight and bold the main topic.
    - Use Diagrams.
"""
        ),
        ("human", "{input}")
    ]
)

chain = prompt | llm | StrOutputParser()

st.title("AI CHATBOT")

st.sidebar.title("Settings")

lang = st.sidebar.selectbox("Select You'r Language",["English","Hindi","Japaness","Germen","Spanish","Urdu","French"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
# embedding = GoogleGenerativeAIEmbeddings(
#     model = "google/gemini-embedding-2",
#     google_api_key = os.getenv("GEMINI_API_KEY")
# )

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
    batch_size=64
)

val_dataset = tf.keras.utils.image_dataset_from_directory(
    path,
    validation_split=0.2,
    subset="validation",
    seed=100,
    image_size=(128, 128),
    batch_size=64
)

history = ""
text = ""
img = ""
user_input = st.chat_input("Ask Anything",accept_file="multiple",file_type=["pdf","docx","txt","jpg","jpeg","png"],accept_audio=True)

if user_input and (user_input.text or user_input.files):
    with st.chat_message("user"):
        st.write(user_input.text)
        
        st.session_state.messages.append({
            "role" : "user",
            "content" : user_input.text
        })

        
    for file in user_input.files:
        st.write(f"File Atteched : - {file.name}")
        
        suffix = os.path.splitext(file.name)[1].lower()
        byte_file = file.read()
        with tempfile.NamedTemporaryFile(
            delete = False,
            suffix = suffix
        ) as temp:
            temp_path = temp.name
            temp.write(byte_file)
         
        response = None
        
        if file.name.endswith(".pdf"):
            with st.spinner("PDF Loading..."):
                loader = PyPDFLoader(temp_path)
            docs = loader.load()
            
            # splitter = RecursiveCharacterTextSplitter(
            #     chunk_size = 1000,
            #     chunk_overlap = 200
            # )
            # with st.spinner("Splitting Text"):
            #     chunks = splitter.split_documents(docs)
            # vectorstore = FAISS.from_documents(chunks,embedding)
            # retriver = vectorstore.as_retriever(
            # search_kwargs = {"k":3}
            # )
            
            # with st.spinner("Searching"):
            #     docs = retriver.invoke(user_input.text)
      
            text = "\n".join(doc.page_content for doc in docs)
                
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        elif file.name.endswith(".docx"):
            with st.spinner("DOCX Loading..."):
                loader = Docx2txtLoader(temp_path)
            docs = loader.load()
            
            # splitter = RecursiveCharacterTextSplitter(
            #     chunk_size = 1000,
            #     chunk_overlap = 200
            # )
            # with st.spinner("Splitting Text"):
            #     chunks = splitter.split_documents(docs)
            # vectorstore = FAISS.from_documents(chunks,embedding)
            # retriver = vectorstore.as_retriever(
            #     search_kwargs = {"k":3}
            # )           
            
            # with st.spinner("Searching"):
            #     docs = retriver.invoke(user_input.text)  
               
            text = "\n".join(doc.page_content for doc in docs)
            
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        elif file.name.endswith(".txt"):
            with st.spinner("TXT Loading..."):
                    loader = TextLoader(temp_path)
            docs = loader.load()
            
            # splitter = RecursiveCharacterTextSplitter(
            #     chunk_size = 1000,
            #     chunk_overlap = 200
            # ) 
            # with st.spinner("Splitting Text"):
            #     chunks = splitter.split_documents(docs)
            # vectorestore = FAISS.from_documents(chunks,embedding)
            # retriver = vectorestore.as_retriever(
            #     search_kwargs = {"k":3}
            # )
            
            # with st.spinner("Searching"):
            #     docs = retriver.invoke(user_input.text)
            
            text = "\n".join(doc.page_content for doc in docs)
             
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
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
        {user_input}

        Language:
        {lang}
"""

with st.spinner("Generating Response..."):
        response = chain.invoke({"input":full_prompt})
        
st.session_state.messages.append({
        "role":"assistant",
        "content" : response
    })     

with st.chat_message("assistant"):
        st.write(response)       
    