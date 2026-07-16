# import streamlit as st
# # from langchain_groq import ChatGroq
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_community.document_loaders import PyPDFLoader , Docx2txtLoader , TextLoader
# from langchain_core.output_parsers import StrOutputParser
# from dotenv import load_dotenv
# import os
# import tempfile
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_community.vectorstores import FAISS


# load_dotenv()

# st.set_page_config(
#     page_title="AI",
#     page_icon="📖",
#     layout="wide"
# )

# llm = ChatGoogleGenerativeAI(
#     model= "gemini-2.5-flash",
#     temperature=0.8,
#     google_api_key = os.getenv("GEMINI_API_KEY")
# )

# prompt = ChatPromptTemplate.from_messages([
    
#         (
#             "system",
#             """
# you are a code assistant, and a friend, a storyteller, and a file or pdf question answerer.

# Rules as assistant.
#     - Understand the Question First.
#     - You have to help the user.
#     - Answer the question.
#     - Work Smart.
#     - Give Multiple Examples.
#     - Ask Questions
# Rules as friend.
#     - Talk as a best friend.
#     - Help the friend if he is in a problem.
#     - Highlight and bold the main topic.
#     - Use Diagrams.
#     - Use Different Font style and size.
#     - Tell him jokes.
#     - Be polite.
#     - Be friendly.
# Rules as storyteller.
#     - Tell immersive stories.
#     - Keep characters consistent within a single response.
#     - Use dialogue.
#     - End with a cliffhanger unless user asks to finish.
#     - Never break character.
#     - Highlight and bold the main topic.                               
# Rules as a docx or txt or pdf reader.
#     - Understand what the user attached with the question.
#     - Open the file and read it carefully.
#     - Understand the context.
#     - Answer the question correctly.
#     - Read the file content and answer the question.
#     - Highlight and bold the main topic.
#     - Use Diagrams.
# """
#         ),
#         ("human", "{input}")
#     ]
# )
    
# chain = prompt | llm | StrOutputParser()

# st.title("AI")
# st.write("You'r Chatbot")
# st.sidebar.title("Settings")

# hero = st.sidebar.text_input("Main Character", "Naruto")
# place = st.sidebar.text_input("Place", "Leaf Village")
# lang = st.sidebar.selectbox("Select You'r Language",["hin","eng"])


# if "messages" not in st.session_state:
#     st.session_state.messages = []

# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.write(message["content"])

# user_input = st.chat_input("Ask Anything...",accept_file="multiple",file_type=["pdf","docx","txt"],accept_audio=True)

# if user_input and (user_input.text or user_input.files):
#     with st.chat_message("user"):
#         st.write(user_input.text)
        
    
#     st.session_state.messages.append({
#         "role":"user",
#         "content": user_input.text
#     })
    
#     response = None
    
#     for file in user_input.files:
#         st.write(f"File : - {file.name}")
        
#         suffix = os.path.splitext(file.name)[1].lower()
#         file_bytes = file.read()
        
#         with tempfile.NamedTemporaryFile(
#             delete=False,
#             suffix = suffix
#         ) as temp:
#             temp.write(file_bytes)
#             temp_path = temp.name
            
        
#         if file.name.endswith(".pdf"):
#             loader = PyPDFLoader(temp_path)
#             docs = loader.load()
#             splitter = RecursiveCharacterTextSplitter(
#                 chunk_size = 30,
#                 chunk_overlap = 10
#             )
#             docs = splitter.split_documents(docs)
#             text = "\n".join(doc.page_content for doc in docs)
            
            
            
#             response = chain.invoke({"input":f"""
                                    
#                                     file content:
#                                     {text}
                                    
#                                     user question:
#                                     {user_input.text}
                                    
#                                     """})
#         elif file.name.endswith(".docx"):
#             loader = Docx2txtLoader(temp_path)
#             docs = loader.load()
#             splitter = RecursiveCharacterTextSplitter(
#                 chunk_size = 30,
#                 chunk_overlap = 10
#             )
#             docs = splitter.split_documents(docs)
#             text = "\n".join(doc.page_content for doc in docs)
            
#             response = chain.invoke({"input":f"""
#                                     Read the file content and answer the question.
                                    
#                                     file content:
#                                     {text}
                                    
#                                     user question:
#                                     {user_input.text}
                                    
#                                     """})
#         elif file.name.endswith(".txt"):
#             loader = TextLoader(temp_path)
#             docs = loader.load()
#             splitter = RecursiveCharacterTextSplitter(
#                 chunk_size = 30,
#                 chunk_overlap = 10
#             )
#             docs = splitter.split_documents(docs)
#             text = "\n".join(doc.page_content for doc in docs)
            
#             response = chain.invoke({"input":f"""
#                                     Read the file content and answer the question.
                                    
#                                     file content:
#                                     {text}
                                    
#                                     user question:
#                                     {user_input.text}
                                    
#                                   """})
            
#             embedding = GoogleGenerativeAIEmbeddings(
#             model="models/text-embedding-004",
#             )
#             vectorstore = FAISS.from_documents(docs,embedding)
            
#             retriver = vectorstore.as_retriever(
#                 search_kwarg = {"k":3}
#             )
            
#             docs = retriver.invoke(user_input.text)
                        
#             if os.path.exists(temp_path):
#                 os.remove(temp_path)

# text = ""
# history = ""
# for message in st.session_state.messages:
#     history += f"{message['role']}: {message['content']}\n"

# full_prompt = f"""
#             Conversation History:
#             {history}
            
#             File Content:
#             {text}

#             Current Question:
#             {user_input}
#             """
        
# response = chain.invoke({
#                 "input": full_prompt
#             })
        
        
# st.session_state.messages.append({
#                 "role" :"assistant",
#                 "content": response
#             })
# with st.chat_message("assistant"):
#         st.write(response)        
        
        
        
