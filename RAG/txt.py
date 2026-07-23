import os
import streamlit as st
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings




def ask_txt(file_path: str, question: str):
    """
    Loads a PDF, builds/reuses a FAISS vectorstore in session_state,
    and returns the top-k relevant chunks for the given question.
    """
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    

    # Reuse the vectorstore across calls instead of rebuilding every time
    with st.spinner("PDF Loading..."):
            loader = TextLoader(file_path)
            docs = loader.load()

    with st.spinner("Splitting Text"):
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = splitter.split_documents(docs)

    with st.spinner("Building vectorstore..."):
            st.session_state.vectorstore = FAISS.from_documents(chunks, embedding)

    retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 3})
    results = retriever.invoke(question)

    if not results:
        return "No relevant content found in the PDF."

    return "\n\n".join(docs.page_content for docs in results)
