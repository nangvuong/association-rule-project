"""
Transaction transformation module
"""

import pandas as pd
from typing import List, Set, Tuple


class TransactionTransformer:
    """Transform grouped data into transaction format"""
    
    def __init__(self, min_items: int = 2):
        """
        Initialize TransactionTransformer
        
        Args:
            min_items: Minimum number of items per transaction (filters smaller transactions)
        """
        self.min_items = min_items
    
    def transform_by_invoice(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Set[str]]]:
        """
        Transform data by grouping items by invoice
        
        Args:
            df: Input DataFrame with 'Invoice' and 'Description' columns
            
        Returns:
            Tuple of (transactions_dataframe, transaction_list)
        """
        print("Creating transaction format by grouping by Invoice...")
        
        # Group by invoice
        transactions = df.groupby('Invoice')['Description'].apply(list).reset_index()
        transactions.columns = ['Invoice', 'Items']
        
        print(f"Total transactions (invoices): {len(transactions)}")
        print(f"Average items per transaction: {transactions['Items'].apply(len).mean():.2f}")
        print(f"Min items per transaction: {transactions['Items'].apply(len).min()}")
        print(f"Max items per transaction: {transactions['Items'].apply(len).max()}")
        
        # Display sample transactions
        print(f"\nSample transactions:")
        for i in range(min(5, len(transactions))):
            items = transactions.iloc[i]['Items']
            print(f"Transaction {i+1} ({len(items)} items): {items[:5]}...")
        
        # Filter transactions with minimum items
        print(f"\n\nFiltering transactions with at least {self.min_items} items...")
        transactions_filtered = transactions[transactions['Items'].apply(len) >= self.min_items].copy()
        print(f"Transactions with {self.min_items}+ items: {len(transactions_filtered)}")
        
        # Create final transaction list (list of itemsets)
        transaction_list = [set(items) for items in transactions_filtered['Items']]
        
        print(f"\nSample itemsets:")
        for i in range(min(3, len(transaction_list))):
            print(f"  {transaction_list[i]}")
        
        return transactions_filtered, transaction_list
    
    def get_unique_items(self, transaction_list: List[Set[str]]) -> List[str]:
        """
        Get all unique items from transaction list
        
        Args:
            transaction_list: List of itemsets
            
        Returns:
            Sorted list of unique items
        """
        all_items = sorted(list(set().union(*transaction_list)))
        print(f"Total unique items: {len(all_items)}")
        return all_items
