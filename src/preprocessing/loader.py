"""
Data loading module for Online Retail II dataset
"""

import pandas as pd
import urllib.request
from pathlib import Path
from typing import Tuple


class DataLoader:
    """Load the Online Retail II dataset from UCI repository or local storage"""
    
    UCI_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00502/online_retail_II.xlsx"
    
    def __init__(self, raw_data_path: Path = None):
        """
        Initialize DataLoader
        
        Args:
            raw_data_path: Path to raw data file. If None, uses default location
        """
        self.raw_data_path = raw_data_path or Path(__file__).parent.parent.parent / 'data' / 'raw' / 'online_retail_II.xlsx'
    
    def ensure_data_exists(self) -> Path:
        """
        Ensure raw data exists. Download if necessary.
        
        Returns:
            Path to the data file
        """
        if self.raw_data_path.exists():
            print(f"✓ Data found at {self.raw_data_path}")
            return self.raw_data_path
        
        # Download if not exists
        print(f"File not found at {self.raw_data_path}")
        print("Downloading from UCI Machine Learning Repository...")
        
        # Create parent directories
        self.raw_data_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            urllib.request.urlretrieve(self.UCI_URL, self.raw_data_path)
            print(f"✓ Downloaded successfully to {self.raw_data_path}\n")
            return self.raw_data_path
        except Exception as e:
            print(f"✗ Download failed: {e}")
            raise
    
    def load_data(self) -> pd.DataFrame:
        """
        Load the dataset
        
        Returns:
            DataFrame with columns: Transaction, Customer ID, Invoice, StockCode, 
                                  Description, Quantity, InvoiceDate, Price, Country
        """
        data_path = self.ensure_data_exists()
        
        print(f"Loading data from: {data_path}")
        df = pd.read_excel(data_path)
        
        print(f"\nDataset loaded successfully!")
        print(f"Shape: {df.shape}")
        print(f"\nColumn names and types:")
        print(df.dtypes)
        
        return df
    
    def explore_dataset(self, df: pd.DataFrame) -> dict:
        """
        Explore dataset structure and return basic statistics
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary with exploration statistics
        """
        stats = {
            'total_rows': df.shape[0],
            'total_columns': df.shape[1],
            'missing_values': df.isnull().sum().to_dict(),
            'unique_invoices': df['Invoice'].nunique(),
            'unique_products': df['StockCode'].nunique(),
            'unique_customers': df['Customer ID'].nunique(),
            'date_range': f"{df['InvoiceDate'].min()} to {df['InvoiceDate'].max()}",
        }
        
        print(f"\nDataset Exploration:")
        print(f"{'='*60}")
        print(f"Total records: {stats['total_rows']}")
        print(f"Total unique invoices: {stats['unique_invoices']}")
        print(f"Total unique products: {stats['unique_products']}")
        print(f"Total unique customers: {stats['unique_customers']}")
        print(f"Date range: {stats['date_range']}")
        
        print(f"\nMissing values:")
        print(df.isnull().sum())
        print(f"\nPercentage of missing values:")
        print((df.isnull().sum() / len(df) * 100).round(2))
        print(f"{'='*60}")
        
        return stats
