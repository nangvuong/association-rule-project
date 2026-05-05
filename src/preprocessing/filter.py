"""
Rare item filtering module
"""

import pandas as pd
from typing import Tuple, List


class RareItemFilter:
    """Filter out rare items based on support thresholds"""
    
    def __init__(self, min_support_count: int = 50, min_support_percentage: float = 0.1):
        """
        Initialize RareItemFilter
        
        Args:
            min_support_count: Absolute threshold (items must appear at least this many times)
            min_support_percentage: Relative threshold (items must appear in at least this % of records)
        """
        self.min_support_count = min_support_count
        self.min_support_percentage = min_support_percentage
        self.threshold = None
        self.rare_items = None
        self.common_items = None
    
    def filter(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], List[str]]:
        """
        Filter rare items from dataset
        
        Args:
            df: Input DataFrame with 'Description' column
            
        Returns:
            Tuple of (filtered_dataframe, rare_items_list, common_items_list)
        """
        print("Calculating item frequency (support)...\n")
        
        # Calculate item frequency
        item_counts = df['Description'].value_counts()
        print(f"Total unique items before filtering: {len(item_counts)}")
        print(f"\nItem frequency statistics:")
        print(item_counts.describe())
        
        # Calculate thresholds
        min_count_relative = int(len(df) * (self.min_support_percentage / 100))
        self.threshold = max(self.min_support_count, min_count_relative)
        
        print(f"\n{'='*60}")
        print(f"Rare Item Filtering Configuration:")
        print(f"{'='*60}")
        print(f"Total records: {len(df)}")
        print(f"Absolute threshold: {self.min_support_count} occurrences")
        print(f"Relative threshold: {self.min_support_percentage}% = {min_count_relative} occurrences")
        print(f"Using threshold: {self.threshold} occurrences")
        
        # Identify rare and common items
        self.rare_items = item_counts[item_counts < self.threshold].index.tolist()
        self.common_items = item_counts[item_counts >= self.threshold].index.tolist()
        
        print(f"\n{'='*60}")
        print(f"Filtering Results:")
        print(f"{'='*60}")
        print(f"Rare items (frequency < {self.threshold}): {len(self.rare_items)}")
        print(f"Common items (frequency >= {self.threshold}): {len(self.common_items)}")
        print(f"Items to remove: {len(self.rare_items)} ({len(self.rare_items)/len(item_counts)*100:.2f}%)")
        
        # Display top rare and common items
        print(f"\nTop 10 most frequent items (KEEP):")
        print(item_counts.head(10))
        
        print(f"\nTop 10 rarest items (REMOVE):")
        print(item_counts.tail(10))
        
        # Filter dataset
        print(f"\n\nRemoving rare items...")
        initial_len = len(df)
        df_filtered = df[df['Description'].isin(self.common_items)].copy()
        removed_rows = initial_len - len(df_filtered)
        
        print(f"Records removed due to rare items: {removed_rows}")
        print(f"Percentage removed: {removed_rows/initial_len*100:.2f}%")
        
        print(f"\n{'='*60}")
        print(f"Dataset after removing rare items:")
        print(f"{'='*60}")
        print(f"Total records: {len(df_filtered)}")
        print(f"Unique invoices: {df_filtered['Invoice'].nunique()}")
        print(f"Unique products: {df_filtered['StockCode'].nunique()}")
        print(f"Unique customers: {df_filtered['Customer ID'].nunique()}")
        print(f"Unique items (descriptions): {df_filtered['Description'].nunique()}")
        print(f"{'='*60}\n")
        
        return df_filtered, self.rare_items, self.common_items
