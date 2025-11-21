"""
Prediction Agent - Multi-Sector Prediction Markets System

A comprehensive prediction system for sports, politics, economics, and crypto markets.
Uses ensemble models combining XGBoost and LLM predictions with probability calibration.

Author: Python Pro
Created: 2025-11-09
"""

from .multi_sector_predictor import MultiSectorPredictor
from .ensemble import EnsembleModel
from .features import FeatureEngineering
from .sector_configs import SectorConfig, SECTOR_CONFIGS, MarketSector, detect_sector, get_sector_config
from .data_sources import DataSourceManager

__version__ = "1.0.0"

__all__ = [
    "MultiSectorPredictor",
    "EnsembleModel",
    "FeatureEngineering",
    "SectorConfig",
    "SECTOR_CONFIGS",
    "MarketSector",
    "detect_sector",
    "get_sector_config",
    "DataSourceManager",
]
