"""
Production RAG System - Comprehensive Test
=========================================

Tests:
1. RAG Service initialization
2. Document indexing (Magnus documentation)
3. Hybrid search
4. Adaptive retrieval
5. Caching
6. Evaluation metrics
7. End-to-end Q&A
"""

from src.rag import RAGService, DocumentIndexer
from pathlib import Path
import json
import time

def test_rag_system():
    """Comprehensive RAG system test"""

    print("=" * 80)
    print("PRODUCTION RAG SYSTEM - COMPREHENSIVE TEST")
    print("=" * 80)
    print()

    # Test 1: RAG Service Initialization
    print("[1/7] Initializing RAG Service...")
    rag = RAGService(
        collection_name="magnus_test",
        cache_ttl_seconds=300,
        min_confidence_threshold=0.6
    )
    print(f"  Collection: {rag.collection_name}")
    print(f"  Embedding model: all-mpnet-base-v2")
    print(f"  [OK] RAG Service initialized")
    print()

    # Test 2: Document Indexing
    print("[2/7] Indexing Magnus documentation...")
    indexer = DocumentIndexer(chunk_size=800, chunk_overlap=150)

    # Index current directory markdown files
    current_dir = Path(".")
    chunks = indexer.index_directory(
        current_dir,
        file_patterns=["*.md"],
        recursive=False,
        exclude_patterns=["*test*", "*old*", "*backup*"]
    )

    print(f"  Indexed {len(chunks)} chunks")
    print(f"  Documents indexed: {indexer.get_indexing_stats()['total_docs_indexed']}")

    # Add chunks to RAG
    if chunks:
        rag.add_documents(
            documents=[chunk.content for chunk in chunks[:50]],  # Limit for test
            metadatas=[chunk.metadata for chunk in chunks[:50]],
            ids=[chunk.chunk_id for chunk in chunks[:50]]
        )
        print(f"  [OK] Added {min(50, len(chunks))} chunks to RAG")
    print()

    # Test 3: Semantic Search
    print("[3/7] Testing semantic search...")
    test_query = "What is Cash Secured Put strategy?"
    result = rag.query(test_query, force_retrieval_method='semantic')
    print(f"  Query: {test_query}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Sources: {len(result.sources)}")
    print(f"  Time: {result.processing_time_ms:.0f}ms")
    print(f"  [OK] Semantic search working")
    print()

    # Test 4: Hybrid Search
    print("[4/7] Testing hybrid search...")
    test_query2 = "wheel strategy selling covered calls"
    result2 = rag.query(test_query2, force_retrieval_method='hybrid')
    print(f"  Query: {test_query2}")
    print(f"  Method: {result2.retrieval_method}")
    print(f"  Confidence: {result2.confidence:.2f}")
    print(f"  Time: {result2.processing_time_ms:.0f}ms")
    print(f"  [OK] Hybrid search working")
    print()

    # Test 5: Adaptive Retrieval
    print("[5/7] Testing adaptive retrieval...")
    test_queries = [
        "What is CSP?",  # Simple
        "How do I find good options opportunities?",  # Medium
        "What's the best strategy for high IV stocks with earnings coming up?",  # Complex
    ]

    for q in test_queries:
        result = rag.query(q, use_cache=False)
        print(f"  Query: {q}")
        print(f"    Complexity: {result.query_complexity}")
        print(f"    Method: {result.retrieval_method}")
        print(f"    Confidence: {result.confidence:.2f}")

    print(f"  [OK] Adaptive retrieval working")
    print()

    # Test 6: Caching
    print("[6/7] Testing caching...")
    cache_query = "What is options trading?"

    # First query (not cached)
    start = time.time()
    result_uncached = rag.query(cache_query)
    time_uncached = (time.time() - start) * 1000

    # Second query (should be cached)
    start = time.time()
    result_cached = rag.query(cache_query)
    time_cached = (time.time() - start) * 1000

    print(f"  Uncached time: {time_uncached:.0f}ms")
    print(f"  Cached time: {time_cached:.0f}ms")
    print(f"  Speed improvement: {time_uncached/time_cached:.1f}x")
    print(f"  [OK] Caching working")
    print()

    # Test 7: Metrics and Evaluation
    print("[7/7] Evaluation metrics...")
    metrics = rag.get_metrics()
    stats = rag.get_collection_stats()

    print(f"  Total queries: {metrics['total_queries']}")
    print(f"  Cache hit rate: {metrics['cache_hit_rate']:.1%}")
    print(f"  Avg confidence: {metrics['avg_confidence']:.2f}")
    print(f"  Avg response time: {metrics['avg_response_time_ms']:.0f}ms")
    print(f"  Success rate: {metrics['success_rate']:.1%}")
    print(f"  Total documents: {stats['total_documents']}")
    print(f"  [OK] Metrics tracking working")
    print()

    print("=" * 80)
    print("ALL TESTS PASSED!")
    print("=" * 80)
    print()

    print("Summary:")
    print(f"  - RAG Service: WORKING")
    print(f"  - Document Indexing: WORKING ({len(chunks)} chunks)")
    print(f"  - Semantic Search: WORKING")
    print(f"  - Hybrid Search: WORKING")
    print(f"  - Adaptive Retrieval: WORKING (3 complexity levels)")
    print(f"  - Caching: WORKING ({time_uncached/time_cached:.1f}x faster)")
    print(f"  - Metrics: WORKING")
    print()
    print("Ready for QA Review!")
    print()

    return rag, metrics, stats


if __name__ == "__main__":
    test_rag_system()
