"""
RAG Service for Magnus Financial Assistant
Handles document indexing, retrieval, and question answering
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from datetime import datetime

# Vector database and embeddings
try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    logging.warning("ChromaDB not installed. Install with: pip install chromadb")

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    logging.warning("sentence-transformers not installed. Install with: pip install sentence-transformers")

# LLM integration
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    logging.warning("anthropic not installed. Install with: pip install anthropic")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGService:
    """
    Retrieval-Augmented Generation service for financial assistant.

    Features:
    - Document indexing with semantic chunking
    - Vector similarity search
    - Context assembly for LLM queries
    - Multi-source retrieval (docs, trades, market data)
    """

    def __init__(
        self,
        collection_name: str = "magnus_docs",
        embedding_model: str = "all-mpnet-base-v2",
        chroma_path: str = "./chroma_db",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize RAG service.

        Args:
            collection_name: Name of the vector collection
            embedding_model: Sentence transformer model to use
            chroma_path: Path to ChromaDB storage
            chunk_size: Size of text chunks in characters
            chunk_overlap: Overlap between chunks
        """
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Initialize embedding model
        if HAS_SENTENCE_TRANSFORMERS:
            logger.info(f"Loading embedding model: {embedding_model}")
            self.embedding_model = SentenceTransformer(embedding_model)
            self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
            logger.info(f"Embedding dimension: {self.embedding_dim}")
        else:
            raise ImportError("sentence-transformers required. Install with: pip install sentence-transformers")

        # Initialize ChromaDB
        if HAS_CHROMADB:
            logger.info(f"Initializing ChromaDB at: {chroma_path}")
            self.client = chromadb.PersistentClient(path=chroma_path)
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Magnus Financial Assistant knowledge base"}
            )
            logger.info(f"Collection '{collection_name}' ready with {self.collection.count()} documents")
        else:
            raise ImportError("chromadb required. Install with: pip install chromadb")

        # Initialize Anthropic client if available
        self.llm_client = None
        if HAS_ANTHROPIC:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.llm_client = anthropic.Anthropic(api_key=api_key)
                logger.info("Anthropic client initialized")
            else:
                logger.warning("ANTHROPIC_API_KEY not found in environment")

    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk

        Returns:
            List of chunks with metadata
        """
        chunks = []
        start = 0
        chunk_id = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('. ')
                if last_period > self.chunk_size * 0.7:  # At least 70% of chunk size
                    end = start + last_period + 2
                    chunk = text[start:end]

            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata.update({
                "chunk_id": chunk_id,
                "start_char": start,
                "end_char": end,
                "chunk_size": len(chunk)
            })

            chunks.append({
                "text": chunk.strip(),
                "metadata": chunk_metadata
            })

            start = end - self.chunk_overlap
            chunk_id += 1

        return chunks

    def index_document(
        self,
        content: str,
        doc_id: str,
        metadata: Dict[str, Any] = None
    ) -> int:
        """
        Index a single document.

        Args:
            content: Document content
            doc_id: Unique document identifier
            metadata: Document metadata

        Returns:
            Number of chunks created
        """
        logger.info(f"Indexing document: {doc_id}")

        # Prepare metadata
        doc_metadata = {
            "doc_id": doc_id,
            "indexed_at": datetime.now().isoformat(),
            "content_length": len(content)
        }
        if metadata:
            doc_metadata.update(metadata)

        # Chunk the document
        chunks = self.chunk_text(content, doc_metadata)

        # Generate embeddings and add to collection
        for i, chunk in enumerate(chunks):
            try:
                embedding = self.embedding_model.encode(chunk["text"])

                # Unique ID for this chunk
                chunk_id = f"{doc_id}_chunk_{i}"

                self.collection.add(
                    ids=[chunk_id],
                    embeddings=[embedding.tolist()],
                    documents=[chunk["text"]],
                    metadatas=[chunk["metadata"]]
                )
            except Exception as e:
                logger.error(f"Error indexing chunk {i} of {doc_id}: {e}")

        logger.info(f"Indexed {len(chunks)} chunks from {doc_id}")
        return len(chunks)

    def index_file(self, file_path: Path) -> int:
        """
        Index a file (markdown, text, etc.).

        Args:
            file_path: Path to file

        Returns:
            Number of chunks created
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            metadata = {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_type": file_path.suffix,
                "file_size": len(content)
            }
            return self.index_document(content, file_path.name, metadata)
        except Exception as e:
            logger.error(f"Error indexing file {file_path}: {e}")
            return 0

    def index_directory(
        self,
        directory: Path,
        pattern: str = "*.md",
        recursive: bool = True
    ) -> Dict[str, int]:
        """
        Index all files matching pattern in directory.

        Args:
            directory: Directory path
            pattern: File pattern (e.g., "*.md")
            recursive: Search subdirectories

        Returns:
            Dictionary mapping file names to chunk counts
        """
        logger.info(f"Indexing directory: {directory} (pattern: {pattern}, recursive: {recursive})")

        results = {}

        # Find matching files
        if recursive:
            files = directory.rglob(pattern)
        else:
            files = directory.glob(pattern)

        # Index each file
        for file_path in files:
            if file_path.is_file():
                chunk_count = self.index_file(file_path)
                results[file_path.name] = chunk_count

        total_chunks = sum(results.values())
        logger.info(f"Indexed {len(results)} files with {total_chunks} total chunks")

        return results

    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant documents.

        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Filter by metadata (e.g., {"file_type": ".md"})

        Returns:
            List of search results with documents and metadata
        """
        logger.info(f"Searching for: '{query}' (top {n_results})")

        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)

        # Search collection
        search_params = {
            "query_embeddings": [query_embedding.tolist()],
            "n_results": n_results
        }
        if filter_metadata:
            search_params["where"] = filter_metadata

        results = self.collection.query(**search_params)

        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                "id": results['ids'][0][i],
                "document": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i] if 'distances' in results else None
            })

        logger.info(f"Found {len(formatted_results)} results")
        return formatted_results

    def get_context_for_query(
        self,
        query: str,
        n_results: int = 3,
        max_tokens: int = 2000
    ) -> str:
        """
        Get relevant context for a query, formatted for LLM.

        Args:
            query: User query
            n_results: Number of documents to retrieve
            max_tokens: Maximum tokens in context (approximate)

        Returns:
            Formatted context string
        """
        results = self.search(query, n_results)

        # Build context
        context_parts = ["Here is relevant information from the Magnus documentation:\n"]

        total_chars = 0
        max_chars = max_tokens * 4  # Rough approximation

        for i, result in enumerate(results, 1):
            source = result['metadata'].get('file_name', 'Unknown')
            text = result['document']

            # Check if adding this would exceed limit
            if total_chars + len(text) > max_chars:
                break

            context_parts.append(f"\n[Source {i}: {source}]\n{text}\n")
            total_chars += len(text)

        context = "\n".join(context_parts)
        logger.info(f"Assembled context: {total_chars} chars from {len(results)} sources")

        return context

    def query(
        self,
        question: str,
        n_results: int = 3,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG.

        Args:
            question: User question
            n_results: Number of documents to retrieve
            system_prompt: Optional custom system prompt

        Returns:
            Dictionary with answer and sources
        """
        if not self.llm_client:
            return {
                "answer": "LLM not configured. Set ANTHROPIC_API_KEY environment variable.",
                "sources": [],
                "error": "No LLM client"
            }

        # Get relevant context
        context = self.get_context_for_query(question, n_results)
        search_results = self.search(question, n_results)

        # Build system prompt
        if not system_prompt:
            system_prompt = """You are Magnus Financial Assistant, an AI advisor for options trading.

Your role is to:
- Answer questions about Magnus trading dashboard features
- Explain options trading concepts (CSP, covered calls, Greeks, etc.)
- Provide accurate information based on the documentation provided
- Be concise and helpful

Always base your answers on the provided documentation. If you don't have enough information, say so."""

        # Build user prompt
        user_prompt = f"""Context from documentation:

{context}

Question: {question}

Please provide a clear, accurate answer based on the documentation above. If the documentation doesn't contain enough information to answer fully, mention what's missing."""

        try:
            # Query LLM
            logger.info("Querying LLM...")
            response = self.llm_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            answer = response.content[0].text

            # Format sources
            sources = [
                {
                    "file": result['metadata'].get('file_name', 'Unknown'),
                    "snippet": result['document'][:200] + "..."
                }
                for result in search_results
            ]

            return {
                "answer": answer,
                "sources": sources,
                "question": question,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error querying LLM: {e}")
            return {
                "answer": f"Error: {str(e)}",
                "sources": [],
                "error": str(e)
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "embedding_model": self.embedding_model.__class__.__name__,
            "embedding_dim": self.embedding_dim,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap
        }


def main():
    """Test the RAG service."""
    print("Magnus RAG Service - Test Mode\n")

    # Initialize service
    rag = RAGService()

    # Show current stats
    stats = rag.get_stats()
    print("Current Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()

    # Index Magnus documentation if collection is empty
    if stats["document_count"] == 0:
        print("Indexing Magnus documentation...")

        # Index all markdown files in current directory
        current_dir = Path(".")
        results = rag.index_directory(current_dir, pattern="*.md", recursive=False)

        print(f"\nIndexed {len(results)} files:")
        for file_name, chunk_count in results.items():
            print(f"  {file_name}: {chunk_count} chunks")

        # Also index docs/ directory if it exists
        docs_dir = Path("./docs")
        if docs_dir.exists():
            print("\nIndexing docs/ directory...")
            results = rag.index_directory(docs_dir, pattern="*.md", recursive=True)
            print(f"Indexed {len(results)} additional files from docs/")

    # Test queries
    test_queries = [
        "What is a cash-secured put?",
        "How does Magnus find CSP opportunities?",
        "What is the wheel strategy?",
        "How do I configure Robinhood?"
    ]

    print("\n" + "="*80)
    print("Testing RAG Queries")
    print("="*80 + "\n")

    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 80)

        # Get context (without LLM)
        context = rag.get_context_for_query(query, n_results=2)
        print("Context (first 500 chars):")
        print(context[:500] + "...\n")

        # Get full answer (with LLM if configured)
        result = rag.query(query, n_results=2)
        print("Answer:")
        print(result['answer'])
        print("\nSources:")
        for source in result.get('sources', []):
            print(f"  - {source['file']}")
        print()


if __name__ == "__main__":
    main()
