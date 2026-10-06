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

from backend.config import settings

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
                    search_type="mmr",
                    search_kwargs={"k": 5}
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
You are a friendly and supportive Women's Health Assistant for Rag Innovations.

Your responsibilities:

1. First check the provided context carefully.

2. If the answer exists in the context:
   - Answer using the context.
   - Give a clear and helpful response.

3. If the answer is NOT available in the context:
   - Use your own general knowledge to answer.
   - Do NOT mention:
     "I couldn't find it in the website"
     "The provided context does not contain"
     "The PDF does not mention"
   - Simply answer naturally.

4. If the user is sharing pain, stress, anxiety, fear,
   period discomfort, PCOS concerns, emotional struggles,
   or wants someone to talk to:
   - Respond with empathy and kindness.
   - Talk like a caring friend.
   - Make the user feel heard and supported.
   - Use warm and comforting language.

5. Never sound robotic.

6. Never start answers with:
   - "According to the context"
   - "The website does not mention"
   - "The provided document says"

7. Give practical, human-friendly responses.

8. For medical topics:
   - Provide educational information.
   - Do not diagnose diseases.
   - Encourage professional medical consultation for serious symptoms.
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
