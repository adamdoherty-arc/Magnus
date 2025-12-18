# Magnus/AVA RAG Integration Guide
## Step-by-Step Implementation and Integration

**Version:** 1.0.0
**Date:** 2025-11-20
**Prerequisites:** RAG_SYSTEM_ARCHITECTURE.md reviewed
**Estimated Time:** 8-12 hours

---

## Table of Contents

1. [Quick Start (30 minutes)](#1-quick-start)
2. [Infrastructure Setup (1 hour)](#2-infrastructure-setup)
3. [Core Components Implementation (4-6 hours)](#3-core-components-implementation)
4. [Agent Integration (2-3 hours)](#4-agent-integration)
5. [Testing and Validation (1-2 hours)](#5-testing-and-validation)
6. [Production Deployment](#6-production-deployment)

---

## 1. Quick Start (30 minutes)

### 1.1 Install Dependencies

All required packages are already in `requirements.txt`:

```bash
# Verify installations
python -c "from sentence_transformers import SentenceTransformer; print('✓ sentence-transformers')"
python -c "from qdrant_client import QdrantClient; print('✓ qdrant-client')"
python -c "from langchain.text_splitter import RecursiveCharacterTextSplitter; print('✓ langchain')"
```

If missing:
```bash
pip install sentence-transformers==3.0.0 qdrant-client==1.7.0
```

### 1.2 Start Qdrant

**Option A: Docker (Recommended)**
```bash
docker run -d \
  --name qdrant-magnus \
  -p 6333:6333 \
  -p 6334:6334 \
  -v c:/code/Magnus/data/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest

# Verify
curl http://localhost:6333/health
```

**Option B: Windows Binary**
```bash
# Download from https://github.com/qdrant/qdrant/releases
# Extract and run
qdrant.exe --config-path config.yaml
```

### 1.3 Initialize Database

```bash
# Create RAG tables in PostgreSQL
python scripts/rag/setup_rag_system.py
```

Expected output:
```
✓ Created rag_documents table
✓ Created rag_chunks table
✓ Created rag_query_logs table
✓ Created rag_embeddings_cache table
✓ Created indexes
✓ Initialized Qdrant collection: magnus_kb
```

### 1.4 Quick Test

```bash
# Ingest a test document
python scripts/rag/test_ingest.py

# Test query
python scripts/rag/test_query.py --query "What is the wheel strategy?"
```

Expected output:
```
Query: What is the wheel strategy?
Retrieved 5 chunks in 234ms
Response: The Wheel Strategy is an options trading strategy...
Sources:
  [1] Options Trading Guide - Section: Wheel Strategy
  [2] Advanced Strategies - Section: Income Generation
```

---

## 2. Infrastructure Setup (1 hour)

### 2.1 Update docker-compose.yml

```yaml
# c:/code/Magnus/docker-compose.yml

version: '3.8'

services:
  # ... existing services ...

  qdrant:
    image: qdrant/qdrant:latest
    container_name: magnus-qdrant
    ports:
      - "6333:6333"  # HTTP API
      - "6334:6334"  # gRPC
    volumes:
      - ./data/qdrant_storage:/qdrant/storage
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
      - QDRANT__LOG_LEVEL=INFO
    restart: unless-stopped
    networks:
      - magnus-network

networks:
  magnus-network:
    driver: bridge
```

Start all services:
```bash
docker-compose up -d qdrant
```

### 2.2 Update .env Configuration

```bash
# c:/code/Magnus/.env

# ... existing config ...

# RAG Configuration
RAG_ENABLED=true
RAG_QDRANT_HOST=localhost
RAG_QDRANT_PORT=6333
RAG_QDRANT_COLLECTION=magnus_kb
RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
RAG_EMBEDDING_DIMENSION=384
RAG_CHUNK_SIZE=512
RAG_CHUNK_OVERLAP=50
RAG_TOP_K_DEFAULT=5
RAG_CACHE_TTL_SECONDS=300
RAG_MAX_CONTEXT_TOKENS=4000
```

### 2.3 Create Directory Structure

```bash
# Run setup script
python scripts/rag/create_directories.py
```

Or manually:
```bash
mkdir -p data/documents/raw/trading_guides
mkdir -p data/documents/raw/strategies
mkdir -p data/documents/raw/market_analysis
mkdir -p data/documents/raw/research_papers
mkdir -p data/documents/processed
mkdir -p data/qdrant_storage
mkdir -p data/cache/embeddings
mkdir -p data/cache/queries
```

### 2.4 Initialize PostgreSQL Tables

```sql
-- c:/code/Magnus/src/rag/database/migrations/001_create_rag_tables.sql

-- Documents table
CREATE TABLE IF NOT EXISTS rag_documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    file_path TEXT NOT NULL,
    file_hash VARCHAR(64) UNIQUE NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    author VARCHAR(200),
    source_url TEXT,
    upload_date TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW(),
    file_size_bytes INTEGER,
    total_chunks INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'processing',
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_rag_documents_type ON rag_documents(document_type);
CREATE INDEX idx_rag_documents_status ON rag_documents(status);
CREATE INDEX idx_rag_documents_tags ON rag_documents USING GIN(tags);
CREATE INDEX idx_rag_documents_hash ON rag_documents(file_hash);

-- Chunks table
CREATE TABLE IF NOT EXISTS rag_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES rag_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    qdrant_point_id UUID NOT NULL,
    text_content TEXT NOT NULL,
    token_count INTEGER,
    section_title VARCHAR(500),
    embedding_model VARCHAR(100) DEFAULT 'all-MiniLM-L6-v2',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (document_id, chunk_index)
);

CREATE INDEX idx_rag_chunks_document ON rag_chunks(document_id);
CREATE INDEX idx_rag_chunks_qdrant ON rag_chunks(qdrant_point_id);

-- Query logs table
CREATE TABLE IF NOT EXISTS rag_query_logs (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    query_hash VARCHAR(64),
    context_type VARCHAR(50),
    top_k INTEGER,
    filters JSONB DEFAULT '{}',
    retrieved_chunk_ids INTEGER[],
    avg_similarity_score FLOAT,
    processing_time_ms INTEGER,
    llm_used VARCHAR(50),
    cache_hit BOOLEAN DEFAULT false,
    response_quality_rating INTEGER,
    user_agent VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_rag_query_logs_created ON rag_query_logs(created_at);
CREATE INDEX idx_rag_query_logs_type ON rag_query_logs(context_type);
CREATE INDEX idx_rag_query_logs_hash ON rag_query_logs(query_hash);

-- Embeddings cache table (optional optimization)
CREATE TABLE IF NOT EXISTS rag_embeddings_cache (
    id SERIAL PRIMARY KEY,
    text_hash VARCHAR(64) UNIQUE NOT NULL,
    embedding_vector FLOAT[] NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_accessed TIMESTAMP DEFAULT NOW(),
    access_count INTEGER DEFAULT 1
);

CREATE INDEX idx_rag_embeddings_hash ON rag_embeddings_cache(text_hash);
CREATE INDEX idx_rag_embeddings_model ON rag_embeddings_cache(model_name);

-- Update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_rag_documents_updated_at
BEFORE UPDATE ON rag_documents
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

Run migration:
```bash
psql -U postgres -d magnus -f src/rag/database/migrations/001_create_rag_tables.sql
```

---

## 3. Core Components Implementation (4-6 hours)

### 3.1 Configuration Module

```python
# src/rag/config/rag_config.py

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class RAGConfig(BaseSettings):
    """RAG System Configuration"""

    # Qdrant Configuration
    qdrant_host: str = Field(default="localhost", env="RAG_QDRANT_HOST")
    qdrant_port: int = Field(default=6333, env="RAG_QDRANT_PORT")
    qdrant_collection: str = Field(default="magnus_kb", env="RAG_QDRANT_COLLECTION")
    qdrant_use_grpc: bool = Field(default=False, env="RAG_QDRANT_USE_GRPC")

    # Embedding Configuration
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        env="RAG_EMBEDDING_MODEL"
    )
    embedding_dimension: int = Field(default=384, env="RAG_EMBEDDING_DIMENSION")
    embedding_batch_size: int = Field(default=32, env="RAG_EMBEDDING_BATCH_SIZE")
    embedding_device: str = Field(default="cpu", env="RAG_EMBEDDING_DEVICE")

    # Chunking Configuration
    chunk_size: int = Field(default=512, env="RAG_CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, env="RAG_CHUNK_OVERLAP")
    min_chunk_size: int = Field(default=100, env="RAG_MIN_CHUNK_SIZE")

    # Retrieval Configuration
    top_k_default: int = Field(default=5, env="RAG_TOP_K_DEFAULT")
    top_k_max: int = Field(default=20, env="RAG_TOP_K_MAX")
    similarity_threshold: float = Field(default=0.3, env="RAG_SIMILARITY_THRESHOLD")

    # Context Configuration
    max_context_tokens: int = Field(default=4000, env="RAG_MAX_CONTEXT_TOKENS")
    include_metadata: bool = Field(default=True, env="RAG_INCLUDE_METADATA")

    # Cache Configuration
    cache_enabled: bool = Field(default=True, env="RAG_CACHE_ENABLED")
    cache_ttl_seconds: int = Field(default=300, env="RAG_CACHE_TTL_SECONDS")
    embedding_cache_ttl_seconds: int = Field(default=3600, env="RAG_EMBEDDING_CACHE_TTL")

    # PostgreSQL Configuration (inherit from main config)
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_db: str = Field(default="magnus", env="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(default="", env="POSTGRES_PASSWORD")

    # Redis Configuration (if available)
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=1, env="RAG_REDIS_DB")

    # Storage Paths
    documents_path: str = Field(default="c:/code/Magnus/data/documents", env="RAG_DOCUMENTS_PATH")
    cache_path: str = Field(default="c:/code/Magnus/data/cache", env="RAG_CACHE_PATH")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global config instance
_rag_config: Optional[RAGConfig] = None


def get_rag_config() -> RAGConfig:
    """Get global RAG configuration"""
    global _rag_config
    if _rag_config is None:
        _rag_config = RAGConfig()
    return _rag_config
```

### 3.2 Embedding Engine

```python
# src/rag/core/embedding_engine.py

import logging
from typing import List, Union, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import hashlib
import pickle
from pathlib import Path

from src.rag.config.rag_config import get_rag_config

logger = logging.getLogger(__name__)


class EmbeddingEngine:
    """
    Embedding generation engine using sentence-transformers

    Features:
    - Batch processing for efficiency
    - Caching for repeated texts
    - CPU/GPU support
    - Normalization for cosine similarity
    """

    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        """
        Initialize embedding engine

        Args:
            model_name: Model to use (default from config)
            device: Device to use ('cpu', 'cuda', 'mps')
        """
        self.config = get_rag_config()
        self.model_name = model_name or self.config.embedding_model
        self.device = device or self.config.embedding_device

        logger.info(f"Loading embedding model: {self.model_name} on {self.device}")
        self.model = SentenceTransformer(self.model_name, device=self.device)

        # Initialize cache
        self.cache_enabled = self.config.cache_enabled
        self.cache_dir = Path(self.config.cache_path) / "embeddings"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Embedding engine initialized (dim={self.config.embedding_dimension})")

    def encode_query(self, query: str, normalize: bool = True) -> np.ndarray:
        """
        Encode a single query

        Args:
            query: Query text
            normalize: Normalize for cosine similarity

        Returns:
            Embedding vector
        """
        # Check cache
        if self.cache_enabled:
            cached = self._get_cached_embedding(query)
            if cached is not None:
                logger.debug("Cache hit for query embedding")
                return cached

        # Encode
        embedding = self.model.encode(
            query,
            normalize_embeddings=normalize,
            show_progress_bar=False
        )

        # Cache
        if self.cache_enabled:
            self._cache_embedding(query, embedding)

        return embedding

    def encode_chunks(
        self,
        texts: List[str],
        batch_size: Optional[int] = None,
        normalize: bool = True,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Encode multiple text chunks

        Args:
            texts: List of text chunks
            batch_size: Batch size (default from config)
            normalize: Normalize embeddings
            show_progress: Show progress bar

        Returns:
            Array of embeddings
        """
        batch_size = batch_size or self.config.embedding_batch_size

        logger.info(f"Encoding {len(texts)} chunks in batches of {batch_size}")

        # Check cache for all texts
        if self.cache_enabled:
            embeddings = []
            uncached_texts = []
            uncached_indices = []

            for i, text in enumerate(texts):
                cached = self._get_cached_embedding(text)
                if cached is not None:
                    embeddings.append(cached)
                else:
                    embeddings.append(None)
                    uncached_texts.append(text)
                    uncached_indices.append(i)

            # Encode uncached texts
            if uncached_texts:
                logger.info(f"Cache miss for {len(uncached_texts)} chunks, encoding...")
                new_embeddings = self.model.encode(
                    uncached_texts,
                    batch_size=batch_size,
                    normalize_embeddings=normalize,
                    show_progress_bar=show_progress
                )

                # Insert new embeddings and cache
                for idx, embedding in zip(uncached_indices, new_embeddings):
                    embeddings[idx] = embedding
                    self._cache_embedding(texts[idx], embedding)

                logger.info(f"Cache hit rate: {(len(texts) - len(uncached_texts)) / len(texts) * 100:.1f}%")

            return np.array(embeddings)

        else:
            # No caching, encode all
            return self.model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=normalize,
                show_progress_bar=show_progress
            )

    def _get_cached_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get cached embedding if available"""
        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cached embedding: {e}")
                return None

        return None

    def _cache_embedding(self, text: str, embedding: np.ndarray):
        """Cache embedding to disk"""
        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(embedding, f)
        except Exception as e:
            logger.warning(f"Failed to cache embedding: {e}")

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        text_normalized = text.strip().lower()
        return hashlib.md5(f"{self.model_name}:{text_normalized}".encode()).hexdigest()

    def get_embedding_dimension(self) -> int:
        """Get embedding dimension"""
        return self.model.get_sentence_embedding_dimension()
```

### 3.3 Qdrant Client

```python
# src/rag/database/qdrant_client.py

import logging
from typing import List, Dict, Any, Optional
from uuid import uuid4
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    MatchAny,
    SearchRequest
)

from src.rag.config.rag_config import get_rag_config

logger = logging.getLogger(__name__)


class QdrantManager:
    """
    Qdrant vector database manager

    Features:
    - Collection management
    - Vector CRUD operations
    - Semantic search
    - Metadata filtering
    """

    def __init__(self):
        """Initialize Qdrant client"""
        self.config = get_rag_config()

        if self.config.qdrant_use_grpc:
            self.client = QdrantClient(
                host=self.config.qdrant_host,
                grpc_port=self.config.qdrant_port,
                prefer_grpc=True
            )
        else:
            self.client = QdrantClient(
                host=self.config.qdrant_host,
                port=self.config.qdrant_port
            )

        self.collection_name = self.config.qdrant_collection

        logger.info(f"Connected to Qdrant at {self.config.qdrant_host}:{self.config.qdrant_port}")

        # Ensure collection exists
        self._ensure_collection()

    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name not in collection_names:
            logger.info(f"Creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.config.embedding_dimension,
                    distance=Distance.COSINE
                )
            )
            logger.info("Collection created successfully")
        else:
            logger.info(f"Collection exists: {self.collection_name}")

    def upsert_chunks(
        self,
        document_id: int,
        chunks: List[Any],
        embeddings: np.ndarray
    ) -> List[str]:
        """
        Insert or update document chunks

        Args:
            document_id: Document ID from PostgreSQL
            chunks: List of chunk objects
            embeddings: Array of embeddings

        Returns:
            List of Qdrant point IDs
        """
        points = []
        point_ids = []

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = str(uuid4())
            point_ids.append(point_id)

            payload = {
                "document_id": document_id,
                "chunk_id": chunk.id if hasattr(chunk, 'id') else i,
                "text": chunk.text,
                "document_title": chunk.metadata.get("document_title", ""),
                "document_type": chunk.metadata.get("document_type", ""),
                "topic_tags": chunk.metadata.get("topic_tags", []),
                "section": chunk.metadata.get("section", ""),
                "token_count": chunk.token_count if hasattr(chunk, 'token_count') else 0,
                "created_at": chunk.metadata.get("created_at", "")
            }

            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding.tolist(),
                    payload=payload
                )
            )

        # Batch upsert
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        logger.info(f"Upserted {len(points)} points for document {document_id}")
        return point_ids

    def search(
        self,
        query_vector: np.ndarray,
        limit: int = 10,
        filter: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> List[Any]:
        """
        Semantic search in Qdrant

        Args:
            query_vector: Query embedding
            limit: Number of results
            filter: Metadata filters
            score_threshold: Minimum similarity score

        Returns:
            List of search results
        """
        # Build filter
        qdrant_filter = self._build_filter(filter) if filter else None

        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector.tolist(),
            limit=limit,
            query_filter=qdrant_filter,
            score_threshold=score_threshold or self.config.similarity_threshold
        )

        logger.info(f"Found {len(results)} results")
        return results

    def _build_filter(self, filter_dict: Dict[str, Any]) -> Filter:
        """Build Qdrant filter from dict"""
        conditions = []

        for key, value in filter_dict.items():
            if "must" in filter_dict:
                # Already formatted
                return Filter(**filter_dict)

            if isinstance(value, list):
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchAny(any=value)
                    )
                )
            else:
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )

        return Filter(must=conditions) if conditions else None

    def delete_document(self, document_id: int):
        """Delete all chunks for a document"""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector={
                "filter": {
                    "must": [
                        {
                            "key": "document_id",
                            "match": {"value": document_id}
                        }
                    ]
                }
            }
        )
        logger.info(f"Deleted chunks for document {document_id}")

    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection statistics"""
        info = self.client.get_collection(self.collection_name)
        return {
            "name": info.config.name,
            "vectors_count": info.vectors_count,
            "indexed_vectors_count": info.indexed_vectors_count,
            "points_count": info.points_count,
            "status": info.status
        }
```

---

## 4. Agent Integration (2-3 hours)

### 4.1 Update Research Orchestrator

```python
# src/agents/ai_research/orchestrator.py (ADDITIONS)

from src.rag.services.rag_query_service import RAGQueryService

class ResearchOrchestrator:
    def __init__(self, ...):
        # ... existing init ...

        # Add RAG service
        self.rag_service = RAGQueryService()
        logger.info("RAG service initialized for research orchestrator")

    async def analyze(self, request: ResearchRequest) -> ResearchReport:
        """Enhanced analysis with RAG knowledge"""

        # Get RAG context before running agents
        try:
            rag_context = await self._get_rag_context(request.symbol)
        except Exception as e:
            logger.warning(f"RAG context retrieval failed: {e}")
            rag_context = None

        # Continue with existing agent execution
        # ...

        # If RAG context available, enhance synthesis
        if rag_context:
            synthesis = await self._synthesize_with_crew_and_rag(
                symbol, agent_results, rag_context, request.user_position
            )
        else:
            synthesis = await self._synthesize_with_crew(
                symbol, agent_results, request.user_position
            )

        # ... rest of existing code ...

    async def _get_rag_context(self, symbol: str) -> Optional[str]:
        """Get relevant RAG context for symbol analysis"""
        try:
            # Query for trading strategies
            strategy_result = self.rag_service.query(
                prompt=f"What are the best practices for analyzing and trading {symbol}?",
                context_type="trading_guide",
                top_k=3,
                use_cache=True
            )

            # Query for symbol-specific info
            symbol_result = self.rag_service.query(
                prompt=f"What is important to know about {symbol} for trading decisions?",
                context_type="market_analysis",
                top_k=2,
                use_cache=True
            )

            # Combine contexts
            combined = f"""
TRADING BEST PRACTICES:
{strategy_result.response}

SYMBOL-SPECIFIC KNOWLEDGE:
{symbol_result.response}
"""
            return combined

        except Exception as e:
            logger.error(f"Failed to get RAG context: {e}")
            return None
```

### 4.2 Update MagnusLocalLLM

```python
# src/magnus_local_llm.py (ADDITIONS)

from typing import Optional
from src.rag.services.rag_query_service import RAGQueryService

class MagnusLocalLLM:
    def __init__(self, ...):
        # ... existing init ...

        # Initialize RAG service (optional)
        self.rag_enabled = os.getenv("RAG_ENABLED", "false").lower() == "true"
        if self.rag_enabled:
            try:
                self.rag_service = RAGQueryService()
                logger.info("RAG service enabled for LLM queries")
            except Exception as e:
                logger.warning(f"RAG service unavailable: {e}")
                self.rag_enabled = False
                self.rag_service = None

    def query(
        self,
        prompt: str,
        complexity: Optional[TaskComplexity] = None,
        system_prompt: Optional[str] = None,
        use_trading_context: bool = True,
        max_tokens: int = 4000,
        stream: bool = False,
        use_rag: bool = True  # NEW PARAMETER
    ) -> str:
        """Query with optional RAG enhancement"""

        # Get RAG context if enabled
        rag_context = None
        if use_rag and self.rag_enabled and self.rag_service:
            try:
                rag_result = self.rag_service.query(
                    prompt=prompt,
                    top_k=5,
                    complexity=complexity or TaskComplexity.BALANCED
                )
                rag_context = rag_result.context_used
                logger.info("RAG context added to prompt")
            except Exception as e:
                logger.warning(f"RAG enhancement failed: {e}")

        # Build prompt with RAG context
        if rag_context:
            full_prompt = f"""
KNOWLEDGE BASE CONTEXT:
{rag_context}

USER QUERY:
{prompt}

Answer based on the knowledge base context above, combined with your general knowledge.
"""
        else:
            full_prompt = prompt

        # Continue with existing query logic
        return super().query(
            prompt=full_prompt,
            complexity=complexity,
            system_prompt=system_prompt,
            use_trading_context=use_trading_context,
            max_tokens=max_tokens,
            stream=stream
        )
```

### 4.3 Dashboard Integration

```python
# dashboard.py (ADDITIONS)

import streamlit as st
from src.rag.services.rag_query_service import RAGQueryService
from src.rag.services.document_ingestion_service import DocumentIngestionService

# Initialize RAG services
@st.cache_resource
def get_rag_services():
    """Initialize RAG services (cached)"""
    try:
        query_service = RAGQueryService()
        ingestion_service = DocumentIngestionService()
        return query_service, ingestion_service
    except Exception as e:
        st.error(f"Failed to initialize RAG services: {e}")
        return None, None

# Add RAG management page
def show_rag_management_page():
    """RAG system management interface"""
    st.title("Knowledge Base Management")

    query_service, ingestion_service = get_rag_services()

    if not query_service:
        st.warning("RAG system not available")
        return

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📚 Documents", "🔍 Search", "📊 Analytics"])

    with tab1:
        show_document_management(ingestion_service)

    with tab2:
        show_rag_search(query_service)

    with tab3:
        show_rag_analytics(query_service)

# Add to main navigation
pages = {
    "Trading": [...],
    "Knowledge Base": [
        st.Page(show_rag_management_page, title="Knowledge Base", icon="🧠")
    ]
}
```

---

## 5. Testing and Validation (1-2 hours)

### 5.1 Unit Tests

```bash
# Run all RAG tests
pytest tests/test_rag/ -v

# Run specific test
pytest tests/test_rag/test_embedding_engine.py -v
```

### 5.2 Integration Tests

```bash
# Test end-to-end workflow
python scripts/rag/test_integration.py
```

### 5.3 Performance Benchmarks

```bash
# Benchmark RAG performance
python scripts/rag/evaluate_rag.py --num-queries 100
```

Expected output:
```
RAG Performance Benchmark
==========================
Queries: 100
Total time: 23.4s
Avg query time: 234ms
Cache hit rate: 45%
Avg similarity score: 0.82
Top-5 accuracy: 92%
```

---

## 6. Production Deployment

### 6.1 Pre-Deployment Checklist

```markdown
- [ ] Qdrant running and accessible
- [ ] PostgreSQL tables created
- [ ] Environment variables configured
- [ ] Test documents ingested
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Performance benchmarks acceptable
- [ ] Monitoring dashboard configured
- [ ] Backup strategy defined
```

### 6.2 Startup Script

```bash
# scripts/start_rag_system.sh

#!/bin/bash

echo "Starting Magnus RAG System..."

# Start Qdrant
docker-compose up -d qdrant

# Wait for Qdrant
sleep 5

# Verify Qdrant
curl -s http://localhost:6333/health || {
    echo "ERROR: Qdrant not responding"
    exit 1
}

# Verify PostgreSQL tables
python scripts/rag/verify_tables.py || {
    echo "ERROR: PostgreSQL tables missing"
    exit 1
}

echo "✓ RAG system ready"
```

### 6.3 Monitoring

```python
# Add to dashboard sidebar

with st.sidebar:
    st.markdown("---")
    st.subheader("RAG System Status")

    try:
        from src.rag.services.rag_monitoring_service import RAGMonitoringService
        monitor = RAGMonitoringService()
        metrics = monitor.get_metrics()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Documents", metrics["total_documents"])
            st.metric("Queries/hr", metrics["queries_per_hour"])
        with col2:
            st.metric("Avg Latency", f"{metrics['avg_query_latency_ms']}ms")
            st.metric("Cache Hit %", f"{metrics['cache_hit_rate']:.1%}")

        # Health indicator
        health_status = "🟢 Healthy" if metrics["system_healthy"] else "🔴 Issues"
        st.text(health_status)

    except Exception as e:
        st.error("RAG monitoring unavailable")
```

---

## Summary

You now have a complete integration guide for the RAG system. The implementation is:

✅ **Modular** - Each component can be tested independently
✅ **Scalable** - Handles growing document corpus
✅ **Observable** - Built-in monitoring and logging
✅ **Integrated** - Works seamlessly with existing agents
✅ **Production-Ready** - Error handling, caching, optimization

### Next Steps

1. Follow Quick Start to verify infrastructure
2. Implement core components in order
3. Test each component before integration
4. Deploy to production environment
5. Monitor and optimize based on metrics

**Estimated Total Implementation Time:** 8-12 hours for complete system

---

**Document Version:** 1.0.0
**Last Updated:** 2025-11-20
**Status:** Ready for Implementation
