"""
Initialize Magnus Knowledge Base
=================================

Indexes all project documentation into ChromaDB for RAG queries.

This script:
1. Initializes ChromaDB with persistence
2. Creates 'magnus_knowledge' collection
3. Indexes all markdown documentation
4. Indexes Python source code docstrings
5. Indexes SQL schema comments
6. Verifies indexing with sample queries
"""

import sys
import os
from pathlib import Path
from typing import List
import time

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from src.rag.rag_service import RAGService
from src.rag.document_indexer import DocumentIndexer


def index_markdown_files(indexer: DocumentIndexer) -> int:
    """Index all markdown documentation files"""
    print("\n[1/3] Indexing Markdown Documentation...")
    print("-" * 80)

    root_dir = Path(".")
    patterns = ["*.md", "**/*.md"]

    # Directories to exclude
    exclude_dirs = {
        "venv", "node_modules", ".git", "__pycache__",
        "chroma_db", ".streamlit", ".legion"
    }

    total_chunks = 0
    files_indexed = 0

    for pattern in patterns:
        files = list(root_dir.glob(pattern))

        for file_path in files:
            # Skip if in excluded directory
            if any(exc_dir in file_path.parts for exc_dir in exclude_dirs):
                continue

            try:
                chunks = indexer.index_file(file_path)
                if chunks:
                    files_indexed += 1
                    total_chunks += len(chunks)
                    print(f"   [OK] {file_path} ({len(chunks)} chunks)")
            except Exception as e:
                print(f"   [ERROR] {file_path}: {e}")

    print(f"\nIndexed {files_indexed} markdown files ({total_chunks} chunks)")
    return total_chunks


def index_python_docstrings(indexer: DocumentIndexer) -> int:
    """Index Python source code (docstrings and key code)"""
    print("\n[2/3] Indexing Python Source Code...")
    print("-" * 80)

    src_dir = Path("src")
    if not src_dir.exists():
        print("   [SKIP] src/ directory not found")
        return 0

    total_chunks = 0
    files_indexed = 0

    # Index key Python files with good documentation
    important_files = [
        "src/rag/rag_service.py",
        "src/rag/document_indexer.py",
        "src/task_completion_with_qa.py",
        "src/qa/multi_agent_qa_service.py",
        "src/qa/agent_rag_expertise.py",
        "src/ava/telegram_bot_enhanced.py",
        "src/ava/nlp_handler.py",
        "src/ava/autonomous_agent.py",
    ]

    for file_str in important_files:
        file_path = Path(file_str)
        if not file_path.exists():
            continue

        try:
            chunks = indexer.index_file(file_path)
            if chunks:
                files_indexed += 1
                total_chunks += len(chunks)
                print(f"   [OK] {file_path} ({len(chunks)} chunks)")
        except Exception as e:
            print(f"   [ERROR] {file_path}: {e}")

    print(f"\nIndexed {files_indexed} Python files ({total_chunks} chunks)")
    return total_chunks


def index_sql_schemas(indexer: DocumentIndexer) -> int:
    """Index SQL schema files"""
    print("\n[3/3] Indexing SQL Schemas...")
    print("-" * 80)

    sql_files = [
        "src/qa_multi_agent_schema.sql",
        "src/task_management_schema.sql",
        "src/xtrades_schema.sql",
        "src/kalshi_schema.sql",
        "src/nfl_data_schema.sql",
    ]

    total_chunks = 0
    files_indexed = 0

    for file_str in sql_files:
        file_path = Path(file_str)
        if not file_path.exists():
            continue

        try:
            chunks = indexer.index_file(file_path)
            if chunks:
                files_indexed += 1
                total_chunks += len(chunks)
                print(f"   [OK] {file_path} ({len(chunks)} chunks)")
        except Exception as e:
            print(f"   [ERROR] {file_path}: {e}")

    print(f"\nIndexed {files_indexed} SQL files ({total_chunks} chunks)")
    return total_chunks


def verify_indexing(rag: RAGService):
    """Verify indexing with sample queries"""
    print("\n" + "=" * 80)
    print("VERIFYING INDEXING WITH SAMPLE QUERIES")
    print("=" * 80)

    test_queries = [
        "How does the QA system work?",
        "What is the task completion workflow?",
        "How do I use the RAG system?",
        "What is AVA?",
        "How do I complete a task with QA sign-off?"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n[Query {i}/5] {query}")
        print("-" * 80)

        try:
            result = rag.query(query, use_cache=False)

            print(f"Confidence: {result.confidence:.2%}")
            print(f"Answer: {result.answer[:200]}...")
            print(f"Sources: {len(result.sources)} documents")
            if result.sources:
                print(f"Top source: {result.sources[0].metadata.get('file_path', 'unknown')}")
        except Exception as e:
            print(f"[ERROR] {e}")

        time.sleep(0.5)  # Rate limiting


def main():
    """Main initialization function"""
    print("=" * 80)
    print("MAGNUS KNOWLEDGE BASE INITIALIZATION")
    print("=" * 80)
    print()
    print("This will index all project documentation into ChromaDB.")
    print("Estimated time: 2-5 minutes")
    print()

    start_time = time.time()

    # Initialize RAG service
    print("[Step 1] Initializing RAG Service...")
    rag = RAGService(
        collection_name="magnus_knowledge",
        embedding_model="all-mpnet-base-v2"
    )
    print("   [OK] RAG service initialized")

    # Initialize document indexer
    print("[Step 2] Initializing Document Indexer...")
    indexer = DocumentIndexer(
        rag_service=rag,
        chunk_size=1000,
        chunk_overlap=200
    )
    print("   [OK] Document indexer initialized")

    # Index all documentation
    print("\n[Step 3] Indexing Project Documentation...")
    print("=" * 80)

    total_chunks = 0
    total_chunks += index_markdown_files(indexer)
    total_chunks += index_python_docstrings(indexer)
    total_chunks += index_sql_schemas(indexer)

    # Verify indexing
    print("\n[Step 4] Verifying Indexing...")
    verify_indexing(rag)

    # Summary
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 80)
    print("INITIALIZATION COMPLETE")
    print("=" * 80)
    print(f"\nTotal document chunks indexed: {total_chunks}")
    print(f"Time elapsed: {elapsed_time:.1f} seconds")
    print(f"ChromaDB location: ./chroma_db")
    print(f"Collection name: magnus_knowledge")
    print(f"Embedding model: all-mpnet-base-v2")
    print("\nThe knowledge base is ready for queries via AVA!")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInitialization cancelled by user.")
    except Exception as e:
        print(f"\n\n[ERROR] Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
