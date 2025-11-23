## Multi-Modal Analysis System

Complete guide for analyzing charts, images, and PDF documents with AVA.

---

## Overview

The multi-modal system enables AVA to understand visual and document-based information:

- **Vision Analysis**: Chart pattern recognition, earnings screenshots, option chains
- **PDF Parsing**: Earnings reports, financial statements, research papers
- **Multi-Format Support**: JPG, PNG, PDF, with automatic format detection

### Supported Models

**Vision Models:**
- GPT-4 Vision / GPT-4o (OpenAI) - Best overall
- Claude 3 Opus/Sonnet (Anthropic) - Strong vision capabilities
- Gemini Pro Vision (Google) - Good for free tier
- LLaVA (Local/Ollama) - Free, runs offline

**PDF Parsing:**
- PyMuPDF - High quality text extraction
- pdfplumber - Advanced table extraction
- Camelot - Specialized financial tables
- PyPDF2 - Basic fallback

---

## Quick Start

### Installation

```bash
# Vision Analysis
pip install openai anthropic google-generativeai pillow

# PDF Parsing
pip install PyPDF2 pdfplumber PyMuPDF camelot-py[cv]

# Optional: Local vision model
ollama pull llava
```

### API Keys

Add to `.env`:
```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
```

---

## Chart Analysis

### Basic Usage

```python
from src.multimodal import analyze_chart_image

# Analyze any stock chart
result = analyze_chart_image("chart.png", ticker="AAPL")

print(result['analysis'])
# Technical analysis with support/resistance levels, patterns, signals
```

### What It Identifies

**1. Trend Analysis**
- Direction: Uptrend, downtrend, sideways
- Strength: Weak, moderate, strong
- Reversal signals

**2. Support & Resistance**
- Key price levels
- Breakout/breakdown zones
- Historical pivot points

**3. Technical Indicators** (if visible)
- Moving averages (position, crossovers)
- RSI levels (overbought/oversold)
- MACD signals
- Volume patterns

**4. Chart Patterns**
- Head & shoulders
- Double top/bottom
- Triangles, flags, pennants
- Wedges, channels

**5. Trading Signals**
- Entry points (long/short)
- Stop loss levels
- Profit targets
- Risk/reward ratios

### Example Output

```json
{
  "status": "success",
  "analysis": "The AAPL chart shows a strong uptrend with price trading above the 50-day and 200-day moving averages.  Support is identified at $170 (previous resistance turned support) and $165 (50-day MA). Resistance levels are $180 (current price) and $185 (previous high).  RSI at 62 suggests moderate bullish momentum without being overbought. MACD shows positive crossover with expanding histogram. An ascending triangle pattern is forming with breakout potential above $180. Entry: $178-179 on pullback. Stop: Below $170. Target: $190-195 (measured move from pattern). Bullish bias with 7/10 confidence.",
  "model_used": "gpt-4o",
  "structured_analysis": {
    "ticker": "AAPL",
    "trend": "uptrend",
    "sentiment": "bullish",
    "confidence": 7
  }
}
```

---

## Earnings Report Analysis

### Screenshot Analysis

```python
from src.multimodal import analyze_earnings_screenshot

# Analyze earnings report screenshot
result = analyze_earnings_screenshot("earnings_screenshot.png", ticker="AAPL")

print(result['analysis'])
```

### PDF Analysis

```python
from src.multimodal import parse_earnings_pdf

# Parse earnings report PDF
result = parse_earnings_pdf("Q4_2024_Earnings.pdf", ticker="AAPL")

earnings_data = result['earnings_data']
print(f"Revenue: {earnings_data['revenue']}")
print(f"EPS: {earnings_data['eps']}")
print(f"Guidance: {earnings_data['guidance']}")
```

### Extracted Data

- **Revenue**: Actual vs expected
- **EPS**: Actual vs expected, beat/miss
- **Margins**: Gross, operating, net
- **Guidance**: Forward expectations
- **YoY Growth**: Revenue, profit, metrics
- **Key Metrics**: Users, ARR, churn, etc.

---

## Option Chain Analysis

```python
from src.multimodal import VisionAnalyzer, AnalysisType

analyzer = VisionAnalyzer()

result = analyzer.analyze_option_chain(
    "option_chain_screenshot.png",
    ticker="TSLA"
)

print(result['analysis'])
```

### Identified Elements

- **Unusual Activity**: High volume strikes, large OI
- **Key Strikes**: Max pain, highest put/call OI
- **IV Analysis**: Levels, skew, volatility smile
- **Greeks**: Delta, gamma, theta concentrations
- **Opportunities**: Best strikes for strategies

---

## PDF Parsing

### General Document

```python
from src.multimodal import parse_pdf_document

result = parse_pdf_document("research_report.pdf")

print(f"Pages: {result['page_count']}")
print(f"Tables found: {len(result['tables'])}")
print(result['text'][:500])  # First 500 chars
```

### Financial Statements

```python
from src.multimodal import PDFParser

parser = PDFParser()

result = parser.parse_financial_statement(
    "10K_financials.pdf",
    statement_type="income_statement"
)

financial_data = result['financial_data']
```

### Table Extraction

All financial tables automatically extracted:

```python
for table in result['tables']:
    print(f"Table {table['table_number']} on page {table['page']}")
    print(f"Headers: {table['headers']}")
    print(f"Rows: {len(table['data'])}")
```

---

## Advanced Usage

### Custom Analysis Prompts

```python
analyzer = VisionAnalyzer()

custom_prompt = """
Analyze this chart specifically for:
1. Fibonacci retracement levels
2. Elliott Wave patterns
3. Volume profile (point of control, value area)
4. Order flow imbalances
"""

result = analyzer.analyze_image(
    "chart.png",
    custom_prompt=custom_prompt
)
```

### Model Selection

```python
from src.multimodal import VisionModel

# Use specific model
result = analyzer.analyze_chart(
    "chart.png",
    ticker="NVDA"
)

# GPT-4 Vision is used by default

# Use Claude for comparison
result_claude = analyzer.analyze_image(
    "chart.png",
    model=VisionModel.CLAUDE_OPUS
)

# Use local LLaVA (free)
result_local = analyzer.analyze_image(
    "chart.png",
    model=VisionModel.LLAVA
)
```

### Extract Images from PDF

```python
parser = PDFParser()

result = parser.parse_pdf(
    "presentation.pdf",
    extract_images=True
)

# Save extracted images
for img in result['images']:
    with open(f"page_{img['page']}_img_{img['image_index']}.{img['format']}", 'wb') as f:
        f.write(img['image_data'])
```

---

## Integration with AVA

### Chat Command

In AVA chatbot:
```
User: "Analyze this chart [uploads chart.png]"
AVA: [Uses vision analyzer] "I see a bullish cup and handle pattern forming..."
```

### File Upload Component

```python
import streamlit as st
from src.multimodal import analyze_chart_image

uploaded_file = st.file_uploader("Upload chart", type=['png', 'jpg'])

if uploaded_file:
    # Save temporarily
    with open("temp_chart.png", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Analyze
    result = analyze_chart_image("temp_chart.png")

    st.markdown(f"**Analysis**: {result['analysis']}")
```

---

## Use Cases

### 1. Daily Chart Review

```python
# Analyze watchlist charts daily
watchlist = ["AAPL", "TSLA", "NVDA", "AMZN"]

for ticker in watchlist:
    chart_path = f"charts/{ticker}_daily.png"
    result = analyze_chart_image(chart_path, ticker=ticker)

    if result['structured_analysis']['sentiment'] == 'bullish':
        print(f"{ticker}: Bullish signal - {result['analysis'][:200]}")
```

### 2. Earnings Season Scanner

```python
# Scan all earnings reports
import glob

for pdf_file in glob.glob("earnings_reports/*.pdf"):
    ticker = extract_ticker_from_filename(pdf_file)

    result = parse_earnings_pdf(pdf_file, ticker=ticker)

    earnings = result['earnings_data']

    if earnings['eps'] and 'beat' in str(earnings['eps']).lower():
        print(f"{ticker} beat earnings: {earnings['eps']}")
```

### 3. Research Automation

```python
# Parse research reports
result = parse_pdf_document("analyst_report.pdf")

# Use LLM to summarize
from src.services.llm_service import LLMService

llm = LLMService()
summary = llm.generate(f"Summarize this research report: {result['text'][:4000]}")

print(summary)
```

---

## Performance & Costs

### Vision Model Costs (per image)

| Model | Cost | Speed | Quality |
|-------|------|-------|---------|
| GPT-4o | $0.01 | Fast | Excellent |
| GPT-4 Vision | $0.02 | Medium | Excellent |
| Claude Opus | $0.015 | Fast | Excellent |
| Claude Sonnet | $0.003 | Fast | Very Good |
| Gemini Pro | Free* | Fast | Good |
| LLaVA | Free | Medium | Good |

*Free tier: 15 requests/min

### PDF Parsing

**Free** - All PDF parsing libraries are free and run locally

### Optimization Tips

1. **Use local LLaVA for batch processing**
   ```python
   analyzer = VisionAnalyzer(default_model=VisionModel.LLAVA)
   ```

2. **Cache results**
   ```python
   @st.cache_data
   def cached_analysis(image_path):
       return analyze_chart_image(image_path)
   ```

3. **Compress images** before sending
   ```python
   from PIL import Image

   img = Image.open("large_chart.png")
   img.thumbnail((1024, 1024))
   img.save("compressed_chart.png")
   ```

---

## Troubleshooting

### "No vision models available"

✅ **Install OpenAI, Anthropic, or Google SDKs**
✅ **Set API keys in `.env`**
✅ **For local: `ollama pull llava`**

### "PDF parsing failed"

✅ **Install: `pip install PyPDF2 pdfplumber PyMuPDF`**
✅ **Check PDF is not password-protected**
✅ **Try different backend (PyMuPDF usually best)**

### Poor chart analysis quality

✅ **Use higher resolution images (min 800x600)**
✅ **Ensure chart is clearly visible**
✅ **Try GPT-4o or Claude Opus for best results**
✅ **Provide ticker context for better analysis**

### Table extraction not working

✅ **Install Camelot: `pip install camelot-py[cv]`**
✅ **Ensure PDF has actual tables (not images of tables)**
✅ **Try pdfplumber as alternative**

---

## API Reference

### VisionAnalyzer

```python
class VisionAnalyzer:
    def __init__(self, default_model: VisionModel = VisionModel.GPT4O)

    def analyze_image(
        image_path: str,
        analysis_type: AnalysisType = AnalysisType.GENERAL_IMAGE,
        custom_prompt: Optional[str] = None,
        model: Optional[VisionModel] = None
    ) -> Dict[str, Any]

    def analyze_chart(
        image_path: str,
        ticker: Optional[str] = None
    ) -> Dict[str, Any]

    def analyze_earnings_report(
        image_path: str,
        ticker: Optional[str] = None
    ) -> Dict[str, Any]

    def analyze_option_chain(
        image_path: str,
        ticker: Optional[str] = None
    ) -> Dict[str, Any]
```

### PDFParser

```python
class PDFParser:
    def __init__(self)

    def parse_pdf(
        pdf_path: str,
        document_type: DocumentType = DocumentType.GENERAL,
        extract_tables: bool = True,
        extract_images: bool = False
    ) -> Dict[str, Any]

    def parse_earnings_report(
        pdf_path: str,
        ticker: Optional[str] = None
    ) -> Dict[str, Any]

    def parse_financial_statement(
        pdf_path: str,
        statement_type: str = "income_statement"
    ) -> Dict[str, Any]
```

---

## Future Enhancements

### Planned Features

1. **Video Analysis**
   - Earnings call transcripts with sentiment
   - CNBC clip analysis
   - Trading video tutorials

2. **Audio Processing**
   - Earnings call audio analysis
   - Podcast episode summaries
   - Voice memo transcription

3. **Real-Time Chart Analysis**
   - Screenshot TradingView/ThinkOrSwim
   - Auto-analyze every 5 minutes
   - Pattern alerts

4. **Batch Processing**
   - Analyze 100+ charts in parallel
   - Daily watchlist automation
   - Earnings season scanner

5. **Interactive Analysis**
   - "What if price breaks $180?"
   - Draw support/resistance requests
   - Scenario modeling

---

## Best Practices

### 1. Image Quality
- Minimum 800x600 resolution
- Clear, well-lit screenshots
- Remove unnecessary UI elements
- Crop to relevant area

### 2. Model Selection
- **GPT-4o**: Best all-around, recommended
- **Claude Opus**: Strong alternative, good for complex analysis
- **Gemini Pro**: Free tier testing
- **LLaVA**: Batch processing, cost-sensitive

### 3. Prompt Engineering
- Be specific about what you want
- Provide ticker context when available
- Request specific price levels
- Ask for confidence scores

### 4. Error Handling
- Implement fallback models
- Cache successful analyses
- Validate image format before sending
- Set reasonable timeouts

### 5. Cost Management
- Use caching aggressively
- Batch similar requests
- Compress images before uploading
- Use local models for repetitive tasks

---

**Multi-Modal System v1.0** • Magnus Trading Platform
