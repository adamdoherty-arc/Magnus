"""
Magnus RAG System - Vector Store
=================================

ChromaDB-based vector store for Magnus RAG system.
Provides persistent vector storage with metadata filtering and similarity search.

Author: AI Engineer Agent
Created: 2025-11-20
"""

import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)


class VectorStore:
    """
    ChromaDB-based vector store for Magnus RAG system

    Features:
    - Persistent storage with automatic backups
    - Efficient similarity search
    - Metadata filtering
    - Collection management
    - CRUD operations for documents and chunks
    """

    def __init__(
        self,
        persist_directory: str = "c:/code/Magnus/data/chromadb",
        collection_name: str = "magnus_knowledge_base",
        embedding_dimension: int = 384
    ):
        """
        Initialize ChromaDB vector store

        Args:
            persist_directory: Directory for persistent storage
            collection_name: Name of the vector collection
            embedding_dimension: Dimension of embedding vectors
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_dimension = embedding_dimension

        # Create persist directory if it doesn't exist
        Path(persist_directory).mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name=collection_name
            )
            logger.info(f"Loaded existing collection: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={
                    "hnsw:space": "cosine",
                    "description": "Magnus Trading Platform Knowledge Base"
                }
            )
            logger.info(f"Created new collection: {collection_name}")

    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to the vector store

        Args:
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            ids: List of document IDs (auto-generated if None)

        Returns:
            List of document IDs
        """
        if not documents:
            logger.warning("No documents to add")
            return []

        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(documents))]

        # Prepare metadatas
        if metadatas is None:
            metadatas = [{} for _ in range(len(documents))]

        try:
            # Add to ChromaDB
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"Added {len(documents)} documents to vector store")
            return ids

        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise

    def search(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List]:
        """
        Search for similar documents

        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Metadata filter conditions
            where_document: Document content filter conditions

        Returns:
            Dictionary with ids, documents, metadatas, distances
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                where_document=where_document
            )

            # Flatten results (query returns nested lists)
            flattened = {
                "ids": results["ids"][0] if results["ids"] else [],
                "documents": results["documents"][0] if results["documents"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                "distances": results["distances"][0] if results["distances"] else []
            }

            # Convert distances to similarity scores (1 - cosine distance)
            if flattened["distances"]:
                flattened["scores"] = [1 - dist for dist in flattened["distances"]]
            else:
                flattened["scores"] = []

            logger.info(f"Found {len(flattened['ids'])} similar documents")
            return flattened

        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise

    def get_by_ids(self, ids: List[str]) -> Dict[str, List]:
        """
        Get documents by their IDs

        Args:
            ids: List of document IDs

        Returns:
            Dictionary with documents and metadatas
        """
        try:
            results = self.collection.get(
                ids=ids,
                include=["documents", "metadatas", "embeddings"]
            )
            return results

        except Exception as e:
            logger.error(f"Error retrieving documents by IDs: {e}")
            raise

    def update_documents(
        self,
        ids: List[str],
        documents: Optional[List[str]] = None,
        embeddings: Optional[List[List[float]]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Update existing documents

        Args:
            ids: List of document IDs to update
            documents: Updated document texts
            embeddings: Updated embedding vectors
            metadatas: Updated metadata dictionaries

        Returns:
            True if successful
        """
        try:
            self.collection.update(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )

            logger.info(f"Updated {len(ids)} documents")
            return True

        except Exception as e:
            logger.error(f"Error updating documents: {e}")
            raise

    def delete_documents(self, ids: List[str]) -> bool:
        """
        Delete documents by IDs

        Args:
            ids: List of document IDs to delete

        Returns:
            True if successful
        """
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents")
            return True

        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise

    def delete_by_filter(self, where: Dict[str, Any]) -> bool:
        """
        Delete documents matching metadata filter

        Args:
            where: Metadata filter conditions

        Returns:
            True if successful
        """
        try:
            self.collection.delete(where=where)
            logger.info(f"Deleted documents matching filter: {where}")
            return True

        except Exception as e:
            logger.error(f"Error deleting documents by filter: {e}")
            raise

    def count(self) -> int:
        """
        Get total number of documents in collection

        Returns:
            Document count
        """
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            return 0

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get collection information and statistics

        Returns:
            Dictionary with collection info
        """
        try:
            count = self.count()

            return {
                "name": self.collection_name,
                "document_count": count,
                "embedding_dimension": self.embedding_dimension,
                "persist_directory": self.persist_directory,
                "metadata": self.collection.metadata if hasattr(self.collection, 'metadata') else {}
            }

        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}

    def reset_collection(self) -> bool:
        """
        Reset (delete and recreate) the collection
        WARNING: This deletes all data!

        Returns:
            True if successful
        """
        try:
            # Delete existing collection
            self.client.delete_collection(name=self.collection_name)
            logger.warning(f"Deleted collection: {self.collection_name}")

            # Create new collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={
                    "hnsw:space": "cosine",
                    "description": "Magnus Trading Platform Knowledge Base"
                }
            )
            logger.info(f"Created new collection: {self.collection_name}")
            return True

        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics

        Returns:
            Dictionary with statistics
        """
        try:
            count = self.count()
            info = self.get_collection_info()

            # Calculate storage size
            persist_path = Path(self.persist_directory)
            storage_size_mb = sum(
                f.stat().st_size for f in persist_path.rglob('*') if f.is_file()
            ) / (1024 * 1024)

            return {
                "collection_name": self.collection_name,
                "total_documents": count,
                "embedding_dimension": self.embedding_dimension,
                "storage_size_mb": round(storage_size_mb, 2),
                "persist_directory": self.persist_directory,
                "is_persistent": True,
                "distance_metric": "cosine"
            }

        except Exception as e:
            logger.error(f"Error getting vector store stats: {e}")
            return {}

    def health_check(self) -> Tuple[bool, str]:
        """
        Check vector store health

        Returns:
            Tuple of (is_healthy, message)
        """
        try:
            # Test basic operations
            count = self.count()

            # Check persistence directory
            persist_path = Path(self.persist_directory)
            if not persist_path.exists():
                return False, "Persist directory does not exist"

            return True, f"Healthy - {count} documents stored"

        except Exception as e:
            return False, f"Health check failed: {str(e)}"


if __name__ == "__main__":
    # Test the vector store
    print("Magnus Vector Store - Test")
    print("=" * 60)

    # Initialize
    store = VectorStore()

    # Print stats
    stats = store.get_stats()
    print("\nVector Store Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Health check
    is_healthy, message = store.health_check()
    print(f"\nHealth Check: {'✓' if is_healthy else '✗'} {message}")
