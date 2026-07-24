import os
import streamlit as st
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from RAG.pdf import get_embeddings


def ask_txt(file_path: str, question: str = ""):
    """
    Loads a TXT file, builds a FAISS vectorstore, and returns relevant text snippets.
    """
    embedding = get_embeddings()

    with st.spinner("Loading Text File..."):
        loader = TextLoader(file_path)
        docs = loader.load()

    with st.spinner("Splitting Text..."):
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)

    with st.spinner("Building vectorstore..."):
        vectorstore = FAISS.from_documents(chunks, embedding)
        st.session_state.vectorstore = vectorstore
        
    return "\n\n".join(doc.page_content for doc in docs)