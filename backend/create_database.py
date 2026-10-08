"""
Standalone script to populate or refresh the Chroma vector database from live website URLs.
Uses MistralAIEmbeddings to ensure vector compatibility with existing RAG embeddings.
"""

import os
import sys
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

urls = [
    "https://www.raginnovations.com",
    "https://www.raginnovations.com/about",
    "https://www.raginnovations.com/services",
    "https://www.raginnovations.com/products",
    "https://www.raginnovations.com/gallery",
    "https://www.raginnovations.com/pricing",
    "https://www.raginnovations.com/contact",
    "https://www.raginnovations.com/school-mhm-compliance-solutions",
]

def build_vector_database(persist_directory: str = "RagInno_DB"):
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("ERROR: MISTRAL_API_KEY environment variable is required to create embeddings.")
        sys.exit(1)

    print(f"Loading web documents from {len(urls)} URLs...")
    loader = WebBaseLoader(web_paths=urls)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)

    for doc in chunks:
        source = doc.metadata.get("source", "")

        if "/products" in source:
            doc.metadata["page_type"] = "products"
        elif "/services" in source:
            doc.metadata["page_type"] = "services"
        elif "/pricing" in source:
            doc.metadata["page_type"] = "pricing"
        elif "/about" in source:
            doc.metadata["page_type"] = "about"
        else:
            doc.metadata["page_type"] = "general"

    print(f"Total pages loaded: {len(docs)}")
    print(f"Total chunks created: {len(chunks)}")

    embeddings = MistralAIEmbeddings(mistral_api_key=api_key)

    print(f"Persisting vector store to '{persist_directory}'...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    print("Vector DB created and persisted successfully!")

if __name__ == "__main__":
    build_vector_database()
