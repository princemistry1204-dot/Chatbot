import os
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


def get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def ask_pdf(file_path: str, question: str = ""):
    """
    Loads a PDF, builds a FAISS vectorstore, and returns relevant text snippets.
    """
    embedding = get_embeddings()

    with st.spinner("Loading PDF..."):
        loader = PyPDFLoader(file_path)
        docs = loader.load()

    with st.spinner("Splitting Text..."):
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)

    with st.spinner("Building vectorstore..."):
        vectorstore = FAISS.from_documents(chunks, embedding)
        st.session_state.vectorstore = vectorstore

    query_text = question if question else "Summarize key points"
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    results = retriever.invoke(query_text)

    if not results:
        return "No relevant content found in the PDF."

    return "\n\n".join(doc.page_content for doc in results)

