"""
Frequent Itemset Mining Algorithms
"""

from .apriori import Apriori
from .hash_tree import HashTree

try:
    from .fp_growth import FPGrowth
except ImportError:
    FPGrowth = None

__all__ = ['Apriori', 'HashTree']
if FPGrowth is not None:
    __all__.append('FPGrowth')
