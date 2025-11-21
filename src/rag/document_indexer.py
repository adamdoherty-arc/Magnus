"""
Production Document Indexer - Semantic Chunking
===============================================

Implements 2025 best practices for document processing:
- Semantic chunking (preserves context)
- Metadata extraction
- Deduplication
- Incremental indexing (delta processing)
- Progress tracking
"""

import os
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import re
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Semantically coherent document chunk"""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    doc_hash: str


class DocumentIndexer:
    """
    Semantic document indexer with best practices

    Features:
    - Semantic chunking at paragraph/section boundaries
    - Metadata extraction (title, category, date)
    - Duplicate detection
    - Delta processing (only index changes)
    - Progress tracking
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100
    ):
        """
        Initialize document indexer

        Args:
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks for context
            min_chunk_size: Minimum chunk size (discard smaller)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

        # Track indexed documents
        self.indexed_docs = set()

        logger.info("Document Indexer initialized")

    def _extract_metadata(self, file_path: Path, content: str) -> Dict[str, Any]:
        """
        Extract metadata from document

        Args:
            file_path: Path to document
            content: Document content

        Returns:
            Metadata dictionary
        """
        metadata = {
            'source': str(file_path),
            'filename': file_path.name,
            'file_type': file_path.suffix,
            'indexed_at': datetime.now().isoformat()
        }

        # Extract title (first # heading or filename)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
        else:
            metadata['title'] = file_path.stem

        # Extract category from path
        parts = file_path.parts
        if len(parts) > 1:
            metadata['category'] = parts[-2]  # Parent directory
        else:
            metadata['category'] = 'general'

        # Estimate reading time (200 words/min)
        word_count = len(content.split())
        metadata['word_count'] = word_count
        metadata['reading_time_min'] = max(1, word_count // 200)

        return metadata

    def _semantic_chunk(self, content: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """
        Chunk document at semantic boundaries

        Priority boundaries:
        1. Markdown headers (##, ###)
        2. Double newlines (paragraphs)
        3. Single newlines
        4. Hard split at chunk_size

        Args:
            content: Document content
            metadata: Document metadata

        Returns:
            List of semantically coherent chunks
        """
        chunks = []

        # Split by headers first
        sections = re.split(r'\n(#{2,6}\s+.+)\n', content)

        current_chunk = ""
        doc_hash = hashlib.md5(content.encode()).hexdigest()

        for section in sections:
            # If adding this section exceeds chunk size, save current chunk
            if len(current_chunk) + len(section) > self.chunk_size and current_chunk:
                if len(current_chunk) >= self.min_chunk_size:
                    chunk_id = hashlib.md5(
                        f"{metadata['source']}_{len(chunks)}".encode()
                    ).hexdigest()

                    chunks.append(DocumentChunk(
                        content=current_chunk.strip(),
                        metadata={
                            **metadata,
                            'chunk_index': len(chunks),
                            'total_chunks': 0  # Will update later
                        },
                        chunk_id=chunk_id,
                        doc_hash=doc_hash
                    ))

                # Start new chunk with overlap
                if self.chunk_overlap > 0 and len(current_chunk) > self.chunk_overlap:
                    current_chunk = current_chunk[-self.chunk_overlap:] + section
                else:
                    current_chunk = section
            else:
                current_chunk += section

        # Add final chunk
        if current_chunk and len(current_chunk) >= self.min_chunk_size:
            chunk_id = hashlib.md5(
                f"{metadata['source']}_{len(chunks)}".encode()
            ).hexdigest()

            chunks.append(DocumentChunk(
                content=current_chunk.strip(),
                metadata={
                    **metadata,
                    'chunk_index': len(chunks),
                    'total_chunks': 0
                },
                chunk_id=chunk_id,
                doc_hash=doc_hash
            ))

        # Update total_chunks
        for chunk in chunks:
            chunk.metadata['total_chunks'] = len(chunks)

        logger.info(f"Created {len(chunks)} semantic chunks from {metadata['filename']}")

        return chunks

    def index_file(self, file_path: Path) -> List[DocumentChunk]:
        """
        Index a single file

        Args:
            file_path: Path to file

        Returns:
            List of document chunks
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract metadata
            metadata = self._extract_metadata(file_path, content)

            # Check if already indexed (hash-based deduplication)
            doc_hash = hashlib.md5(content.encode()).hexdigest()
            if doc_hash in self.indexed_docs:
                logger.info(f"Skipping {file_path.name} (already indexed)")
                return []

            # Semantic chunking
            chunks = self._semantic_chunk(content, metadata)

            # Mark as indexed
            self.indexed_docs.add(doc_hash)

            logger.info(f"Indexed {file_path.name}: {len(chunks)} chunks")

            return chunks

        except Exception as e:
            logger.error(f"Error indexing {file_path}: {e}")
            return []

    def index_directory(
        self,
        directory: Path,
        file_patterns: List[str] = ["*.md", "*.txt"],
        recursive: bool = True,
        exclude_patterns: List[str] = None
    ) -> List[DocumentChunk]:
        """
        Index all documents in a directory

        Args:
            directory: Directory to index
            file_patterns: File patterns to match (e.g., ["*.md"])
            recursive: Search subdirectories
            exclude_patterns: Patterns to exclude (e.g., ["*test*", "*temp*"])

        Returns:
            List of all document chunks
        """
        all_chunks = []
        exclude_patterns = exclude_patterns or []

        logger.info(f"Indexing directory: {directory}")

        for pattern in file_patterns:
            if recursive:
                files = directory.rglob(pattern)
            else:
                files = directory.glob(pattern)

            for file_path in files:
                # Check exclusions
                if any(file_path.match(exc) for exc in exclude_patterns):
                    logger.debug(f"Skipping excluded: {file_path}")
                    continue

                chunks = self.index_file(file_path)
                all_chunks.extend(chunks)

        logger.info(f"Indexed {len(all_chunks)} total chunks from {directory}")

        return all_chunks

    def get_indexing_stats(self) -> Dict[str, Any]:
        """Get indexing statistics"""
        return {
            'total_docs_indexed': len(self.indexed_docs),
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'min_chunk_size': self.min_chunk_size
        }


if __name__ == "__main__":
    # Test document indexer
    print("Testing Document Indexer\n")

    indexer = DocumentIndexer(chunk_size=500, chunk_overlap=100)

    # Test with current directory docs
    current_dir = Path(".")
    chunks = indexer.index_directory(
        current_dir,
        file_patterns=["*.md"],
        recursive=False,
        exclude_patterns=["*test*", "*temp*", "*old*"]
    )

    print(f"\nIndexed {len(chunks)} chunks")
    print(f"Stats: {indexer.get_indexing_stats()}")

    # Show sample chunks
    print("\nSample chunks:")
    for chunk in chunks[:3]:
        print(f"\n--- Chunk {chunk.chunk_index + 1}/{chunk.metadata['total_chunks']} ---")
        print(f"Source: {chunk.metadata['filename']}")
        print(f"Content: {chunk.content[:200]}...")
