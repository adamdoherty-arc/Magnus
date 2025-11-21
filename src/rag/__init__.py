"""
Magnus RAG System
=================

Production-ready Retrieval-Augmented Generation system with:
- Hybrid search (semantic + keyword)
- Adaptive retrieval
- Reranking
- Semantic chunking
- Autonomous learning
- Comprehensive evaluation

Based on 2025 best practices from:
- GitHub: NirDiamant/RAG_Techniques
- kapa.ai: Production lessons from 100+ teams
- Morgan Stanley: Financial AI assistant patterns
"""

from .rag_service import RAGService
from .document_indexer import DocumentIndexer

__all__ = [
    'RAGService',
    'DocumentIndexer'
]
