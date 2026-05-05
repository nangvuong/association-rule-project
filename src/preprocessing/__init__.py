"""
Preprocessing module for Association Rule Mining

This module provides utilities to:
- Load and explore the Online Retail II dataset
- Clean raw transaction data
- Filter rare items
- Transform to transaction format
- Generate one-hot encoded matrices
- Save processed data in multiple formats
"""

from .loader import DataLoader
from .cleaner import DataCleaner
from .filter import RareItemFilter
from .transformer import TransactionTransformer
from .encoder import OneHotEncoder
from .saver import DataSaver
from .pipeline import PreprocessingPipeline

__all__ = [
    'DataLoader',
    'DataCleaner',
    'RareItemFilter',
    'TransactionTransformer',
    'OneHotEncoder',
    'DataSaver',
    'PreprocessingPipeline',
]
