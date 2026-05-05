"""
Main preprocessing pipeline orchestrator
"""

from pathlib import Path
import pandas as pd

from .loader import DataLoader
from .cleaner import DataCleaner
from .filter import RareItemFilter
from .transformer import TransactionTransformer
from .encoder import OneHotEncoder
from .saver import DataSaver


class PreprocessingPipeline:
    """Orchestrate the entire preprocessing pipeline"""
    
    def __init__(self,
                 raw_data_path: Path = None,
                 output_dir: Path = None,
                 min_support_count: int = 50,
                 min_support_percentage: float = 0.1,
                 min_items_per_transaction: int = 2):
        """
        Initialize preprocessing pipeline
        
        Args:
            raw_data_path: Path to raw data file (if None, uses default UCI location)
            output_dir: Directory to save processed files (if None, uses data/processed)
            min_support_count: Absolute threshold for rare item filtering
            min_support_percentage: Relative threshold for rare item filtering (%)
            min_items_per_transaction: Minimum items per transaction (others are filtered)
        """
        # Default paths
        project_root = Path(__file__).parent.parent.parent
        self.raw_data_path = raw_data_path or project_root / 'data' / 'raw' / 'online_retail_II.xlsx'
        self.output_dir = output_dir or project_root / 'data' / 'processed'
        
        # Parameters
        self.min_support_count = min_support_count
        self.min_support_percentage = min_support_percentage
        self.min_items_per_transaction = min_items_per_transaction
        
        # Initialize components
        self.loader = DataLoader(self.raw_data_path)
        self.cleaner = DataCleaner()
        self.filter = RareItemFilter(min_support_count, min_support_percentage)
        self.transformer = TransactionTransformer(min_items_per_transaction)
        self.encoder = OneHotEncoder()
        self.saver = DataSaver(self.output_dir)
    
    def run(self) -> dict:
        """
        Run the complete preprocessing pipeline
        
        Returns:
            Dictionary with processing results and summary statistics
        """
        print("="*60)
        print("STARTING PREPROCESSING PIPELINE")
        print("="*60 + "\n")
        
        # Step 1: Load data
        print("STEP 1: Loading Data")
        print("-"*60)
        df = self.loader.load_data()
        self.loader.explore_dataset(df)
        print()
        
        # Step 2: Clean data
        print("STEP 2: Cleaning Data")
        print("-"*60)
        df_clean = self.cleaner.clean(df)
        print()
        
        # Step 3: Filter rare items
        print("STEP 3: Filtering Rare Items")
        print("-"*60)
        df_clean, rare_items, common_items = self.filter.filter(df_clean)
        print()
        
        # Step 4: Transform to transactions
        print("STEP 4: Transforming to Transaction Format")
        print("-"*60)
        transactions_filtered, transaction_list = self.transformer.transform_by_invoice(df_clean)
        print()
        
        # Step 5: Create one-hot encoding
        print("STEP 5: Creating One-Hot Encoding")
        print("-"*60)
        all_items = self.transformer.get_unique_items(transaction_list)
        onehot_matrix, item_to_idx = self.encoder.create_matrix(transaction_list, all_items)
        onehot_df = self.encoder.to_dataframe(onehot_matrix, all_items)
        encoder_stats = self.encoder.get_statistics(onehot_matrix, all_items)
        print()
        
        # Step 6: Save all files
        print("STEP 6: Saving Processed Data")
        print("-"*60)
        summary_stats = self.saver.save_all(
            df_clean,
            transactions_filtered,
            transaction_list,
            onehot_matrix,
            onehot_df,
            item_to_idx,
            all_items
        )
        
        print("\n" + "="*60)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("="*60)
        
        results = {
            'original_records': len(df),
            'cleaned_records': len(df_clean),
            'transactions': len(transactions_filtered),
            'unique_items': len(all_items),
            'rare_items_removed': len(rare_items),
            'output_directory': str(self.output_dir),
            'saved_files': [str(f) for f in self.saver.saved_files],
            'summary_stats': summary_stats,
        }
        
        return results


def run_pipeline(raw_data_path: Path = None,
                output_dir: Path = None,
                min_support_count: int = 50,
                min_support_percentage: float = 0.1,
                min_items_per_transaction: int = 2) -> dict:
    """
    Convenience function to run the preprocessing pipeline
    
    Args:
        raw_data_path: Path to raw data file
        output_dir: Directory to save processed files
        min_support_count: Absolute threshold for rare item filtering
        min_support_percentage: Relative threshold for rare item filtering (%)
        min_items_per_transaction: Minimum items per transaction
        
    Returns:
        Dictionary with processing results
    """
    pipeline = PreprocessingPipeline(
        raw_data_path=raw_data_path,
        output_dir=output_dir,
        min_support_count=min_support_count,
        min_support_percentage=min_support_percentage,
        min_items_per_transaction=min_items_per_transaction
    )
    return pipeline.run()
