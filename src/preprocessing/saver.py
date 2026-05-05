"""
Data saving module
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from typing import List, Set, Dict


class DataSaver:
    """Save processed data in multiple formats"""
    
    def __init__(self, output_dir: Path):
        """
        Initialize DataSaver
        
        Args:
            output_dir: Directory to save processed files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.saved_files = []
    
    def save_all(self, 
                 df_clean: pd.DataFrame,
                 transactions_filtered: pd.DataFrame,
                 transaction_list: List[Set[str]],
                 onehot_matrix: np.ndarray,
                 onehot_df: pd.DataFrame,
                 item_to_idx: Dict[str, int],
                 all_items: List[str]) -> dict:
        """
        Save all processed data files
        
        Args:
            df_clean: Cleaned dataset
            transactions_filtered: Filtered transactions dataframe
            transaction_list: List of itemsets
            onehot_matrix: Binary numpy matrix
            onehot_df: One-hot dataframe
            item_to_idx: Item-to-index mapping
            all_items: List of all unique items
            
        Returns:
            Dictionary with file paths and statistics
        """
        print("Saving processed data...\n")
        
        # Save 1: Cleaned data (CSV)
        self._save_cleaned_data(df_clean)
        
        # Save 2: Transactions (CSV)
        self._save_transactions_csv(transactions_filtered)
        
        # Save 3: Transaction list (Pickle)
        self._save_transaction_list_pkl(transaction_list)
        
        # Save 4: Transaction list (Text)
        self._save_transaction_list_txt(transaction_list)
        
        # Save 5: One-hot matrix (CSV)
        self._save_onehot_csv(onehot_df)
        
        # Save 6: One-hot matrix (NumPy)
        self._save_onehot_npy(onehot_matrix)
        
        # Save 7: Item mapping (Pickle)
        self._save_item_mapping_pkl(item_to_idx)
        
        # Save 8: Item mapping (CSV)
        self._save_item_mapping_csv(item_to_idx)
        
        # Save 9: Summary statistics
        summary_stats = self._save_summary_stats(
            transactions_filtered, all_items, onehot_matrix
        )
        
        print(f"\n{'='*60}")
        print(f"Processing Summary:")
        print(f"{'='*60}")
        for metric, value in summary_stats.items():
            print(f"{metric:<40} {value}")
        print(f"{'='*60}")
        print(f"\nAll files saved to: {self.output_dir}")
        
        return summary_stats
    
    def _save_cleaned_data(self, df_clean: pd.DataFrame) -> Path:
        """Save cleaned dataset"""
        path = self.output_dir / 'cleaned_data.csv'
        df_clean.to_csv(path, index=False)
        print(f"✓ Saved cleaned data: {path}")
        self.saved_files.append(path)
        return path
    
    def _save_transactions_csv(self, transactions_filtered: pd.DataFrame) -> Path:
        """Save transactions as CSV"""
        path = self.output_dir / 'transactions.csv'
        transactions_filtered.to_csv(path, index=False)
        print(f"✓ Saved transactions (CSV): {path}")
        self.saved_files.append(path)
        return path
    
    def _save_transaction_list_pkl(self, transaction_list: List[Set[str]]) -> Path:
        """Save transaction list as pickle"""
        path = self.output_dir / 'transaction_list.pkl'
        with open(path, 'wb') as f:
            pickle.dump(transaction_list, f)
        print(f"✓ Saved transaction list (pickle): {path}")
        self.saved_files.append(path)
        return path
    
    def _save_transaction_list_txt(self, transaction_list: List[Set[str]]) -> Path:
        """Save transaction list as text file"""
        path = self.output_dir / 'transactions.txt'
        with open(path, 'w', encoding='utf-8') as f:
            for transaction in transaction_list:
                items = ','.join(sorted(transaction))
                f.write(items + '\n')
        print(f"✓ Saved transaction list (text): {path}")
        self.saved_files.append(path)
        return path
    
    def _save_onehot_csv(self, onehot_df: pd.DataFrame) -> Path:
        """Save one-hot matrix as CSV"""
        path = self.output_dir / 'onehot_matrix.csv'
        onehot_df.to_csv(path, index=False)
        print(f"✓ Saved one-hot matrix (CSV): {path}")
        self.saved_files.append(path)
        return path
    
    def _save_onehot_npy(self, onehot_matrix: np.ndarray) -> Path:
        """Save one-hot matrix as NumPy file"""
        path = self.output_dir / 'onehot_matrix.npy'
        np.save(path, onehot_matrix)
        print(f"✓ Saved one-hot matrix (NPY): {path}")
        self.saved_files.append(path)
        return path
    
    def _save_item_mapping_pkl(self, item_to_idx: Dict[str, int]) -> Path:
        """Save item mapping as pickle"""
        path = self.output_dir / 'item_mapping.pkl'
        with open(path, 'wb') as f:
            pickle.dump(item_to_idx, f)
        print(f"✓ Saved item mapping (pickle): {path}")
        self.saved_files.append(path)
        return path
    
    def _save_item_mapping_csv(self, item_to_idx: Dict[str, int]) -> Path:
        """Save item mapping as CSV"""
        path = self.output_dir / 'item_mapping.csv'
        mapping_df = pd.DataFrame(
            list(item_to_idx.items()),
            columns=['Item', 'ColumnIndex']
        ).sort_values('ColumnIndex')
        mapping_df.to_csv(path, index=False)
        print(f"✓ Saved item mapping (CSV): {path}")
        self.saved_files.append(path)
        return path
    
    def _save_summary_stats(self, 
                           transactions_filtered: pd.DataFrame,
                           all_items: List[str],
                           onehot_matrix: np.ndarray) -> dict:
        """Save summary statistics"""
        summary_stats = {
            'Total transactions': len(transactions_filtered),
            'Total unique items': len(all_items),
            'Onehot matrix shape': f"{onehot_matrix.shape[0]} x {onehot_matrix.shape[1]}",
            'Avg items per transaction': f"{transactions_filtered['Items'].apply(len).mean():.2f}",
            'Min items per transaction': int(transactions_filtered['Items'].apply(len).min()),
            'Max items per transaction': int(transactions_filtered['Items'].apply(len).max()),
            'Matrix sparsity': f"{(onehot_matrix == 0).sum() / onehot_matrix.size * 100:.2f}%",
        }
        
        summary_df = pd.DataFrame(
            list(summary_stats.items()),
            columns=['Metric', 'Value']
        )
        path = self.output_dir / 'processing_summary.csv'
        summary_df.to_csv(path, index=False)
        print(f"✓ Saved summary statistics: {path}")
        self.saved_files.append(path)
        
        return summary_stats
