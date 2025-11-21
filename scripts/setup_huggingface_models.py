"""
Setup HuggingFace Models for Sports Prediction

Downloads and caches all required models for offline use.
Run once to set up, then models will be cached locally.

Usage:
    python scripts/setup_huggingface_models.py

Author: AI Engineer
Created: 2025-11-15
"""

import os
import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'transformers',
        'sentence_transformers',
        'torch'
    ]

    missing = []

    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)

    if missing:
        logger.error(f"Missing packages: {', '.join(missing)}")
        logger.error("Install with: pip install -r requirements_huggingface.txt")
        return False

    return True


def download_sentence_transformers():
    """Download sentence transformer models"""
    from sentence_transformers import SentenceTransformer

    models = [
        {
            'name': 'all-MiniLM-L6-v2',
            'path': 'sentence-transformers/all-MiniLM-L6-v2',
            'description': 'Fast embeddings (14k sent/sec)',
            'size': '~90 MB'
        },
        {
            'name': 'all-mpnet-base-v2',
            'path': 'sentence-transformers/all-mpnet-base-v2',
            'description': 'High quality embeddings',
            'size': '~420 MB'
        }
    ]

    logger.info("\n" + "="*80)
    logger.info("DOWNLOADING SENTENCE TRANSFORMERS")
    logger.info("="*80)

    for model_info in models:
        logger.info(f"\nDownloading {model_info['name']}...")
        logger.info(f"  Description: {model_info['description']}")
        logger.info(f"  Size: {model_info['size']}")

        try:
            model = SentenceTransformer(model_info['path'])
            logger.info(f"  ✓ {model_info['name']} downloaded successfully")

            # Test inference
            test_text = "The Chiefs look dominant this season"
            embedding = model.encode(test_text, show_progress_bar=False)
            logger.info(f"  ✓ Test encoding successful (shape: {embedding.shape})")

        except Exception as e:
            logger.error(f"  ✗ Error downloading {model_info['name']}: {e}")
            return False

    return True


def download_sentiment_models():
    """Download sentiment analysis models"""
    from transformers import pipeline

    logger.info("\n" + "="*80)
    logger.info("DOWNLOADING SENTIMENT MODELS")
    logger.info("="*80)

    logger.info("\nDownloading DistilBERT sentiment model...")
    logger.info("  Description: Fast sentiment classifier")
    logger.info("  Size: ~260 MB")

    try:
        sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=-1  # CPU
        )

        # Test
        test_text = "The team is performing exceptionally well"
        result = sentiment_analyzer(test_text)
        logger.info(f"  ✓ DistilBERT downloaded successfully")
        logger.info(f"  ✓ Test sentiment: {result[0]}")

    except Exception as e:
        logger.error(f"  ✗ Error downloading DistilBERT: {e}")
        return False

    return True


def show_cache_location():
    """Show where models are cached"""
    cache_dir = os.path.expanduser('~/.cache/huggingface')

    logger.info("\n" + "="*80)
    logger.info("MODEL CACHE LOCATION")
    logger.info("="*80)
    logger.info(f"\nModels cached at: {cache_dir}")

    if os.path.exists(cache_dir):
        # Calculate total size
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(cache_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)

        size_mb = total_size / (1024 * 1024)
        logger.info(f"Total cache size: {size_mb:.1f} MB")
    else:
        logger.info("Cache directory will be created on first download")


def test_all_models():
    """Test all downloaded models"""
    logger.info("\n" + "="*80)
    logger.info("TESTING ALL MODELS")
    logger.info("="*80)

    from sentence_transformers import SentenceTransformer
    from transformers import pipeline
    import time

    # Test data
    test_headlines = [
        "Chiefs offense dominates with stellar performance",
        "Bills struggling with key injuries this week",
        "Mahomes confident heading into playoff game"
    ]

    # Test 1: Fast embeddings
    logger.info("\n1. Testing all-MiniLM-L6-v2 (fast)...")
    try:
        fast_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

        start = time.time()
        embeddings = fast_model.encode(test_headlines, show_progress_bar=False)
        elapsed = (time.time() - start) * 1000

        logger.info(f"   ✓ Encoded {len(test_headlines)} sentences in {elapsed:.1f}ms")
        logger.info(f"   ✓ Embedding shape: {embeddings.shape}")
        logger.info(f"   ✓ Speed: {len(test_headlines) / (elapsed/1000):.0f} sentences/sec")

    except Exception as e:
        logger.error(f"   ✗ Error: {e}")
        return False

    # Test 2: High quality embeddings
    logger.info("\n2. Testing all-mpnet-base-v2 (quality)...")
    try:
        quality_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

        start = time.time()
        embeddings = quality_model.encode(test_headlines, show_progress_bar=False)
        elapsed = (time.time() - start) * 1000

        logger.info(f"   ✓ Encoded {len(test_headlines)} sentences in {elapsed:.1f}ms")
        logger.info(f"   ✓ Embedding shape: {embeddings.shape}")

    except Exception as e:
        logger.error(f"   ✗ Error: {e}")
        return False

    # Test 3: Sentiment analysis
    logger.info("\n3. Testing DistilBERT sentiment...")
    try:
        sentiment = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=-1
        )

        results = sentiment(test_headlines)

        for headline, result in zip(test_headlines, results):
            logger.info(f"   '{headline[:50]}...'")
            logger.info(f"   → {result['label']} ({result['score']:.3f})")

        logger.info(f"   ✓ Sentiment analysis working")

    except Exception as e:
        logger.error(f"   ✗ Error: {e}")
        return False

    return True


def create_quick_reference():
    """Create quick reference guide"""
    reference = """
# HuggingFace Models Quick Reference

## Installed Models

### 1. all-MiniLM-L6-v2 (RECOMMENDED FOR PRODUCTION)
- **Speed:** 14,000 sentences/sec on CPU
- **Quality:** 84-85% STS-B accuracy
- **Size:** 90 MB
- **Use:** Real-time sentiment analysis, news embeddings

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
embedding = model.encode("Chiefs offense looking strong")
```

### 2. all-mpnet-base-v2 (HIGH QUALITY)
- **Speed:** 550 sentences/sec on CPU
- **Quality:** 87-88% STS-B accuracy
- **Size:** 420 MB
- **Use:** Offline batch processing, maximum quality

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
embeddings = model.encode(headlines)
```

### 3. DistilBERT Sentiment
- **Speed:** 125 sentences/sec on CPU
- **Quality:** 91% accuracy on SST-2
- **Size:** 260 MB
- **Use:** Binary sentiment classification

```python
from transformers import pipeline
sentiment = pipeline("sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english")
result = sentiment("Team playing well")
# {'label': 'POSITIVE', 'score': 0.95}
```

## Integration Examples

### Example 1: Analyze Team Sentiment

```python
from src.ai.sports_sentiment_embedder import SportsSentimentAnalyzer

analyzer = SportsSentimentAnalyzer()

headlines = [
    "Chiefs offense unstoppable",
    "Bills defense dominant",
    # ...
]

chiefs_sentiment = analyzer.analyze_headlines(headlines, "Chiefs")
print(f"Sentiment: {chiefs_sentiment['sentiment_score']:.3f}")
```

### Example 2: Compare Two Teams

```python
comparison = analyzer.compare_teams("Chiefs", "Bills", news_headlines)
print(f"Advantage: {comparison['advantage']:.3f}")
print(f"Winner: {comparison['winner']}")
```

### Example 3: Track Momentum

```python
headlines_by_date = {
    '2025-11-10': [...],
    '2025-11-11': [...],
    '2025-11-12': [...]
}

momentum = analyzer.analyze_momentum("Chiefs", headlines_by_date)
print(f"Momentum: {momentum['momentum']}")
print(f"Velocity: {momentum['velocity']:.3f}")
```

## Performance Benchmarks

| Model | Speed (CPU) | Quality | Size | Use Case |
|-------|-------------|---------|------|----------|
| MiniLM-L6-v2 | 14k sent/s | 84% | 90 MB | Production |
| mpnet-base-v2 | 550 sent/s | 88% | 420 MB | Batch |
| DistilBERT | 125 sent/s | 91% | 260 MB | Sentiment |

## Cache Location

Models are cached at: `~/.cache/huggingface/`

To clear cache: `rm -rf ~/.cache/huggingface/`

## Troubleshooting

### Import Error
```bash
pip install -r requirements_huggingface.txt
```

### Out of Memory
Use smaller batch sizes or switch to all-MiniLM-L6-v2

### Slow Performance
- Use all-MiniLM-L6-v2 instead of mpnet
- Enable GPU if available
- Reduce batch size

## Next Steps

1. Test sentiment analyzer:
   ```bash
   python src/ai/sports_sentiment_embedder.py
   ```

2. Integrate with Kalshi evaluator:
   - Add sentiment score to evaluation
   - Weight: 0.05-0.10 of total score

3. Monitor accuracy improvements:
   - Backtest on historical data
   - A/B test vs current system

## Resources

- HuggingFace Models: https://huggingface.co/models
- Sentence Transformers: https://www.sbert.net/
- Documentation: docs/ai/HUGGINGFACE_NFL_SPORTS_PREDICTION_RESEARCH.md
"""

    filepath = Path(__file__).parent.parent / 'docs' / 'ai' / 'HUGGINGFACE_QUICK_REFERENCE.md'
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w') as f:
        f.write(reference)

    logger.info(f"\n✓ Quick reference created: {filepath}")


def main():
    """Main setup function"""
    logger.info("\n" + "="*80)
    logger.info("HUGGINGFACE MODELS SETUP FOR NFL/NCAA PREDICTION")
    logger.info("="*80)

    # Check dependencies
    logger.info("\nChecking dependencies...")
    if not check_dependencies():
        logger.error("\n✗ Setup failed: missing dependencies")
        return 1

    logger.info("✓ All dependencies installed")

    # Show cache location
    show_cache_location()

    # Download models
    if not download_sentence_transformers():
        logger.error("\n✗ Setup failed: sentence transformers download error")
        return 1

    if not download_sentiment_models():
        logger.error("\n✗ Setup failed: sentiment models download error")
        return 1

    # Test models
    if not test_all_models():
        logger.error("\n✗ Setup failed: model testing error")
        return 1

    # Create reference
    create_quick_reference()

    # Success
    logger.info("\n" + "="*80)
    logger.info("✓ SETUP COMPLETE!")
    logger.info("="*80)
    logger.info("\nAll models downloaded and tested successfully.")
    logger.info("\nNext steps:")
    logger.info("  1. Test sentiment analyzer:")
    logger.info("     python src/ai/sports_sentiment_embedder.py")
    logger.info("  2. Read documentation:")
    logger.info("     docs/ai/HUGGINGFACE_NFL_SPORTS_PREDICTION_RESEARCH.md")
    logger.info("  3. Integrate with existing system:")
    logger.info("     src/ai/enhanced_kalshi_evaluator.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
