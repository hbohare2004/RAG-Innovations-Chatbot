"""
FastAPI application for Rag Innovations RAG Chatbot Backend.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.schemas import ChatRequest, ChatResponse, HealthResponse, SourceDocument
from backend.rag import get_rag_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("raginno-backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager to pre-load RAG models and Chroma vector store on startup."""
    logger.info("Initializing Rag Innovations backend RAG service...")
    try:
        service = get_rag_service()
        logger.info(f"RAG Service startup diagnostics: {service.diagnostics}")
    except Exception as e:
        logger.error(f"Failed to initialize RAG service on startup: {e}")
    yield
    logger.info("Rag Innovations backend shutting down.")


app = FastAPI(
    title="Rag Innovations AI Assistant API",
    description="Backend API powering the Rag Innovations RAG chatbot with Groq LLM and Mistral embeddings.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
origins = settings.CORS_ORIGINS
# Ensure localhost and dev ports are always present in dev
default_dev_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
for origin in default_dev_origins:
    if origin not in origins:
        origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https:\/\/.*\.vercel\.app",  # Allow any Vercel preview or production deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", summary="Root endpoint")
async def root():
    return {
        "name": "Rag Innovations AI Assistant API",
        "status": "online",
        "version": "1.0.0",
        "docs_url": "/docs"
    }


@app.get("/api/health", response_model=HealthResponse, summary="Service health check")
async def health_check():
    """Returns the initialization status and diagnostic details of the RAG system."""
    service = get_rag_service()
    diag = service.diagnostics
    
    is_healthy = diag.get("llm_ready", False) and diag.get("embedding_test", False) and diag.get("chroma_loaded", False)
    status_str = "healthy" if is_healthy else ("degraded" if diag.get("llm_ready", False) else "unhealthy")
    
    errors = diag.get("errors", [])
    error_summary = "; ".join(errors) if errors else None
    
    return HealthResponse(
        status=status_str,
        vectorstore_loaded=diag.get("chroma_loaded", False),
        embedding_model_loaded=diag.get("embedding_test", False),
        llm_loaded=diag.get("llm_ready", False),
        model_name=diag.get("model_name", settings.LLM_MODEL),
        error=error_summary
    )


@app.post("/api/chat", response_model=ChatResponse, summary="Ask a question to the RAG AI")
async def chat(request: ChatRequest):
    """Processes user query against knowledge base and returns AI generated answer with sources."""
    user_msg = request.message.strip()
    if not user_msg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question message cannot be empty."
        )

    try:
        service = get_rag_service()
        answer, sources_data = service.query(user_msg)
        
        sources = [
            SourceDocument(
                content=src.get("content", ""),
                source=src.get("source"),
                page=src.get("page")
            )
            for src in sources_data
        ]
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            status="success"
        )
    except Exception as e:
        logger.error(f"Error handling chat request: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "answer": f"I apologize, but I encountered an issue processing your request: {str(e)}",
                "sources": [],
                "status": "error"
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
