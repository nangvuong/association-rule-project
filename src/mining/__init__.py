"""
Khai phá luật kết hợp - Quản lý itemset phổ biến và sinh luật
"""

from pathlib import Path
from typing import List, Set, Dict
import pickle


class DatasetLoader:
    """Nạp dữ liệu từ các định dạng khác nhau"""
    
    def __init__(self, processed_data_dir: Path):
        """
        Khởi tạo loader
        
        Args:
            processed_data_dir: Đường dẫn tới thư mục processed
        """
        self.processed_data_dir = Path(processed_data_dir)
    
    def load_transactions(self) -> List[Set[str]]:
        """
        Nạp các giao dịch từ tệp pickle (ưu tiên) hoặc tệp text
        
        Ưu tiên pickle vì tên item có thể chứa dấu phẩy (ví dụ: "KEY FOB , SHED"),
        khiến việc split theo ',' từ file text bị sai.
        
        Returns:
            Danh sách các tập hợp (mỗi tập hợp là một giao dịch)
        """
        # Ưu tiên dùng pickle để tránh vấn đề tên item có dấu phẩy
        pkl_file = self.processed_data_dir / 'transaction_list.pkl'
        if pkl_file.exists():
            with open(pkl_file, 'rb') as f:
                return pickle.load(f)
        
        # Fallback: đọc từ file text
        transactions_file = self.processed_data_dir / 'transactions.txt'
        if transactions_file.exists():
            transactions = []
            with open(transactions_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    # Phát hiện delimiter: nếu chứa '|' dùng '|', ngược lại dùng ','
                    if '|' in line:
                        items = line.split('|')
                    else:
                        items = line.split(',')
                    if items and items[0]:
                        transactions.append(set(item.strip() for item in items))
            return transactions
        
        raise FileNotFoundError(
            f"Không tìm thấy transaction_list.pkl hoặc transactions.txt trong: {self.processed_data_dir}"
        )
    
    def load_item_mapping(self, format='csv') -> Dict:
        """
        Nạp ánh xạ item
        
        Args:
            format: Định dạng ('csv' hoặc 'pkl')
            
        Returns:
            Từ điển ánh xạ
        """
        if format == 'csv':
            import pandas as pd
            mapping_file = self.processed_data_dir / 'item_mapping.csv'
            if mapping_file.exists():
                df = pd.read_csv(mapping_file)
                return dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
        
        elif format == 'pkl':
            mapping_file = self.processed_data_dir / 'item_mapping.pkl'
            if mapping_file.exists():
                with open(mapping_file, 'rb') as f:
                    return pickle.load(f)
        
        return {}
    
    def get_dataset_info(self) -> Dict:
        """
        Lấy thông tin về dataset
        
        Returns:
            Từ điển chứa thông tin
        """
        transactions = self.load_transactions()
        
        info = {
            'total_transactions': len(transactions),
            'unique_items': len(set(item for trans in transactions for item in trans)),
            'avg_transaction_size': sum(len(t) for t in transactions) / len(transactions) if transactions else 0
        }
        
        return info


__all__ = ['DatasetLoader']
