# pyrefly: ignore [missing-import]
import os
import sys
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
# pyrefly: ignore [missing-import]
from langchain_community.vectorstores import Chroma
# pyrefly: ignore [missing-import]
from langchain_community.document_loaders import TextLoader
# pyrefly: ignore [missing-import]
from langchain_core.prompts import ChatPromptTemplate
# pyrefly: ignore [missing-import]
from langchain_community.document_loaders import PyPDFLoader
# pyrefly: ignore [missing-import]
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()

embedding_model = MistralAIEmbeddings()

vectorstore = Chroma(
    embedding_function=embedding_model,
    persist_directory="RagInno_DB"
)


retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k":5}
)

# LLM
model = ChatMistralAI(model = "mistral-small-2603")

# Prompt template
template = ChatPromptTemplate.from_messages(
    [
        ("system", """
You are the AI assistant for this website.

When relevant website information is available in the provided context:
- Use the website context as the primary source.
- Prefer website information over general knowledge.

When the user's question is general knowledge and the answer is not available in the website context:
- You may answer using your general knowledge.
- Clearly distinguish between website information and general knowledge when necessary.

For health-related questions:
- First remind the user that they should consult a qualified healthcare professional for personalized medical advice.
- Then provide general educational information.
- Never diagnose medical conditions.
- Never prescribe treatment.
- Encourage medical attention for severe or persistent symptoms.

Do not invent website-specific facts, prices, contact details, services, products, or company information that are not present in the context.
"""),
        (
            "human",
            """
Question: {question}

Website Context:
{context}
            """
        )
    ]
)

print("RAG System initialized. Ask your questions below (type '0' to exit).")
while True:
    query = input("\nAsk a question: ")
    if query.strip() == "0":
        print("Exiting...")
        break
    
    if not query.strip():
        continue
    
    # Retrieve relevant documents for the query
    docs = retriever.invoke(query)

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    # If very little context is found,
    # use general LLM knowledge
    if len(context.strip()) < 100:

        general_prompt = f"""
        User Question: {query}

        Answer the question using your general knowledge.

        If it is a health-related question:
            - First advise the user to consult a qualified doctor.
            - Then provide general educational information.
        """

        response = model.invoke(general_prompt)

    else:

        prompt = template.format_messages(
            question=query,
            context=context
        )

        response = model.invoke(prompt)

    print("\nAnswer:")
    print(response.content)

