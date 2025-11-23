"""
Magnus RAG System - Document Processor
======================================

Handles document loading, text extraction, and intelligent chunking
for multiple file formats (PDF, Markdown, DOCX, TXT).

Author: AI Engineer Agent
Created: 2025-11-20
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import hashlib

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    TextLoader,
    UnstructuredWordDocumentLoader
)

logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """Document type categories"""
    TRADING_GUIDE = "trading_guide"
    STRATEGY = "strategy"
    MARKET_ANALYSIS = "market_analysis"
    RESEARCH = "research"
    GENERAL = "general"


@dataclass
class DocumentChunk:
    """Represents a chunk of a document"""
    chunk_id: str
    text: str
    metadata: Dict[str, Any]
    token_count: int
    char_count: int
    chunk_index: int


@dataclass
class ProcessedDocument:
    """Represents a processed document"""
    document_id: str
    title: str
    file_path: str
    file_hash: str
    document_type: DocumentType
    chunks: List[DocumentChunk]
    total_chunks: int
    metadata: Dict[str, Any]


class DocumentProcessor:
    """
    Document processor for Magnus RAG system

    Features:
    - Multi-format support (PDF, Markdown, DOCX, TXT)
    - Intelligent chunking with overlap
    - Metadata extraction
    - Text cleaning and normalization
    - Token-aware splitting
    """

    # File format handlers
    LOADERS = {
        ".pdf": PyPDFLoader,
        ".md": UnstructuredMarkdownLoader,
        ".txt": TextLoader,
        ".docx": UnstructuredWordDocumentLoader,
        ".doc": UnstructuredWordDocumentLoader
    }

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        separators: Optional[List[str]] = None
    ):
        """
        Initialize document processor

        Args:
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks
            separators: Custom separators for chunking
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Default separators (optimized for trading docs)
        if separators is None:
            separators = [
                "\n\n\n",  # Major section breaks
                "\n\n",    # Paragraph breaks
                "\n",      # Line breaks
                ". ",      # Sentence breaks
                ", ",      # Clause breaks
                " ",       # Word breaks
                ""         # Character breaks (fallback)
            ]

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
            is_separator_regex=False
        )

    def process_document(
        self,
        file_path: str,
        document_type: DocumentType = DocumentType.GENERAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProcessedDocument:
        """
        Process a document file into chunks

        Args:
            file_path: Path to document file
            document_type: Type/category of document
            metadata: Additional metadata

        Returns:
            ProcessedDocument with chunks
        """
        path = Path(file_path)

        # Validate file exists
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        # Validate file format
        if path.suffix.lower() not in self.LOADERS:
            raise ValueError(
                f"Unsupported file format: {path.suffix}. "
                f"Supported formats: {list(self.LOADERS.keys())}"
            )

        logger.info(f"Processing document: {path.name}")

        try:
            # Load document
            raw_text = self._load_document(file_path)

            # Clean text
            cleaned_text = self._clean_text(raw_text)

            # Extract metadata
            doc_metadata = self._extract_metadata(path, cleaned_text, document_type)
            if metadata:
                doc_metadata.update(metadata)

            # Calculate file hash
            file_hash = self._calculate_file_hash(file_path)

            # Generate document ID
            document_id = self._generate_document_id(file_path, file_hash)

            # Chunk document
            chunks = self._chunk_document(
                text=cleaned_text,
                document_id=document_id,
                document_type=document_type,
                base_metadata=doc_metadata
            )

            # Create processed document
            processed = ProcessedDocument(
                document_id=document_id,
                title=doc_metadata.get("title", path.stem),
                file_path=str(path),
                file_hash=file_hash,
                document_type=document_type,
                chunks=chunks,
                total_chunks=len(chunks),
                metadata=doc_metadata
            )

            logger.info(
                f"Successfully processed document: {path.name} "
                f"({len(chunks)} chunks)"
            )

            return processed

        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            raise

    def _load_document(self, file_path: str) -> str:
        """
        Load document content based on file type

        Args:
            file_path: Path to document

        Returns:
            Document text content
        """
        path = Path(file_path)
        loader_class = self.LOADERS[path.suffix.lower()]

        try:
            # Special handling for text files (encoding)
            if path.suffix.lower() == ".txt":
                loader = loader_class(file_path, encoding="utf-8")
            else:
                loader = loader_class(file_path)

            # Load documents
            documents = loader.load()

            # Combine page contents
            text = "\n\n".join(doc.page_content for doc in documents)

            logger.info(f"Loaded document: {len(text)} characters")
            return text

        except Exception as e:
            logger.error(f"Error loading document: {e}")
            raise

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)

        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # Remove repeated punctuation
        text = re.sub(r'([.!?]){3,}', r'\1\1\1', text)

        # Trim whitespace
        text = text.strip()

        return text

    def _extract_metadata(
        self,
        path: Path,
        text: str,
        document_type: DocumentType
    ) -> Dict[str, Any]:
        """
        Extract metadata from document

        Args:
            path: Document path
            text: Document text
            document_type: Document type

        Returns:
            Metadata dictionary
        """
        metadata = {
            "title": path.stem,
            "filename": path.name,
            "file_extension": path.suffix.lower(),
            "file_size_bytes": path.stat().st_size,
            "document_type": document_type.value,
            "char_count": len(text),
            "word_count": len(text.split()),
        }

        # Extract first line as potential title
        lines = text.split('\n', 1)
        if lines:
            first_line = lines[0].strip()
            if len(first_line) < 200:  # Reasonable title length
                metadata["extracted_title"] = first_line

        # Detect topic keywords (simple approach)
        topics = self._detect_topics(text)
        if topics:
            metadata["topics"] = topics

        return metadata

    def _detect_topics(self, text: str) -> List[str]:
        """
        Detect topics/keywords in text

        Args:
            text: Document text

        Returns:
            List of detected topics
        """
        # Trading-specific keyword detection
        topics = []

        keyword_map = {
            "options": ["option", "call", "put", "strike", "expiration"],
            "wheel_strategy": ["wheel", "cash-secured put", "covered call", "csp"],
            "technical_analysis": ["support", "resistance", "chart", "indicator", "macd", "rsi"],
            "fundamental_analysis": ["earnings", "revenue", "valuation", "p/e ratio"],
            "risk_management": ["risk", "stop loss", "position size", "diversification"],
            "market_sentiment": ["sentiment", "bullish", "bearish", "neutral"]
        }

        text_lower = text.lower()

        for topic, keywords in keyword_map.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)

        return topics

    def _chunk_document(
        self,
        text: str,
        document_id: str,
        document_type: DocumentType,
        base_metadata: Dict[str, Any]
    ) -> List[DocumentChunk]:
        """
        Chunk document into smaller pieces

        Args:
            text: Document text
            document_id: Document identifier
            document_type: Document type
            base_metadata: Base metadata to include

        Returns:
            List of DocumentChunk objects
        """
        # Split text into chunks
        text_chunks = self.text_splitter.split_text(text)

        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            # Generate chunk ID
            chunk_id = f"{document_id}_chunk_{i}"

            # Create chunk metadata
            chunk_metadata = {
                **base_metadata,
                "document_id": document_id,
                "chunk_index": i,
                "total_chunks": len(text_chunks),
                "document_type": document_type.value
            }

            # Calculate token count (rough estimate: ~4 chars per token)
            token_count = len(chunk_text) // 4

            # Create chunk object
            chunk = DocumentChunk(
                chunk_id=chunk_id,
                text=chunk_text,
                metadata=chunk_metadata,
                token_count=token_count,
                char_count=len(chunk_text),
                chunk_index=i
            )

            chunks.append(chunk)

        logger.info(f"Created {len(chunks)} chunks from document")
        return chunks

    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA256 hash of file

        Args:
            file_path: Path to file

        Returns:
            File hash
        """
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()

    def _generate_document_id(self, file_path: str, file_hash: str) -> str:
        """
        Generate unique document ID

        Args:
            file_path: Path to file
            file_hash: File hash

        Returns:
            Document ID
        """
        # Use first 12 characters of hash plus filename
        path = Path(file_path)
        return f"{path.stem}_{file_hash[:12]}"

    def batch_process_directory(
        self,
        directory_path: str,
        document_type: DocumentType = DocumentType.GENERAL,
        recursive: bool = True,
        file_extensions: Optional[List[str]] = None
    ) -> List[ProcessedDocument]:
        """
        Process all documents in a directory

        Args:
            directory_path: Path to directory
            document_type: Type of documents
            recursive: Search subdirectories
            file_extensions: Filter by extensions

        Returns:
            List of processed documents
        """
        path = Path(directory_path)

        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory_path}")

        # Default file extensions
        if file_extensions is None:
            file_extensions = list(self.LOADERS.keys())

        # Find files
        pattern = "**/*" if recursive else "*"
        files = []
        for ext in file_extensions:
            files.extend(path.glob(f"{pattern}{ext}"))

        logger.info(f"Found {len(files)} files to process in {directory_path}")

        # Process each file
        processed_documents = []
        for file_path in files:
            try:
                doc = self.process_document(
                    file_path=str(file_path),
                    document_type=document_type
                )
                processed_documents.append(doc)

            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")

        logger.info(
            f"Successfully processed {len(processed_documents)}/{len(files)} documents"
        )

        return processed_documents

    def get_stats(self) -> Dict[str, Any]:
        """
        Get processor statistics

        Returns:
            Dictionary with stats
        """
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "supported_formats": list(self.LOADERS.keys()),
            "separators_count": len(self.text_splitter.separators)
        }


if __name__ == "__main__":
    # Test the document processor
    print("Magnus Document Processor - Test")
    print("=" * 60)

    # Initialize
    processor = DocumentProcessor()

    # Print stats
    stats = processor.get_stats()
    print("\nProcessor Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Test with sample text
    print("\nTesting text chunking...")
    sample_text = """
    The Wheel Strategy is a popular options trading strategy that combines
    cash-secured puts and covered calls to generate consistent income.

    Step 1: Sell Cash-Secured Puts
    Begin by selling put options on stocks you'd be willing to own. The premium
    collected provides immediate income. If the stock stays above the strike price,
    you keep the premium and the position expires worthless.

    Step 2: Get Assigned (If Necessary)
    If the stock price falls below the strike price, you'll be assigned the shares
    at the strike price. This is acceptable since you selected a stock you wanted
    to own at this price.

    Step 3: Sell Covered Calls
    Once you own the shares, sell covered call options against your position.
    This generates additional premium income while potentially selling your shares
    at a profit if called away.
    """

    # Create temporary file for testing
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_text)
        temp_file = f.name

    try:
        # Process document
        doc = processor.process_document(
            file_path=temp_file,
            document_type=DocumentType.TRADING_GUIDE
        )

        print(f"\nProcessed Document:")
        print(f"  ID: {doc.document_id}")
        print(f"  Title: {doc.title}")
        print(f"  Type: {doc.document_type.value}")
        print(f"  Total Chunks: {doc.total_chunks}")
        print(f"\nFirst Chunk:")
        print(f"  Text: {doc.chunks[0].text[:100]}...")
        print(f"  Token Count: {doc.chunks[0].token_count}")
        print(f"  Metadata: {doc.chunks[0].metadata}")

    finally:
        # Clean up temp file
        import os
        os.unlink(temp_file)
