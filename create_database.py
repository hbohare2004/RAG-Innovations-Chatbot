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

loader = WebBaseLoader(web_paths=urls)

docs = loader.load()

print(f"Total pages loaded: {len(docs)}")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150
)

chunks = splitter.split_documents(docs)

print(f"Total chunks: {len(chunks)}")

embeddings = MistralAIEmbeddings()

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="RagInno_DB"
)

print("Vector DB created successfully!")