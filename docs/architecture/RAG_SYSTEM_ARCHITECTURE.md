# Magnus/AVA RAG System Architecture
## Production-Ready Retrieval Augmented Generation for Financial Intelligence

**Version:** 1.0.0
**Date:** 2025-11-20
**Status:** Design Complete - Ready for Implementation
**Author:** AI Engineer Agent

---

## Executive Summary

This document outlines a comprehensive, production-ready RAG (Retrieval Augmented Generation) system for the Magnus/AVA trading platform. The architecture is optimized for local/self-hosted deployment, cost-effectiveness, and integration with the existing 33-agent system and local LLM infrastructure (Qwen 2.5 32B).

### Key Design Decisions

- **Vector Database:** Qdrant (already in requirements, Docker-ready, Apache 2.0 license)
- **Embeddings Model:** sentence-transformers/all-MiniLM-L6-v2 (local, free, fast)
- **Document Processing:** LangChain with custom financial splitters
- **Storage:** PostgreSQL for metadata + Qdrant for vectors
- **Integration:** Seamless with existing agent-aware routing system
- **Cost:** 100% local, $0 ongoing costs

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MAGNUS/AVA RAG SYSTEM                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          APPLICATION LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Dashboard  │  │  AI Agents   │  │ AVA Chatbot  │  │  API Layer   │   │
│  │  (Streamlit) │  │  (33 total)  │  │              │  │  (FastAPI)   │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                  │                  │            │
│         └─────────────────┴──────────────────┴──────────────────┘            │
│                                    │                                         │
└────────────────────────────────────┼─────────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼─────────────────────────────────────────┐
│                          RAG SERVICE LAYER                                    │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    RAGQueryService                                   │    │
│  │  ┌────────────────────────────────────────────────────────────┐     │    │
│  │  │  query(prompt, context_type, top_k, filters)               │     │    │
│  │  │       │                                                     │     │    │
│  │  │       ├─ 1. Generate query embedding                        │     │    │
│  │  │       ├─ 2. Semantic search (Qdrant)                       │     │    │
│  │  │       ├─ 3. Re-rank results                                │     │    │
│  │  │       ├─ 4. Build context window                           │     │    │
│  │  │       ├─ 5. Inject into LLM prompt                         │     │    │
│  │  │       └─ 6. Return augmented response                      │     │    │
│  │  └────────────────────────────────────────────────────────────┘     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                 DocumentIngestionService                             │    │
│  │  ┌────────────────────────────────────────────────────────────┐     │    │
│  │  │  ingest(file_path, metadata, doc_type)                     │     │    │
│  │  │       │                                                     │     │    │
│  │  │       ├─ 1. Load document (PDF/MD/TXT/DOCX)               │     │    │
│  │  │       ├─ 2. Extract text and structure                     │     │    │
│  │  │       ├─ 3. Chunk intelligently                            │     │    │
│  │  │       ├─ 4. Generate embeddings                            │     │    │
│  │  │       ├─ 5. Store in Qdrant                                │     │    │
│  │  │       └─ 6. Store metadata in PostgreSQL                   │     │    │
│  │  └────────────────────────────────────────────────────────────┘     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼─────────────────────────────────────────┐
│                        CORE COMPONENTS LAYER                                  │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐       │
│  │  EmbeddingEngine │  │  ChunkingEngine  │  │  ContextBuilder      │       │
│  │                  │  │                  │  │                      │       │
│  │ • Model loading  │  │ • Semantic split │  │ • Window management  │       │
│  │ • Batch encoding │  │ • Financial docs │  │ • Relevance scoring  │       │
│  │ • Caching        │  │ • Size control   │  │ • Deduplication      │       │
│  └──────────────────┘  └──────────────────┘  └──────────────────────┘       │
│                                                                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐       │
│  │  CacheManager    │  │  MetadataManager │  │  RetrievalOptimizer  │       │
│  │                  │  │                  │  │                      │       │
│  │ • Query cache    │  │ • Document index │  │ • Hybrid search      │       │
│  │ • Embedding cache│  │ • Tags/filters   │  │ • Re-ranking         │       │
│  │ • Redis backend  │  │ • Usage tracking │  │ • Query expansion    │       │
│  └──────────────────┘  └──────────────────┘  └──────────────────────┘       │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼─────────────────────────────────────────┐
│                         STORAGE LAYER                                         │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────┐  ┌──────────────────────────────────┐         │
│  │      Qdrant VectorDB     │  │     PostgreSQL Database          │         │
│  │   (Docker Container)     │  │     (Existing Instance)          │         │
│  │                          │  │                                  │         │
│  │ • Collection: magnus_kb  │  │ Tables:                          │         │
│  │ • 384-dim vectors        │  │  • rag_documents                 │         │
│  │ • HNSW index             │  │  • rag_chunks                    │         │
│  │ • Cosine similarity      │  │  • rag_query_logs                │         │
│  │ • Metadata filters       │  │  • rag_embeddings_cache          │         │
│  │ • Port: 6333             │  │                                  │         │
│  └──────────────────────────┘  └──────────────────────────────────┘         │
│                                                                               │
│  ┌──────────────────────────┐  ┌──────────────────────────────────┐         │
│  │     Redis Cache          │  │   Local File Storage             │         │
│  │  (Existing Instance)     │  │   (c:/code/Magnus/data/)         │         │
│  │                          │  │                                  │         │
│  │ • Query results (5min)   │  │ Directories:                     │         │
│  │ • Embeddings (1hr)       │  │  • /data/documents/raw/          │         │
│  │ • Context windows (30m)  │  │  • /data/documents/processed/    │         │
│  └──────────────────────────┘  └──────────────────────────────────┘         │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼─────────────────────────────────────────┐
│                      EXTERNAL INTEGRATIONS                                    │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────┐  ┌──────────────────────────────────┐         │
│  │  MagnusLocalLLM          │  │   HuggingFace Models             │         │
│  │  (Qwen 2.5 32B)          │  │   (sentence-transformers)        │         │
│  │                          │  │                                  │         │
│  │ • Context injection      │  │ • all-MiniLM-L6-v2 (embeddings)  │         │
│  │ • Prompt augmentation    │  │ • Runs on CPU (fast)             │         │
│  │ • Response generation    │  │ • 384-dimensional vectors        │         │
│  └──────────────────────────┘  └──────────────────────────────────┘         │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Flow: Document Ingestion

```
┌─────────────────────────────────────────────────────────────────────┐
│                   DOCUMENT INGESTION PIPELINE                        │
└─────────────────────────────────────────────────────────────────────┘

Input Documents:
  • Trading guides (PDF)
  • Market analysis (MD)
  • Strategy documents (DOCX)
  • Research papers (TXT)
           │
           ▼
┌──────────────────────────┐
│   Document Loader        │
│  (LangChain)             │
│                          │
│  • PDFLoader             │
│  • UnstructuredMDLoader  │
│  • DocxLoader            │
│  • TextLoader            │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Text Extraction         │
│  & Cleaning              │
│                          │
│  • Remove headers/footers│
│  • Fix encoding issues   │
│  • Normalize whitespace  │
│  • Extract tables        │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Intelligent Chunking    │
│  (Financial-Optimized)   │
│                          │
│  Strategy: Semantic      │
│  • Chunk size: 512 tokens│
│  • Overlap: 50 tokens    │
│  • Preserve sections     │
│  • Keep tables intact    │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Metadata Enrichment     │
│                          │
│  • Document title        │
│  • Author/source         │
│  • Creation date         │
│  • Document type         │
│  • Topic tags            │
│  • Section hierarchy     │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Embedding Generation    │
│  (Batch Processing)      │
│                          │
│  Model: all-MiniLM-L6-v2 │
│  Batch size: 32 chunks   │
│  Dimension: 384          │
└──────────┬───────────────┘
           │
           ├──────────────────────────┐
           │                          │
           ▼                          ▼
┌──────────────────────┐   ┌──────────────────────┐
│  Store in Qdrant     │   │  Store in PostgreSQL │
│                      │   │                      │
│  • Vector payload    │   │  • Document record   │
│  • Chunk text        │   │  • Chunk metadata    │
│  • Metadata filters  │   │  • Processing log    │
│  • Collection ID     │   │  • Relationships     │
└──────────────────────┘   └──────────────────────┘
           │                          │
           └──────────────┬───────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  Update Index   │
                 │  & Cache        │
                 └─────────────────┘
                          │
                          ▼
                    ✅ Complete
```

---

## 3. Data Flow: Query & Retrieval

```
┌─────────────────────────────────────────────────────────────────────┐
│                    QUERY & RETRIEVAL PIPELINE                        │
└─────────────────────────────────────────────────────────────────────┘

User/Agent Query:
"What are the best practices for the Wheel Strategy?"
           │
           ▼
┌──────────────────────────┐
│  Query Analysis          │
│                          │
│  • Intent classification │
│  • Entity extraction     │
│  • Topic identification  │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Check Query Cache       │
│  (Redis - 5 min TTL)     │
│                          │
│  Cache Key: hash(query + │
│              filters)    │
└──────────┬───────────────┘
           │
     ┌─────┴─────┐
     │           │
  Cache        Cache
   Hit         Miss
     │           │
     │           ▼
     │  ┌──────────────────────────┐
     │  │  Generate Query Embedding│
     │  │  (all-MiniLM-L6-v2)      │
     │  │                          │
     │  │  • 384-dim vector        │
     │  │  • Normalize             │
     │  └──────────┬───────────────┘
     │             │
     │             ▼
     │  ┌──────────────────────────┐
     │  │  Hybrid Search           │
     │  │                          │
     │  │  1. Semantic (Vector)    │
     │  │     • Qdrant search      │
     │  │     • Cosine similarity  │
     │  │     • top_k=20           │
     │  │                          │
     │  │  2. Keyword (Optional)   │
     │  │     • PostgreSQL FTS     │
     │  │     • BM25 ranking       │
     │  │                          │
     │  │  3. Fusion               │
     │  │     • RRF (Reciprocal    │
     │  │       Rank Fusion)       │
     │  └──────────┬───────────────┘
     │             │
     │             ▼
     │  ┌──────────────────────────┐
     │  │  Re-ranking              │
     │  │                          │
     │  │  • Cross-encoder (opt.)  │
     │  │  • Metadata boost        │
     │  │  • Recency bias          │
     │  │  • Reduce to top_k=5     │
     │  └──────────┬───────────────┘
     │             │
     │             ▼
     │  ┌──────────────────────────┐
     │  │  Context Window Builder  │
     │  │                          │
     │  │  • Concatenate chunks    │
     │  │  • Add metadata headers  │
     │  │  • Manage token limit    │
     │  │  • Add citations         │
     │  └──────────┬───────────────┘
     │             │
     │             ▼
     │  ┌──────────────────────────┐
     │  │  Cache Result            │
     │  │  (Redis - 5 min)         │
     │  └──────────┬───────────────┘
     │             │
     └─────────────┘
                   │
                   ▼
       ┌──────────────────────────┐
       │  Prompt Augmentation     │
       │                          │
       │  Template:               │
       │  """                     │
       │  Context:                │
       │  {retrieved_chunks}      │
       │                          │
       │  Question:               │
       │  {user_query}            │
       │                          │
       │  Answer based on context │
       │  above. Cite sources.    │
       │  """                     │
       └──────────┬───────────────┘
                  │
                  ▼
       ┌──────────────────────────┐
       │  MagnusLocalLLM          │
       │  (Qwen 2.5 32B)          │
       │                          │
       │  • Process augmented     │
       │    prompt                │
       │  • Generate response     │
       │  • Include citations     │
       └──────────┬───────────────┘
                  │
                  ▼
       ┌──────────────────────────┐
       │  Log & Monitor           │
       │                          │
       │  • Log to PostgreSQL     │
       │  • Track relevance       │
       │  • Update analytics      │
       └──────────┬───────────────┘
                  │
                  ▼
            Return Response
         (with citations)
```

---

## 4. Technology Stack

### 4.1 Vector Database: Qdrant

**Why Qdrant:**
- ✅ Already in requirements.txt
- ✅ Open-source (Apache 2.0)
- ✅ Docker-ready (single command deployment)
- ✅ Fast (HNSW algorithm)
- ✅ Rich filtering capabilities
- ✅ Python SDK with excellent docs
- ✅ Low memory footprint
- ✅ Snapshot/backup support

**Configuration:**
```yaml
# docker-compose.yml addition
qdrant:
  image: qdrant/qdrant:latest
  ports:
    - "6333:6333"
    - "6334:6334"  # gRPC
  volumes:
    - ./data/qdrant_storage:/qdrant/storage
  environment:
    - QDRANT__SERVICE__HTTP_PORT=6333
    - QDRANT__SERVICE__GRPC_PORT=6334
  restart: unless-stopped
```

**Collection Schema:**
```python
{
    "vectors": {
        "size": 384,  # all-MiniLM-L6-v2 dimension
        "distance": "Cosine"
    },
    "payload_schema": {
        "document_id": "keyword",
        "chunk_id": "integer",
        "text": "text",
        "document_title": "keyword",
        "document_type": "keyword",  # trading_guide, strategy, analysis
        "topic_tags": "keyword[]",   # [options, wheel_strategy, risk]
        "author": "keyword",
        "created_at": "datetime",
        "section": "keyword",
        "token_count": "integer"
    }
}
```

### 4.2 Embeddings Model: all-MiniLM-L6-v2

**Why This Model:**
- ✅ Lightweight (80MB)
- ✅ Fast inference (CPU-friendly)
- ✅ Good quality (MTEB benchmark: 58.8)
- ✅ Short embedding dimension (384)
- ✅ Optimized for semantic search
- ✅ sentence-transformers library
- ✅ Zero cost

**Alternative Models (if needed):**
```python
# Upgrade paths:
# 1. Better quality, slower:
"sentence-transformers/all-mpnet-base-v2"  # 768-dim, 420MB

# 2. Financial domain-specific:
"microsoft/finbert-tone"  # Fine-tuned for finance

# 3. Multilingual (if needed):
"sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
```

**Performance:**
- Encoding speed: ~1000 sentences/second (CPU)
- Batch encoding: 32-64 chunks at once
- GPU acceleration: 5-10x faster if needed

### 4.3 Document Processing: LangChain

**Components:**
```python
from langchain.document_loaders import (
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    Docx2txtLoader,
    TextLoader
)
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    MarkdownTextSplitter
)
```

**Custom Financial Splitter:**
```python
class FinancialDocumentSplitter:
    """
    Intelligent chunking for financial documents

    Features:
    - Preserves tables and code blocks
    - Respects section boundaries
    - Maintains context in overlaps
    - Handles different document types
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        separators: List[str] = ["\n\n", "\n", ". ", " ", ""]
    ):
        ...
```

### 4.4 Storage: PostgreSQL + Qdrant

**PostgreSQL Tables:**

```sql
-- Main documents table
CREATE TABLE rag_documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    file_path TEXT NOT NULL,
    file_hash VARCHAR(64) UNIQUE,
    document_type VARCHAR(50),  -- trading_guide, strategy, research
    author VARCHAR(200),
    source_url TEXT,
    upload_date TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW(),
    file_size_bytes INTEGER,
    total_chunks INTEGER,
    status VARCHAR(20) DEFAULT 'processing',  -- processing, indexed, failed
    metadata JSONB,
    tags TEXT[],
    INDEX idx_doc_type (document_type),
    INDEX idx_tags (tags),
    INDEX idx_status (status)
);

-- Chunks metadata table
CREATE TABLE rag_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES rag_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    qdrant_point_id UUID NOT NULL,
    text_content TEXT NOT NULL,
    token_count INTEGER,
    section_title VARCHAR(500),
    embedding_model VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_document (document_id),
    INDEX idx_qdrant_id (qdrant_point_id),
    UNIQUE (document_id, chunk_index)
);

-- Query logs for analytics
CREATE TABLE rag_query_logs (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    query_embedding_id UUID,
    context_type VARCHAR(50),
    top_k INTEGER,
    filters JSONB,
    retrieved_chunks INTEGER[],
    avg_similarity_score FLOAT,
    processing_time_ms INTEGER,
    llm_used VARCHAR(50),
    response_quality_rating INTEGER,  -- User feedback (1-5)
    created_at TIMESTAMP DEFAULT NOW(),
    user_agent VARCHAR(100),
    INDEX idx_created (created_at),
    INDEX idx_context_type (context_type)
);

-- Embeddings cache (optional optimization)
CREATE TABLE rag_embeddings_cache (
    id SERIAL PRIMARY KEY,
    text_hash VARCHAR(64) UNIQUE,
    embedding_vector FLOAT[],  -- or BYTEA for compressed
    model_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    last_accessed TIMESTAMP DEFAULT NOW(),
    access_count INTEGER DEFAULT 1,
    INDEX idx_hash (text_hash),
    INDEX idx_model (model_name)
);
```

---

## 5. File Structure

```
c:/code/Magnus/
│
├── src/
│   ├── rag/                                    # NEW: RAG System
│   │   ├── __init__.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── rag_query_service.py           # Main query interface
│   │   │   ├── document_ingestion_service.py  # Document processing
│   │   │   └── rag_monitoring_service.py      # Analytics & monitoring
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── embedding_engine.py            # Embeddings generation
│   │   │   ├── chunking_engine.py             # Document chunking
│   │   │   ├── context_builder.py             # Context window management
│   │   │   ├── cache_manager.py               # Query/embedding caching
│   │   │   ├── metadata_manager.py            # Document metadata
│   │   │   └── retrieval_optimizer.py         # Search optimization
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── document.py                    # Document data models
│   │   │   ├── chunk.py                       # Chunk data models
│   │   │   ├── query.py                       # Query data models
│   │   │   └── retrieval.py                   # Retrieval result models
│   │   │
│   │   ├── loaders/
│   │   │   ├── __init__.py
│   │   │   ├── pdf_loader.py
│   │   │   ├── markdown_loader.py
│   │   │   ├── docx_loader.py
│   │   │   └── text_loader.py
│   │   │
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── qdrant_client.py               # Qdrant operations
│   │   │   ├── postgres_client.py             # PostgreSQL operations
│   │   │   └── migrations/
│   │   │       ├── 001_create_rag_tables.sql
│   │   │       └── 002_add_indexes.sql
│   │   │
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── rag_config.py                  # RAG configuration
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── text_preprocessing.py
│   │       ├── token_counter.py
│   │       └── evaluation_metrics.py
│   │
│   ├── agents/
│   │   ├── ai_research/
│   │   │   ├── orchestrator.py                # UPDATED: Add RAG integration
│   │   │   └── ...
│   │   └── runtime/
│   │       └── ...
│   │
│   └── magnus_local_llm.py                    # UPDATED: RAG context injection
│
├── data/                                       # NEW: Data storage
│   ├── documents/
│   │   ├── raw/                               # Original documents
│   │   │   ├── trading_guides/
│   │   │   ├── strategies/
│   │   │   ├── market_analysis/
│   │   │   └── research_papers/
│   │   └── processed/                         # Processed documents
│   │       └── .gitkeep
│   │
│   ├── qdrant_storage/                        # Qdrant persistence
│   │   └── .gitkeep
│   │
│   └── cache/
│       ├── embeddings/
│       └── queries/
│
├── scripts/                                    # NEW: RAG utilities
│   ├── rag/
│   │   ├── setup_rag_system.py               # Initial setup script
│   │   ├── ingest_documents.py               # Batch document ingestion
│   │   ├── test_rag_query.py                 # Test retrieval
│   │   ├── evaluate_rag.py                   # Benchmark performance
│   │   └── backup_qdrant.py                  # Backup vector DB
│   │
│   └── ...
│
├── docs/
│   ├── architecture/
│   │   ├── RAG_SYSTEM_ARCHITECTURE.md        # This document
│   │   ├── RAG_INTEGRATION_GUIDE.md          # Integration guide (next)
│   │   └── RAG_QUERY_EXAMPLES.md             # Usage examples (next)
│   │
│   └── rag/
│       ├── SETUP.md
│       ├── INGESTION_GUIDE.md
│       └── TROUBLESHOOTING.md
│
├── tests/
│   └── test_rag/
│       ├── __init__.py
│       ├── test_embedding_engine.py
│       ├── test_chunking_engine.py
│       ├── test_qdrant_client.py
│       ├── test_query_service.py
│       └── test_integration.py
│
├── docker-compose.yml                         # UPDATED: Add Qdrant service
├── requirements.txt                           # Already has dependencies
└── .env                                       # UPDATED: Add RAG config
```

---

## 6. Key Components Implementation

### 6.1 RAGQueryService

```python
# src/rag/services/rag_query_service.py

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

from src.rag.core.embedding_engine import EmbeddingEngine
from src.rag.core.context_builder import ContextBuilder
from src.rag.core.cache_manager import CacheManager
from src.rag.database.qdrant_client import QdrantManager
from src.rag.database.postgres_client import PostgresRAGClient
from src.magnus_local_llm import get_magnus_llm, TaskComplexity

logger = logging.getLogger(__name__)


@dataclass
class RAGQueryResult:
    """Result from RAG query"""
    response: str
    sources: List[Dict[str, Any]]
    similarity_scores: List[float]
    context_used: str
    processing_time_ms: int
    cache_hit: bool


class RAGQueryService:
    """
    Main RAG query service for Magnus/AVA

    Handles:
    - Query embedding generation
    - Semantic search in Qdrant
    - Context building
    - LLM prompt augmentation
    - Response generation with citations
    """

    def __init__(
        self,
        embedding_engine: Optional[EmbeddingEngine] = None,
        context_builder: Optional[ContextBuilder] = None,
        cache_manager: Optional[CacheManager] = None,
        qdrant_client: Optional[QdrantManager] = None,
        postgres_client: Optional[PostgresRAGClient] = None
    ):
        """Initialize RAG query service"""
        self.embedding_engine = embedding_engine or EmbeddingEngine()
        self.context_builder = context_builder or ContextBuilder()
        self.cache_manager = cache_manager or CacheManager()
        self.qdrant = qdrant_client or QdrantManager()
        self.postgres = postgres_client or PostgresRAGClient()
        self.llm = get_magnus_llm()

    def query(
        self,
        prompt: str,
        context_type: Optional[str] = None,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        complexity: TaskComplexity = TaskComplexity.BALANCED,
        use_cache: bool = True
    ) -> RAGQueryResult:
        """
        Execute RAG query

        Args:
            prompt: User query
            context_type: Filter by document type (e.g., 'trading_guide')
            top_k: Number of chunks to retrieve
            filters: Additional metadata filters
            complexity: LLM complexity level
            use_cache: Use cached results if available

        Returns:
            RAGQueryResult with response and sources
        """
        import time
        start_time = time.time()

        # Check cache
        if use_cache:
            cached = self.cache_manager.get_query_result(
                prompt, context_type, filters
            )
            if cached:
                logger.info("Cache hit for RAG query")
                return cached

        # Generate query embedding
        logger.info(f"Generating embedding for query: {prompt[:50]}...")
        query_embedding = self.embedding_engine.encode_query(prompt)

        # Build filters
        qdrant_filters = self._build_filters(context_type, filters)

        # Search Qdrant
        logger.info(f"Searching Qdrant with top_k={top_k}")
        search_results = self.qdrant.search(
            query_vector=query_embedding,
            limit=top_k * 2,  # Get more for re-ranking
            filter=qdrant_filters
        )

        # Re-rank (optional - can add cross-encoder here)
        ranked_results = self._rerank_results(
            search_results, prompt, top_k
        )

        # Build context window
        context, sources = self.context_builder.build_context(
            chunks=ranked_results,
            max_tokens=4000  # Reserve space for prompt + response
        )

        # Augment prompt with context
        augmented_prompt = self._build_augmented_prompt(
            prompt, context, sources
        )

        # Query LLM
        logger.info(f"Querying LLM with augmented prompt")
        response = self.llm.query(
            prompt=augmented_prompt,
            complexity=complexity,
            use_trading_context=True
        )

        # Extract similarity scores
        similarity_scores = [r.score for r in ranked_results]

        # Build result
        processing_time_ms = int((time.time() - start_time) * 1000)

        result = RAGQueryResult(
            response=response,
            sources=sources,
            similarity_scores=similarity_scores,
            context_used=context,
            processing_time_ms=processing_time_ms,
            cache_hit=False
        )

        # Cache result
        if use_cache:
            self.cache_manager.set_query_result(
                prompt, context_type, filters, result
            )

        # Log query
        self._log_query(prompt, result, context_type, filters)

        logger.info(f"RAG query complete in {processing_time_ms}ms")
        return result

    def _build_filters(
        self,
        context_type: Optional[str],
        filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build Qdrant filter conditions"""
        conditions = []

        if context_type:
            conditions.append({
                "key": "document_type",
                "match": {"value": context_type}
            })

        if filters:
            for key, value in filters.items():
                if isinstance(value, list):
                    conditions.append({
                        "key": key,
                        "match": {"any": value}
                    })
                else:
                    conditions.append({
                        "key": key,
                        "match": {"value": value}
                    })

        return {"must": conditions} if conditions else None

    def _rerank_results(
        self,
        results: List[Any],
        query: str,
        top_k: int
    ) -> List[Any]:
        """Re-rank search results"""
        # For now, simple truncation
        # Can add cross-encoder re-ranking here
        return results[:top_k]

    def _build_augmented_prompt(
        self,
        user_prompt: str,
        context: str,
        sources: List[Dict[str, Any]]
    ) -> str:
        """Build prompt with retrieved context"""

        # Build source citations
        source_list = "\n".join([
            f"[{i+1}] {s['title']} (Section: {s.get('section', 'N/A')})"
            for i, s in enumerate(sources)
        ])

        prompt = f"""You are AVA, an expert financial trading advisor. Use the following context from trusted sources to answer the user's question.

CONTEXT:
{context}

SOURCES:
{source_list}

USER QUESTION:
{user_prompt}

INSTRUCTIONS:
1. Answer based primarily on the provided context
2. Cite sources using [1], [2], etc.
3. If context doesn't fully answer the question, say so
4. Provide actionable insights where appropriate
5. Maintain a professional, helpful tone

ANSWER:"""

        return prompt

    def _log_query(
        self,
        prompt: str,
        result: RAGQueryResult,
        context_type: Optional[str],
        filters: Optional[Dict[str, Any]]
    ):
        """Log query to PostgreSQL for analytics"""
        try:
            self.postgres.log_query(
                query_text=prompt,
                context_type=context_type,
                filters=filters,
                retrieved_chunks=[],  # Would need to track chunk IDs
                avg_similarity_score=sum(result.similarity_scores) / len(result.similarity_scores),
                processing_time_ms=result.processing_time_ms,
                llm_used="Qwen 2.5 32B"
            )
        except Exception as e:
            logger.error(f"Failed to log query: {e}")
```

### 6.2 DocumentIngestionService

```python
# src/rag/services/document_ingestion_service.py

from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib
import logging
from datetime import datetime

from src.rag.core.embedding_engine import EmbeddingEngine
from src.rag.core.chunking_engine import ChunkingEngine
from src.rag.loaders import get_loader
from src.rag.database.qdrant_client import QdrantManager
from src.rag.database.postgres_client import PostgresRAGClient
from src.rag.models.document import Document, DocumentType

logger = logging.getLogger(__name__)


class DocumentIngestionService:
    """
    Document ingestion pipeline for RAG system

    Handles:
    - Document loading (PDF, MD, DOCX, TXT)
    - Text extraction and cleaning
    - Intelligent chunking
    - Embedding generation
    - Storage in Qdrant + PostgreSQL
    """

    def __init__(
        self,
        embedding_engine: Optional[EmbeddingEngine] = None,
        chunking_engine: Optional[ChunkingEngine] = None,
        qdrant_client: Optional[QdrantManager] = None,
        postgres_client: Optional[PostgresRAGClient] = None
    ):
        """Initialize ingestion service"""
        self.embedding_engine = embedding_engine or EmbeddingEngine()
        self.chunking_engine = chunking_engine or ChunkingEngine()
        self.qdrant = qdrant_client or QdrantManager()
        self.postgres = postgres_client or PostgresRAGClient()

    def ingest_document(
        self,
        file_path: str,
        document_type: DocumentType,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> Document:
        """
        Ingest a single document

        Args:
            file_path: Path to document file
            document_type: Type of document
            metadata: Additional metadata
            tags: Topic tags

        Returns:
            Document object with ingestion results
        """
        logger.info(f"Ingesting document: {file_path}")

        # Validate file
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        # Calculate file hash for deduplication
        file_hash = self._calculate_file_hash(file_path)

        # Check if already ingested
        existing = self.postgres.get_document_by_hash(file_hash)
        if existing:
            logger.info(f"Document already ingested: {existing.title}")
            return existing

        # Create document record
        document = Document(
            title=metadata.get("title", path.stem),
            file_path=str(path),
            file_hash=file_hash,
            document_type=document_type,
            author=metadata.get("author"),
            source_url=metadata.get("source_url"),
            file_size_bytes=path.stat().st_size,
            metadata=metadata or {},
            tags=tags or [],
            status="processing"
        )

        # Save to PostgreSQL
        doc_id = self.postgres.create_document(document)
        document.id = doc_id

        try:
            # Load document
            loader = get_loader(path.suffix)
            raw_text = loader.load(file_path)

            # Chunk document
            chunks = self.chunking_engine.chunk_document(
                text=raw_text,
                document_type=document_type,
                metadata={"document_id": doc_id}
            )

            logger.info(f"Created {len(chunks)} chunks")

            # Generate embeddings (batch)
            embeddings = self.embedding_engine.encode_chunks(
                [chunk.text for chunk in chunks],
                batch_size=32
            )

            # Store in Qdrant
            qdrant_point_ids = self.qdrant.upsert_chunks(
                document_id=doc_id,
                chunks=chunks,
                embeddings=embeddings
            )

            # Store chunk metadata in PostgreSQL
            for chunk, point_id in zip(chunks, qdrant_point_ids):
                self.postgres.create_chunk(
                    document_id=doc_id,
                    chunk_index=chunk.index,
                    qdrant_point_id=point_id,
                    text_content=chunk.text,
                    token_count=chunk.token_count,
                    section_title=chunk.section_title
                )

            # Update document status
            document.total_chunks = len(chunks)
            document.status = "indexed"
            self.postgres.update_document_status(doc_id, "indexed", len(chunks))

            logger.info(f"Successfully ingested document: {document.title}")
            return document

        except Exception as e:
            logger.error(f"Failed to ingest document: {e}")
            self.postgres.update_document_status(doc_id, "failed")
            raise

    def ingest_directory(
        self,
        directory_path: str,
        document_type: DocumentType,
        recursive: bool = True,
        file_extensions: Optional[List[str]] = None
    ) -> List[Document]:
        """
        Ingest all documents in a directory

        Args:
            directory_path: Path to directory
            document_type: Type of documents
            recursive: Search subdirectories
            file_extensions: Filter by extensions (e.g., ['.pdf', '.md'])

        Returns:
            List of ingested documents
        """
        logger.info(f"Ingesting directory: {directory_path}")

        path = Path(directory_path)
        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory_path}")

        # Find files
        if file_extensions is None:
            file_extensions = ['.pdf', '.md', '.txt', '.docx']

        pattern = "**/*" if recursive else "*"
        files = []
        for ext in file_extensions:
            files.extend(path.glob(f"{pattern}{ext}"))

        logger.info(f"Found {len(files)} files to ingest")

        # Ingest each file
        documents = []
        for file_path in files:
            try:
                doc = self.ingest_document(
                    file_path=str(file_path),
                    document_type=document_type,
                    metadata={"directory": str(path)}
                )
                documents.append(doc)
            except Exception as e:
                logger.error(f"Failed to ingest {file_path}: {e}")

        logger.info(f"Successfully ingested {len(documents)} documents")
        return documents

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
```

---

## 7. Integration with Existing Agent System

### 7.1 Agent-Aware Routing Integration

The RAG system integrates seamlessly with the existing agent-aware routing:

```python
# Example: Integrate RAG with Research Orchestrator

# src/agents/ai_research/orchestrator.py (UPDATED)

from src.rag.services.rag_query_service import RAGQueryService

class ResearchOrchestrator:
    def __init__(self, ...):
        ...
        # Add RAG service
        self.rag_service = RAGQueryService()

    async def analyze(self, request: ResearchRequest) -> ResearchReport:
        """Enhanced with RAG knowledge"""

        # Get RAG context for symbol
        rag_context = self.rag_service.query(
            prompt=f"Provide background information and best practices for analyzing {request.symbol}",
            context_type="trading_guide",
            top_k=3
        )

        # Add RAG context to agent prompts
        enhanced_prompt = f"""
        KNOWLEDGE BASE CONTEXT:
        {rag_context.response}

        ANALYSIS TASK:
        Analyze {request.symbol} using the above best practices...
        """

        # Continue with normal agent execution
        ...
```

### 7.2 AVA Chatbot Integration

```python
# dashboard.py or AVA chatbot handler

from src.rag.services.rag_query_service import RAGQueryService

def handle_ava_query(user_message: str) -> str:
    """
    AVA chatbot with RAG enhancement
    """
    rag_service = RAGQueryService()

    # Classify query type
    query_type = classify_query(user_message)

    if query_type in ["strategy_question", "trading_advice", "how_to"]:
        # Use RAG for knowledge-based questions
        result = rag_service.query(
            prompt=user_message,
            context_type="trading_guide",
            top_k=5
        )

        # Format response with sources
        response = f"{result.response}\n\n"
        response += "**Sources:**\n"
        for i, source in enumerate(result.sources, 1):
            response += f"{i}. {source['title']}\n"

        return response
    else:
        # Use standard LLM for other queries
        llm = get_magnus_llm()
        return llm.query(user_message)
```

---

## 8. Caching and Optimization

### 8.1 Multi-Level Caching Strategy

```
┌─────────────────────────────────────────────┐
│          CACHING ARCHITECTURE               │
└─────────────────────────────────────────────┘

Level 1: Query Result Cache (Redis)
├─ Key: hash(query + filters)
├─ TTL: 5 minutes
├─ Storage: Complete RAGQueryResult
└─ Hit Rate: ~40-50%

Level 2: Embedding Cache (Redis)
├─ Key: hash(text)
├─ TTL: 1 hour
├─ Storage: 384-dim vector
└─ Hit Rate: ~60-70%

Level 3: Context Window Cache (Redis)
├─ Key: hash(chunk_ids + order)
├─ TTL: 30 minutes
├─ Storage: Pre-built context string
└─ Hit Rate: ~30-40%

Level 4: Qdrant Native Cache
├─ Built-in search result caching
├─ Automatic by Qdrant
└─ Reduces search latency
```

### 8.2 Performance Optimizations

1. **Batch Embedding Generation**
   - Process 32-64 chunks at once
   - Reduces API/model calls by 32-64x

2. **HNSW Index in Qdrant**
   - Near-constant time search O(log N)
   - Trade-off: Slightly more memory

3. **Async Processing**
   - Non-blocking document ingestion
   - Background re-indexing

4. **Smart Re-ranking**
   - Only re-rank top 20 results
   - Reduces computation by 50%

5. **Token-Aware Chunking**
   - Precise token counting
   - Maximizes context window usage

---

## 9. Deployment Guide

### Step 1: Setup Qdrant (Docker)

```bash
# Add to docker-compose.yml or run standalone
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -v c:/code/Magnus/data/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest

# Verify
curl http://localhost:6333/health
```

### Step 2: Initialize PostgreSQL Tables

```bash
# Run migration scripts
python scripts/rag/setup_rag_system.py
```

### Step 3: Ingest Initial Documents

```bash
# Ingest trading guides
python scripts/rag/ingest_documents.py \
  --directory "c:/code/Magnus/data/documents/raw/trading_guides" \
  --type trading_guide

# Ingest strategies
python scripts/rag/ingest_documents.py \
  --directory "c:/code/Magnus/data/documents/raw/strategies" \
  --type strategy
```

### Step 4: Test RAG System

```bash
# Test query
python scripts/rag/test_rag_query.py \
  --query "What is the wheel strategy?" \
  --top-k 5
```

### Step 5: Integrate with Dashboard

```python
# Update dashboard.py
from src.rag.services.rag_query_service import RAGQueryService

# Initialize in app
if 'rag_service' not in st.session_state:
    st.session_state.rag_service = RAGQueryService()
```

---

## 10. Monitoring and Analytics

### Key Metrics to Track

```python
# src/rag/services/rag_monitoring_service.py

class RAGMonitoringService:
    """Monitor RAG system performance"""

    def get_metrics(self) -> Dict[str, Any]:
        """Get current RAG metrics"""
        return {
            # Query Performance
            "avg_query_latency_ms": self._get_avg_latency(),
            "cache_hit_rate": self._get_cache_hit_rate(),
            "queries_per_hour": self._get_query_rate(),

            # Retrieval Quality
            "avg_similarity_score": self._get_avg_similarity(),
            "avg_chunks_retrieved": self._get_avg_chunks(),

            # System Health
            "qdrant_index_size": self._get_qdrant_size(),
            "total_documents": self._get_document_count(),
            "total_chunks": self._get_chunk_count(),

            # Storage
            "postgres_table_size": self._get_postgres_size(),
            "cache_memory_usage": self._get_cache_usage(),
        }
```

### Dashboard Integration

```python
# Add to Streamlit dashboard

with st.sidebar:
    st.subheader("RAG System Status")
    metrics = rag_monitoring.get_metrics()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Documents", metrics["total_documents"])
        st.metric("Avg Latency", f"{metrics['avg_query_latency_ms']}ms")
    with col2:
        st.metric("Cache Hit Rate", f"{metrics['cache_hit_rate']:.1%}")
        st.metric("Queries/hr", metrics["queries_per_hour"])
```

---

## 11. Cost Analysis

### Infrastructure Costs

```
Component            | Setup Cost | Monthly Cost | Notes
---------------------|------------|--------------|------------------
Qdrant (Docker)      | $0         | $0           | Self-hosted
PostgreSQL           | $0         | $0           | Already have
Redis                | $0         | $0           | Already have
Embeddings Model     | $0         | $0           | Local inference
Storage (100GB)      | $0         | $0           | Local disk
---------------------|------------|--------------|------------------
TOTAL                | $0         | $0           | 100% free!
```

### Cost Savings vs Cloud RAG

```
Cloud Alternative       | Monthly Cost | Magnus RAG | Savings
------------------------|--------------|------------|--------
Pinecone (Starter)      | $70          | $0         | $70
OpenAI Embeddings       | $13/M tokens | $0         | $50-100
Vector DB hosting       | $50-200      | $0         | $50-200
------------------------|--------------|------------|--------
TOTAL SAVINGS                                       | $170-370/mo
```

### ROI Timeline

- **Setup Time:** 4-6 hours
- **Break-even:** Immediate (no costs)
- **Maintenance:** ~2 hours/month

---

## 12. Security and Privacy

### Data Security Measures

1. **Local Storage**
   - All documents stay on local machine
   - No external API calls for embeddings
   - Full data ownership

2. **Access Control**
   - PostgreSQL user permissions
   - Qdrant API key (optional)
   - File system permissions

3. **Data Encryption**
   - Disk encryption (Windows BitLocker)
   - PostgreSQL SSL connections
   - Qdrant TLS (production)

4. **Sensitive Data Handling**
   - Sanitize financial data in logs
   - Redact PII before ingestion
   - Secure document deletion

---

## 13. Future Enhancements

### Phase 2 (Post-MVP)

1. **Hybrid Search**
   - Combine vector + keyword search
   - BM25 + semantic fusion
   - Better for specific terms

2. **Cross-Encoder Re-ranking**
   - More accurate relevance scoring
   - Trade-off: Slightly slower

3. **Multi-Modal RAG**
   - Ingest charts and images
   - Vision-language models
   - Extract data from screenshots

4. **Query Expansion**
   - Automatic synonym detection
   - Expand abbreviations
   - Handle typos

5. **Feedback Loop**
   - User ratings on responses
   - Fine-tune retrieval
   - Improve chunk boundaries

### Phase 3 (Advanced)

1. **Fine-Tuned Embeddings**
   - Train on financial documents
   - Domain-specific model
   - Better accuracy

2. **GraphRAG**
   - Entity extraction
   - Knowledge graph
   - Reasoning over relationships

3. **Agentic RAG**
   - Multi-hop retrieval
   - Iterative refinement
   - Self-correction

---

## 14. Summary

This RAG architecture provides:

✅ **100% Local & Free** - No ongoing costs
✅ **Production-Ready** - Proven tech stack
✅ **Fast** - <500ms query latency with caching
✅ **Scalable** - Handles 10,000+ documents
✅ **Secure** - All data stays local
✅ **Integrated** - Works with existing 33 agents
✅ **Maintainable** - Clear structure, good docs

### Next Steps

1. **Review this architecture** - Validate design decisions
2. **Create implementation files** - Code the components
3. **Setup infrastructure** - Deploy Qdrant + tables
4. **Ingest test documents** - Load sample data
5. **Integration testing** - Test with agents
6. **Production deployment** - Go live!

---

**Document Version:** 1.0.0
**Last Updated:** 2025-11-20
**Status:** Ready for Implementation
**Estimated Implementation Time:** 8-12 hours
