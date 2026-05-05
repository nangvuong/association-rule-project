"""
Data cleaning module for transaction data
"""

import pandas as pd
from typing import Tuple


class DataCleaner:
    """Clean raw transaction data through 5-step process"""
    
    def __init__(self):
        """Initialize DataCleaner"""
        self.cleaning_log = []
    
    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all cleaning steps
        
        Args:
            df: Raw input DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        print(f"Starting data cleaning...")
        print(f"Original dataset size: {len(df)}\n")
        
        df_clean = df.copy()
        
        # Step 1: Remove rows with missing Invoice, Description, or Customer ID
        df_clean = self._remove_missing_values(df_clean)
        
        # Step 2: Remove cancelled transactions and negative quantities
        df_clean = self._remove_cancelled_transactions(df_clean)
        
        # Step 3: Remove non-positive prices
        df_clean = self._remove_invalid_prices(df_clean)
        
        # Step 4: Remove duplicates
        df_clean = self._remove_duplicates(df_clean)
        
        # Step 5: Clean descriptions
        df_clean = self._clean_descriptions(df_clean)
        
        print(f"\n{'='*60}")
        print(f"Data Cleaning Completed")
        print(f"{'='*60}")
        print(f"Final cleaned dataset size: {len(df_clean)}")
        print(f"Total rows removed: {len(df) - len(df_clean)} ({(len(df) - len(df_clean)) / len(df) * 100:.2f}%)")
        print(f"Unique invoices: {df_clean['Invoice'].nunique()}")
        print(f"Unique products: {df_clean['StockCode'].nunique()}")
        print(f"Unique customers: {df_clean['Customer ID'].nunique()}")
        print(f"{'='*60}\n")
        
        return df_clean
    
    def _remove_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove rows with missing Invoice, Description, or Customer ID"""
        print(f"Step 1: Removing rows with missing Invoice, Description, or Customer ID...")
        initial_len = len(df)
        df = df.dropna(subset=['Invoice', 'Description', 'Customer ID'])
        removed = initial_len - len(df)
        print(f"  Removed {removed} rows")
        self.cleaning_log.append(('missing_values', removed))
        return df
    
    def _remove_cancelled_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove cancelled transactions and negative quantities"""
        print(f"Step 2: Removing cancelled transactions and negative quantities...")
        initial_len = len(df)
        
        # Remove invoices starting with 'C' (cancelled)
        df = df[~df['Invoice'].astype(str).str.startswith('C')]
        # Remove negative or zero quantities
        df = df[df['Quantity'] > 0]
        
        removed = initial_len - len(df)
        print(f"  Removed {removed} rows")
        self.cleaning_log.append(('cancelled_transactions', removed))
        return df
    
    def _remove_invalid_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove non-positive prices"""
        print(f"Step 3: Removing non-positive prices...")
        initial_len = len(df)
        df = df[df['Price'] > 0]
        removed = initial_len - len(df)
        print(f"  Removed {removed} rows")
        self.cleaning_log.append(('invalid_prices', removed))
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate transactions"""
        print(f"Step 4: Removing duplicate transactions...")
        initial_len = len(df)
        df = df.drop_duplicates(subset=['Invoice', 'StockCode', 'Customer ID'], keep='first')
        removed = initial_len - len(df)
        print(f"  Removed {removed} rows")
        self.cleaning_log.append(('duplicates', removed))
        return df
    
    def _clean_descriptions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean product descriptions"""
        print(f"Step 5: Cleaning product descriptions...")
        initial_len = len(df)
        
        # Strip whitespace and remove empty descriptions
        df['Description'] = df['Description'].str.strip()
        df = df[df['Description'].str.len() > 0]
        
        removed = initial_len - len(df)
        print(f"  Removed {removed} rows")
        self.cleaning_log.append(('empty_descriptions', removed))
        return df
