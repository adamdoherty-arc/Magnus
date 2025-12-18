# Magnus RAG System - Quick Reference Card

**Version:** 1.0.0 | **Date:** 2025-11-20

---

## Quick Start Commands

```bash
# 1. Start Qdrant
docker-compose up -d qdrant

# 2. Initialize database
python scripts/rag/setup_rag_system.py

# 3. Ingest documents
python scripts/rag/ingest_documents.py --directory data/documents/raw/trading_guides

# 4. Test query
python scripts/rag/test_query.py --query "What is the wheel strategy?"

# 5. Start dashboard
streamlit run dashboard.py
```

---

## Common Code Patterns

### Pattern 1: Query Knowledge Base

```python
from src.rag.services.rag_query_service import RAGQueryService

rag = RAGQueryService()

result = rag.query(
    prompt="Your question here",
    context_type="trading_guide",  # Optional filter
    top_k=5,                       # Number of chunks
    use_cache=True                 # Default: True
)

print(result.response)
print(f"Sources: {result.sources}")
print(f"Time: {result.processing_time_ms}ms")
```

### Pattern 2: Ingest Documents

```python
from src.rag.services.document_ingestion_service import DocumentIngestionService

ingestion = DocumentIngestionService()

# Single document
doc = ingestion.ingest_document(
    file_path="path/to/document.pdf",
    document_type="trading_guide",
    metadata={"author": "Name", "version": "1.0"},
    tags=["options", "strategy"]
)

# Entire directory
docs = ingestion.ingest_directory(
    directory_path="data/documents/raw/strategies",
    document_type="strategy",
    recursive=True
)
```

### Pattern 3: Agent Integration

```python
# In your agent code
from src.rag.services.rag_query_service import RAGQueryService

class YourAgent:
    def __init__(self):
        self.rag = RAGQueryService()

    async def analyze(self, symbol: str):
        # Get RAG context
        context = self.rag.query(
            prompt=f"Background on {symbol}",
            context_type="market_analysis",
            top_k=3
        )

        # Use context in your analysis
        enhanced_prompt = f"""
        Context: {context.response}

        Now analyze {symbol}...
        """

        # Continue with your logic
        ...
```

### Pattern 4: Dashboard Widget

```python
import streamlit as st
from src.rag.services.rag_query_service import RAGQueryService

st.subheader("Ask AVA")

query = st.text_input("Your question:")

if query:
    with st.spinner("Thinking..."):
        rag = RAGQueryService()
        result = rag.query(query, top_k=5)

    st.success(result.response)

    with st.expander("Sources"):
        for i, src in enumerate(result.sources, 1):
            st.write(f"{i}. {src['title']} - {src['section']}")
```

---

## Configuration Reference

### Environment Variables (.env)

```bash
# RAG System
RAG_ENABLED=true
RAG_QDRANT_HOST=localhost
RAG_QDRANT_PORT=6333
RAG_QDRANT_COLLECTION=magnus_kb
RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
RAG_CHUNK_SIZE=512
RAG_CHUNK_OVERLAP=50
RAG_TOP_K_DEFAULT=5
RAG_CACHE_TTL_SECONDS=300
```

### RAGConfig Object

```python
from src.rag.config.rag_config import get_rag_config

config = get_rag_config()

# Access settings
print(config.qdrant_host)
print(config.embedding_model)
print(config.chunk_size)
```

---

## Database Quick Reference

### PostgreSQL Tables

```sql
-- View all documents
SELECT id, title, document_type, total_chunks, status
FROM rag_documents
ORDER BY upload_date DESC;

-- View recent queries
SELECT query_text, processing_time_ms, cache_hit
FROM rag_query_logs
ORDER BY created_at DESC
LIMIT 10;

-- Document statistics
SELECT
    document_type,
    COUNT(*) as doc_count,
    SUM(total_chunks) as total_chunks
FROM rag_documents
WHERE status = 'indexed'
GROUP BY document_type;
```

### Qdrant Operations

```python
from src.rag.database.qdrant_client import QdrantManager

qdrant = QdrantManager()

# Collection info
info = qdrant.get_collection_info()
print(f"Vectors: {info['vectors_count']}")

# Search
results = qdrant.search(
    query_vector=embedding,
    limit=10,
    filter={"document_type": "trading_guide"}
)

# Delete document
qdrant.delete_document(document_id=123)
```

---

## API Reference

### RAGQueryService

```python
class RAGQueryService:
    def query(
        self,
        prompt: str,              # User query
        context_type: str = None, # Filter by doc type
        top_k: int = 5,           # Results to retrieve
        filters: dict = None,     # Additional filters
        complexity: TaskComplexity = BALANCED,
        use_cache: bool = True
    ) -> RAGQueryResult
```

**Returns:**
```python
RAGQueryResult(
    response: str,                    # Generated response
    sources: List[Dict],              # Source documents
    similarity_scores: List[float],   # Relevance scores
    context_used: str,                # Retrieved context
    processing_time_ms: int,          # Latency
    cache_hit: bool                   # Was cached?
)
```

### DocumentIngestionService

```python
class DocumentIngestionService:
    def ingest_document(
        self,
        file_path: str,           # Path to file
        document_type: str,       # Category
        metadata: dict = None,    # Additional metadata
        tags: list = None         # Topic tags
    ) -> Document

    def ingest_directory(
        self,
        directory_path: str,
        document_type: str,
        recursive: bool = True,
        file_extensions: list = None
    ) -> List[Document]
```

---

## Document Types

```python
# Standard document types
DOCUMENT_TYPES = [
    "trading_guide",      # Trading strategies, how-tos
    "strategy",           # Specific strategy docs
    "market_analysis",    # Market research, analysis
    "research_paper",     # Academic/research papers
    "faq",               # FAQs, Q&A documents
    "policy",            # Trading policies, rules
    "glossary",          # Term definitions
]
```

---

## Monitoring Queries

```python
from src.rag.services.rag_monitoring_service import RAGMonitoringService

monitor = RAGMonitoringService()
metrics = monitor.get_metrics()

# Key metrics
print(f"Avg Latency: {metrics['avg_query_latency_ms']}ms")
print(f"Cache Hit Rate: {metrics['cache_hit_rate']:.1%}")
print(f"Documents: {metrics['total_documents']}")
print(f"Queries/hr: {metrics['queries_per_hour']}")
```

---

## Troubleshooting

### Issue: Qdrant not responding

```bash
# Check if running
docker ps | grep qdrant

# Restart
docker-compose restart qdrant

# Check logs
docker logs magnus-qdrant

# Test connection
curl http://localhost:6333/health
```

### Issue: Slow queries

```python
# Check cache hit rate
from src.rag.services.rag_query_service import RAGQueryService
rag = RAGQueryService()
metrics = rag.get_metrics()
print(f"Cache hit rate: {metrics['cache_hit_rate']}")

# If low, increase TTL in .env
RAG_CACHE_TTL_SECONDS=600  # 10 minutes
```

### Issue: Poor results

```python
# Adjust retrieval parameters
result = rag.query(
    prompt=query,
    top_k=10,  # Retrieve more chunks
    similarity_threshold=0.5  # Lower threshold
)

# Or re-chunk documents with smaller chunks
RAG_CHUNK_SIZE=256  # Smaller chunks
RAG_CHUNK_OVERLAP=100  # More overlap
```

### Issue: Out of memory (embeddings)

```python
# Use smaller batch size
from src.rag.core.embedding_engine import EmbeddingEngine

engine = EmbeddingEngine()
embeddings = engine.encode_chunks(
    texts=chunks,
    batch_size=16  # Default 32, reduce to 16
)
```

---

## Performance Optimization Tips

### 1. Enable All Caching

```python
# In .env
RAG_CACHE_ENABLED=true
RAG_CACHE_TTL_SECONDS=600
RAG_EMBEDDING_CACHE_TTL=3600
```

### 2. Optimize Chunk Size

```python
# Smaller chunks = more precise, slower
RAG_CHUNK_SIZE=256

# Larger chunks = more context, faster
RAG_CHUNK_SIZE=1024
```

### 3. Use Metadata Filters

```python
# Faster: Filter by document type
result = rag.query(
    prompt=query,
    context_type="trading_guide"  # Limits search space
)
```

### 4. Batch Operations

```python
# Ingest multiple documents at once
docs = ingestion.ingest_directory("data/documents")

# Generate embeddings in batches
embeddings = engine.encode_chunks(texts, batch_size=32)
```

---

## Testing Commands

```bash
# Run all tests
pytest tests/test_rag/ -v

# Run specific test file
pytest tests/test_rag/test_embedding_engine.py -v

# Run with coverage
pytest tests/test_rag/ --cov=src.rag --cov-report=html

# Benchmark performance
python scripts/rag/evaluate_rag.py --num-queries 100
```

---

## Backup and Maintenance

### Backup Qdrant

```bash
# Create snapshot
curl -X POST http://localhost:6333/collections/magnus_kb/snapshots

# Download snapshot
# Check Qdrant docs for snapshot download
```

### Backup PostgreSQL

```bash
# Export RAG tables
pg_dump -U postgres -d magnus \
  -t rag_documents -t rag_chunks -t rag_query_logs \
  > rag_backup.sql

# Restore
psql -U postgres -d magnus < rag_backup.sql
```

### Clean Cache

```python
# Clear Redis cache
import redis
r = redis.Redis(host='localhost', port=6379, db=1)
r.flushdb()

# Or programmatically
from src.rag.core.cache_manager import CacheManager
cache = CacheManager()
cache.clear_all()
```

---

## Useful SQL Queries

```sql
-- Top queried topics
SELECT
    context_type,
    COUNT(*) as query_count,
    AVG(processing_time_ms) as avg_latency
FROM rag_query_logs
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY context_type
ORDER BY query_count DESC;

-- Cache effectiveness
SELECT
    cache_hit,
    COUNT(*) as count,
    AVG(processing_time_ms) as avg_latency
FROM rag_query_logs
WHERE created_at > NOW() - INTERVAL '1 day'
GROUP BY cache_hit;

-- Document ingestion status
SELECT
    status,
    COUNT(*) as count,
    SUM(total_chunks) as total_chunks
FROM rag_documents
GROUP BY status;

-- Slowest queries
SELECT
    query_text,
    processing_time_ms,
    cache_hit,
    created_at
FROM rag_query_logs
ORDER BY processing_time_ms DESC
LIMIT 10;
```

---

## File Locations Reference

```
Important Files:
├── Architecture: docs/architecture/RAG_SYSTEM_ARCHITECTURE.md
├── Integration: docs/architecture/RAG_INTEGRATION_GUIDE.md
├── Summary: RAG_IMPLEMENTATION_SUMMARY.md
└── This File: docs/RAG_QUICK_REFERENCE.md

Source Code:
├── Services: src/rag/services/
├── Core: src/rag/core/
├── Database: src/rag/database/
└── Config: src/rag/config/rag_config.py

Scripts:
├── Setup: scripts/rag/setup_rag_system.py
├── Ingest: scripts/rag/ingest_documents.py
└── Test: scripts/rag/test_query.py

Data:
├── Documents: data/documents/raw/
├── Qdrant: data/qdrant_storage/
└── Cache: data/cache/
```

---

## Support Resources

### Documentation
- Full Architecture: `docs/architecture/RAG_SYSTEM_ARCHITECTURE.md`
- Integration Guide: `docs/architecture/RAG_INTEGRATION_GUIDE.md`
- Implementation Summary: `RAG_IMPLEMENTATION_SUMMARY.md`

### External Resources
- Qdrant Docs: https://qdrant.tech/documentation/
- sentence-transformers: https://www.sbert.net/
- LangChain: https://python.langchain.com/docs/

### Internal Tools
- Monitoring Dashboard: Streamlit sidebar
- Query Logs: PostgreSQL `rag_query_logs` table
- Performance Metrics: `RAGMonitoringService.get_metrics()`

---

**Quick Reference Card v1.0.0**
**Last Updated:** 2025-11-20
**For Magnus/AVA RAG System**

Keep this handy during implementation and daily use!
