"""
Multi-Modal Analysis System
===========================

Enables AVA to analyze charts, images, and PDF documents.

Components:
- vision_analyzer: Chart and image analysis using vision models
- pdf_parser: PDF document parsing and understanding
- streamlit_multimodal: UI components for file upload and analysis

Capabilities:
- Technical chart pattern recognition
- Earnings report screenshot analysis
- PDF earnings report parsing
- Financial statement extraction
- Research report summarization

Quick Start (Vision):
--------------------
from src.multimodal import analyze_chart_image

result = analyze_chart_image("chart.png", ticker="AAPL")
print(result['analysis'])

Quick Start (PDF):
-----------------
from src.multimodal import parse_earnings_pdf

result = parse_earnings_pdf("earnings_report.pdf", ticker="AAPL")
print(result['earnings_data'])

Author: Magnus Trading Platform
Created: 2025-11-21
"""

from .vision_analyzer import (
    VisionAnalyzer,
    VisionModel,
    AnalysisType,
    analyze_chart_image,
    analyze_earnings_screenshot
)

from .pdf_parser import (
    PDFParser,
    DocumentType,
    parse_pdf_document,
    parse_earnings_pdf
)

__all__ = [
    # Vision Analysis
    'VisionAnalyzer',
    'VisionModel',
    'AnalysisType',
    'analyze_chart_image',
    'analyze_earnings_screenshot',

    # PDF Parsing
    'PDFParser',
    'DocumentType',
    'parse_pdf_document',
    'parse_earnings_pdf',
]

__version__ = '1.0.0'
