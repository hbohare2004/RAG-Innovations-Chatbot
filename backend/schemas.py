"""
Pydantic schemas for the Rag Innovations API.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat message request from the client."""
    message: str = Field(..., min_length=1, description="User's question or message")


class SourceDocument(BaseModel):
    """Metadata and snippet of a retrieved source chunk."""
    content: str = Field(..., description="Excerpt from the source document")
    source: Optional[str] = Field(None, description="URL or origin of the document")
    page: Optional[int] = Field(None, description="Page number if applicable")


class ChatResponse(BaseModel):
    """Response returned to the client."""
    answer: str = Field(..., description="Generated answer from the AI assistant")
    sources: List[SourceDocument] = Field(default_factory=list, description="List of source snippets used in context")
    status: str = Field(default="success", description="Response status (success/error)")


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(..., description="Overall health status")
    vectorstore_loaded: bool = Field(..., description="Whether vector database loaded successfully")
    embedding_model_loaded: bool = Field(..., description="Whether Mistral embeddings initialized")
    llm_loaded: bool = Field(..., description="Whether Groq LLM initialized")
    model_name: str = Field(..., description="Active LLM model name")
    error: Optional[str] = Field(None, description="Any initialization error details")
