"""
Magnus RAG System
Retrieval Augmented Generation for financial knowledge base

Components:
- SimpleRAG: Basic RAG query interface
- DocumentIngestionPipeline: Document ingestion and embedding
- Daily XTrades sync (automated via Celery)
"""

from src.rag.simple_rag import SimpleRAG
from src.rag.document_ingestion_pipeline import (
    DocumentIngestionPipeline,
    DocumentCategory,
    DocumentSource,
    ingest_xtrades_daily,
    ingest_all_xtrades_history
)

__version__ = "1.0.0"

__all__ = [
    "SimpleRAG",
    "DocumentIngestionPipeline",
    "DocumentCategory",
    "DocumentSource",
    "ingest_xtrades_daily",
    "ingest_all_xtrades_history",
]
