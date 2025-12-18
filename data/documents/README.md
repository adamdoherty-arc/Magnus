# Magnus RAG Knowledge Base

This directory contains documents that will be indexed into the RAG (Retrieval Augmented Generation) system.

## Quick Start

### 1. Add Your Documents

Place your financial documents here:
- `.txt` files - Text documents
- `.md` files - Markdown documents
- `.pdf` files - PDF documents (requires `pypdf` package)

Example documents:
- Trading strategy guides
- Options education materials
- Market analysis notes
- Risk management procedures
- Technical analysis guides

### 2. Load Documents

Run the document loader:

```bash
# Load sample financial documents (for testing)
python scripts/load_documents.py --sample

# Load your text/markdown files
python scripts/load_documents.py

# Load PDF files
python scripts/load_documents.py --pdf

# Load both
python scripts/load_documents.py --pdf
```

### 3. Use with AVA

Once documents are loaded, AVA automatically has access to them:

```
You: "What is the wheel strategy?"
AVA: [Response enhanced with knowledge from your documents]

You: "How do I manage portfolio Greeks?"
AVA: [Response includes info from your Greek management guide]

You: "Explain covered calls"
AVA: [Response draws from your options education materials]
```

## Directory Structure

```
data/
├── documents/          # Your source documents (this folder)
│   ├── *.txt          # Text files
│   ├── *.md           # Markdown files
│   └── *.pdf          # PDF files
└── chroma_db/         # Vector database (auto-created)
    └── [ChromaDB files]
```

## Supported File Types

### Currently Supported
- `.txt` - Plain text files
- `.md` - Markdown files

### Supported with pypdf
- `.pdf` - PDF documents

To add PDF support:
```bash
pip install pypdf
```

## Best Practices

### Document Organization
- Use descriptive filenames (e.g., `wheel_strategy_guide.txt`, not `doc1.txt`)
- Organize in subdirectories if you have many documents
- Keep documents focused on specific topics

### Document Quality
- Use clear, well-structured text
- Include relevant headers and sections
- Avoid excessive formatting (plain text works best)
- Break long documents into focused topics

### Content Guidelines
- Financial strategies and concepts
- Trading techniques and approaches
- Risk management procedures
- Technical analysis methods
- Options strategies and Greeks
- Market analysis frameworks
- Personal trading notes and insights

## Adding New Documents

Anytime you want to add new knowledge:

1. Add documents to this folder
2. Run: `python scripts/load_documents.py`
3. New documents are instantly available to AVA

No restart required!

## Removing Documents

To clear the knowledge base and start fresh:

```bash
python scripts/load_documents.py --clear
```

Then reload your documents.

## Testing RAG

Test the system with:

```bash
# Basic test
python test_rag_mvp.py

# Test with sample data
python test_rag_mvp.py --with-samples
```

## Troubleshooting

### Documents not loading
- Check file encoding (should be UTF-8)
- Verify file permissions
- Check for very large files (chunk if > 1MB)

### No results in queries
- Load sample data first: `python scripts/load_documents.py --sample`
- Verify documents were loaded: check logs
- Try more specific queries

### RAG not available in AVA
- Install dependencies: `pip install chromadb sentence-transformers`
- Restart Magnus dashboard
- Check logs for RAG initialization message

## Example Documents

See [RAG_IMPLEMENTATION_NOW.md](../RAG_IMPLEMENTATION_NOW.md) for:
- Example document structures
- Sample financial content
- Integration patterns
- Advanced usage

---

**Note:** All documents are stored locally. Nothing is sent to external services. Your trading knowledge stays private and secure.
