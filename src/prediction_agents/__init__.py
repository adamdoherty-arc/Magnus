"""
Sports Prediction Agents
========================

Multi-agent system for predicting sports game outcomes using machine learning.

Agents:
- NFLPredictor: NFL-specific prediction agent with EPA, DVOA, and Elo ratings
- NCAAPredictor: NCAA-specific prediction agent with conference-aware features

Usage:
    from src.prediction_agents import NFLPredictor, NCAAPredictor

    nfl = NFLPredictor()
    prediction = nfl.predict_winner("Kansas City Chiefs", "Buffalo Bills")
    # Returns: {'winner': 'Kansas City Chiefs', 'probability': 0.68, 'confidence': 'medium', ...}
"""

from .base_predictor import BaseSportsPredictor
from .nfl_predictor import NFLPredictor
from .ncaa_predictor import NCAAPredictor

__all__ = ['BaseSportsPredictor', 'NFLPredictor', 'NCAAPredictor']
