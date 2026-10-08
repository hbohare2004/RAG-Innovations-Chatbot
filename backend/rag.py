"""
Core RAG (Retrieval-Augmented Generation) pipeline for Rag Innovations.
Maintains singleton instance of embeddings, vector store retriever, and Groq LLM.
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional, Tuple

from langchain_mistralai import MistralAIEmbeddings
from langchain_groq import ChatGroq
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

try:
    from backend.config import settings
except ImportError:
    from config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """Singleton RAG Service managing retriever, Groq LLM, and prompt chains."""

    _instance: Optional["RAGService"] = None

    def __init__(self):
        self.retriever = None
        self.vectorstore = None
        self.model = None
        self.template = None
        self.embedding_model = None
        self.diagnostics: Dict[str, Any] = {
            "api_key_loaded": False,
            "mistral_key_present": False,
            "groq_key_present": False,
            "chroma_loaded": False,
            "doc_count": 0,
            "embedding_test": False,
            "retriever_ready": False,
            "llm_ready": False,
            "model_name": settings.LLM_MODEL,
            "errors": [],
            "python_version": sys.version,
        }
        self._initialize()

    def _resolve_chroma_path(self) -> str:
        """Find the chroma persist directory across common working directories."""
        candidates = [
            settings.CHROMA_PERSIST_DIR,
            os.path.join(os.path.dirname(__file__), settings.CHROMA_PERSIST_DIR),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), settings.CHROMA_PERSIST_DIR),
            os.path.join(os.path.dirname(__file__), "RagInno_DB"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "RagInno_DB"),
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return settings.CHROMA_PERSIST_DIR

    def _initialize(self):
        """Initialize all components with comprehensive error capturing."""
        mistral_key = settings.MISTRAL_API_KEY.strip().strip('"').strip("'")
        groq_key = settings.GROQ_API_KEY.strip().strip('"').strip("'")

        self.diagnostics["mistral_key_present"] = bool(mistral_key)
        self.diagnostics["groq_key_present"] = bool(groq_key)
        self.diagnostics["api_key_loaded"] = bool(mistral_key and groq_key)

        if not mistral_key:
            self.diagnostics["errors"].append("MISTRAL_API_KEY is empty or not set.")
        if not groq_key:
            self.diagnostics["errors"].append("GROQ_API_KEY is empty or not set.")

        # Ensure env vars are clean
        if mistral_key:
            os.environ["MISTRAL_API_KEY"] = mistral_key
        if groq_key:
            os.environ["GROQ_API_KEY"] = groq_key

        # 1. Initialize Embedding Model (Mistral Embeddings)
        try:
            if mistral_key:
                self.embedding_model = MistralAIEmbeddings(mistral_api_key=mistral_key)
                logger.info("✅ MistralAIEmbeddings initialized successfully.")
            else:
                self.embedding_model = None
        except Exception as e:
            self.diagnostics["errors"].append(f"Embedding model init failed: {e}")
            logger.error(f"Embedding model init failed: {e}")

        # 2. Load ChromaDB Vector Store
        chroma_dir = self._resolve_chroma_path()
        try:
            if self.embedding_model and os.path.exists(chroma_dir):
                self.vectorstore = Chroma(
                    embedding_function=self.embedding_model,
                    persist_directory=chroma_dir
                )
                self.diagnostics["chroma_loaded"] = True
                try:
                    collection = self.vectorstore._collection
                    self.diagnostics["doc_count"] = collection.count()
                except Exception as e:
                    self.diagnostics["doc_count"] = -1
                    self.diagnostics["errors"].append(f"Could not count docs: {e}")
                logger.info(f"✅ ChromaDB loaded from {chroma_dir}. Docs: {self.diagnostics['doc_count']}")
            else:
                self.diagnostics["errors"].append(f"ChromaDB path not found or embeddings not ready: {chroma_dir}")
        except Exception as e:
            self.diagnostics["errors"].append(f"ChromaDB loading failed: {e}")
            logger.error(f"ChromaDB loading failed: {e}")

        # 3. Test Embedding
        try:
            if self.embedding_model:
                test_emb = self.embedding_model.embed_query("test")
                if test_emb and len(test_emb) > 0:
                    self.diagnostics["embedding_test"] = True
                    logger.info(f"✅ Embedding test passed. Dim: {len(test_emb)}")
                else:
                    self.diagnostics["errors"].append("Embedding test returned empty vector.")
        except Exception as e:
            self.diagnostics["errors"].append(f"Embedding test failed: {e}")
            logger.error(f"Embedding test failed: {e}")

        # 4. Create Retriever
        try:
            if self.vectorstore:
                self.retriever = self.vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 4
    }
)
                self.diagnostics["retriever_ready"] = True
                logger.info("✅ Retriever created.")
        except Exception as e:
            self.diagnostics["errors"].append(f"Retriever creation failed: {e}")
            logger.error(f"Retriever creation failed: {e}")

        # 5. Initialize Groq LLM
        try:
            if groq_key:
                self.model = ChatGroq(
                    model=settings.LLM_MODEL,
                    groq_api_key=groq_key
                )
                self.diagnostics["llm_ready"] = True
                logger.info(f"✅ ChatGroq ({settings.LLM_MODEL}) initialized.")
            else:
                self.diagnostics["errors"].append("Groq LLM cannot be initialized without GROQ_API_KEY.")
        except Exception as e:
            self.diagnostics["errors"].append(f"LLM init failed: {e}")
            logger.error(f"LLM init failed: {e}")

        # 6. Chat Prompt Template
        self.template = ChatPromptTemplate.from_messages([
            (
                "system",
                """
You are RagAI, a friendly, supportive, and reliable Women's Health Assistant for Rag Innovations.

Your job is to answer users naturally, accurately, and helpfully while respecting the information available in the provided context.

## 1. Use the provided context

First, carefully analyze the provided context before answering.

For questions specifically about Rag Innovations, its products, machines, services, pricing, specifications, certifications, policies, programs, website content, or business information:

- Use ONLY information that is supported by the provided context.
- Do not invent, assume, estimate, or combine unrelated product information.
- Do not attribute general knowledge to Rag Innovations.
- If the required Rag Innovations-specific information is not available in the context, say naturally that you do not have that specific information and suggest contacting Rag Innovations for accurate details.

## 2. General knowledge

For general educational questions about menstrual health, hygiene, periods, women's health, or related topics:

- You may use your general knowledge when the answer is not available in the context.
- Clearly distinguish general educational information from information specifically provided by Rag Innovations.
- Never present general knowledge as an official Rag Innovations claim.

## 3. Accuracy and hallucination prevention

- Never fabricate product specifications, prices, capacities, certifications, features, guarantees, or business claims.
- Do not combine information from different products unless the context explicitly says they are related.
- If information is uncertain or incomplete, do not guess.
- Prefer a short honest answer over an invented detailed answer.

## 4. Response style

- Be friendly, natural, and conversational.
- Never sound robotic.
- Answer the user's actual question directly.
- Keep answers concise unless the user asks for more detail.
- Do not unnecessarily repeat information.
- Do not restate the user's question.

## 5. Formatting

- DO NOT use Markdown tables unless the user explicitly asks for a table, comparison, or tabular format.
- For normal questions, prefer short paragraphs.
- Use bullet points when listing features, benefits, or multiple items.
- Use numbered lists for step-by-step instructions.
- Use headings only when they improve readability.
- Avoid excessive formatting.

## 6. Women's health and emotional support

If the user is sharing pain, stress, anxiety, fear, period discomfort, PCOS concerns, emotional struggles, or simply wants someone to talk to:

- Respond with empathy and kindness.
- Use warm and supportive language.
- Make the user feel heard and respected.
- Talk naturally, like a caring and knowledgeable friend.
- Do not dismiss or minimize their feelings.

## 7. Medical topics

For medical and health-related questions:

- Provide general educational information.
- Do not diagnose diseases or medical conditions.
- Do not claim certainty about a user's medical condition.
- Encourage consultation with a qualified healthcare professional when symptoms are severe, persistent, unusual, or concerning.
- If there is an urgent or potentially dangerous symptom, recommend seeking appropriate medical care promptly.

## 8. Language

- Respond in the same language as the user whenever practical.
- If the user uses Hinglish, you may respond naturally in Hinglish.
- Keep technical or medical explanations easy to understand.

## 9. Final answer rule

Before responding, check:

1. Did I answer the actual question?
2. Am I using the provided context when the question is Rag Innovations-specific?
3. Did I accidentally mix information from different products?
4. Did I invent any facts?
5. Did I unnecessarily use a table?
6. Can the answer be shorter and more natural?

If the answer is supported by the context, answer confidently and naturally.
If it is not supported and is Rag Innovations-specific, do not guess.
"""
            ),
            (
                "human",
                """
Question:
{question}

Context:
{context}
"""
            )
        ])

    def query(self, user_question: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Execute RAG search and answer generation.
        Returns (answer_string, list_of_sources).
        """
        if not self.model:
            raise RuntimeError("LLM is not initialized. Please verify GROQ_API_KEY.")

        docs: List[Document] = []
        sources: List[Dict[str, Any]] = []

        if self.retriever:
            try:
                docs = self.retriever.invoke(user_question)

                for i, doc in enumerate(docs):
                    logger.info(
                        f"\n--- Retrieved Chunk {i + 1} ---\n"
                        f"Source: {doc.metadata.get('source')}\n"
                        f"{doc.page_content[:1000]}"
                    )

                for doc in docs:
                    source_url = doc.metadata.get("source") or doc.metadata.get("url") or None
                    page_num = doc.metadata.get("page")
                    # Clean snippet
                    snippet = doc.page_content.strip()
                    if len(snippet) > 300:
                        snippet = snippet[:297] + "..."
                    sources.append({
                        "content": snippet,
                        "source": source_url,
                        "page": page_num
                    })
            except Exception as e:
                logger.error(f"Retriever error: {e}")
                # Don't fail the request completely if retrieval errors out; fallback to LLM
                pass

        context = "\n\n".join([doc.page_content for doc in docs]) if docs else ""

        if len(context.strip()) < 100:
            general_prompt = f"""
            User Question: {user_question}

            Answer the question using your general knowledge with a supportive, warm, and professional tone.

            If it is a health-related question:
                - First advise the user to consult a qualified doctor or healthcare specialist.
                - Then provide general educational information.
            """
            response = self.model.invoke(general_prompt)
            # If fallback to general knowledge, do not display misleading sources
            sources = []
        else:
            prompt = self.template.format_messages(question=user_question, context=context)
            response = self.model.invoke(prompt)

        # ChatGroq content can be string
        answer_text = response.content if hasattr(response, "content") else str(response)
        return answer_text, sources


def get_rag_service() -> RAGService:
    """Get or create the singleton RAGService."""
    if RAGService._instance is None:
        RAGService._instance = RAGService()
    return RAGService._instance
