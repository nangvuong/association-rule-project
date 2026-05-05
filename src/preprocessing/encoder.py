"""
One-hot encoding module
"""

import numpy as np
import pandas as pd
from typing import List, Set, Tuple, Dict


class OneHotEncoder:
    """Create one-hot encoded binary matrices from transaction data"""
    
    def __init__(self):
        """Initialize OneHotEncoder"""
        pass
    
    def create_matrix(self, transaction_list: List[Set[str]], all_items: List[str]) -> Tuple[np.ndarray, Dict[str, int]]:
        """
        Create one-hot encoded matrix from transactions
        
        Args:
            transaction_list: List of itemsets (each itemset is a set of item names)
            all_items: Sorted list of all unique items
            
        Returns:
            Tuple of (binary_matrix, item_to_index_dict)
                - binary_matrix: numpy array of shape (n_transactions, n_items) with dtype int
                - item_to_index_dict: dictionary mapping item names to column indices
        """
        print("Creating one-hot encoded matrix...\n")
        
        # Create binary matrix
        matrix = np.zeros((len(transaction_list), len(all_items)), dtype=np.int8)
        
        # Create item-to-index mapping
        item_to_idx = {item: idx for idx, item in enumerate(all_items)}
        
        # Fill matrix
        for trans_idx, transaction in enumerate(transaction_list):
            for item in transaction:
                item_idx = item_to_idx[item]
                matrix[trans_idx, item_idx] = 1
        
        print(f"Shape: {matrix.shape}")
        print(f"Sparsity: {(matrix == 0).sum() / matrix.size * 100:.2f}% zeros\n")
        
        return matrix, item_to_idx
    
    def to_dataframe(self, matrix: np.ndarray, all_items: List[str]) -> pd.DataFrame:
        """
        Convert one-hot matrix to DataFrame
        
        Args:
            matrix: Binary matrix from create_matrix()
            all_items: List of item names (column names)
            
        Returns:
            pandas DataFrame
        """
        return pd.DataFrame(matrix, columns=all_items)
    
    def get_statistics(self, matrix: np.ndarray, all_items: List[str]) -> dict:
        """
        Get statistics about item frequencies
        
        Args:
            matrix: Binary matrix from create_matrix()
            all_items: List of item names
            
        Returns:
            Dictionary with statistics
        """
        item_freq = matrix.sum(axis=0)
        
        stats = {
            'n_transactions': matrix.shape[0],
            'n_items': matrix.shape[1],
            'min_frequency': int(item_freq.min()),
            'max_frequency': int(item_freq.max()),
            'mean_frequency': float(item_freq.mean()),
            'median_frequency': float(np.median(item_freq)),
            'sparsity': (matrix == 0).sum() / matrix.size * 100,
        }
        
        print("Item frequency statistics:")
        print(f"Min frequency: {stats['min_frequency']}")
        print(f"Max frequency: {stats['max_frequency']}")
        print(f"Mean frequency: {stats['mean_frequency']:.2f}")
        print(f"Median frequency: {stats['median_frequency']:.2f}")
        
        # Top items
        print(f"\nTop 10 most frequent items:")
        top_indices = np.argsort(item_freq)[-10:][::-1]
        for i, idx in enumerate(top_indices, 1):
            print(f"  {i}. {all_items[idx]}: {item_freq[idx]}")
        
        print(f"\nTop 10 least frequent items:")
        bottom_indices = np.argsort(item_freq)[:10]
        for i, idx in enumerate(bottom_indices, 1):
            print(f"  {i}. {all_items[idx]}: {item_freq[idx]}")
        
        return stats
