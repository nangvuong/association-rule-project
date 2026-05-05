"""
Lớp và tiện ích để quản lý itemset phổ biến
"""

from typing import Set, Tuple, Dict, List
from dataclasses import dataclass


@dataclass
class FrequentItemset:
    """Đại diện cho một itemset phổ biến với thông tin hỗ trợ"""
    itemset: Tuple[str, ...]
    support_count: int
    support_percentage: float = 0.0
    
    def __hash__(self):
        """Cho phép dùng trong các cấu trúc dữ liệu dạng tập hợp"""
        return hash(self.itemset)
    
    def __eq__(self, other):
        """So sánh hai itemset"""
        if isinstance(other, FrequentItemset):
            return self.itemset == other.itemset
        return False
    
    def __str__(self):
        """Biểu diễn chuỗi"""
        return f"{{{', '.join(self.itemset)}}} (support: {self.support_count}, {self.support_percentage:.2%})"
    
    def __repr__(self):
        """Biểu diễn chi tiết"""
        return f"FrequentItemset(itemset={self.itemset}, support_count={self.support_count}, support_percentage={self.support_percentage:.2%})"


class FrequentItemsetManager:
    """Quản lý tập hợp các itemset phổ biến"""
    
    def __init__(self):
        """Khởi tạo trình quản lý"""
        self.itemsets: Dict[int, List[Tuple[str, ...]]] = {}  # {kích_thước: [itemsets]}
        self.support_counts: Dict[Tuple[str, ...], int] = {}   # {itemset: support_count}
        self.total_transactions = 0
    
    def add_itemset(self, itemset: Tuple[str, ...], support_count: int):
        """
        Thêm một itemset phổ biến
        
        Args:
            itemset: Bộ (tuple) các item
            support_count: Số lượng support
        """
        size = len(itemset)
        if size not in self.itemsets:
            self.itemsets[size] = []
        
        self.itemsets[size].append(itemset)
        self.support_counts[itemset] = support_count
    
    def get_itemsets_by_size(self, size: int) -> List[Tuple[str, ...]]:
        """
        Lấy danh sách các itemset theo kích thước
        
        Args:
            size: Kích thước của itemset (số lượng item)
            
        Returns:
            Danh sách các itemset với kích thước yêu cầu
        """
        return self.itemsets.get(size, [])
    
    def get_all_itemsets(self) -> List[Tuple[str, ...]]:
        """
        Lấy tất cả các itemset phổ biến
        
        Returns:
            Danh sách tất cả các itemset
        """
        result = []
        for size in sorted(self.itemsets.keys()):
            result.extend(self.itemsets[size])
        return result
    
    def get_support(self, itemset: Tuple[str, ...]) -> int:
        """
        Lấy giá trị support của một itemset
        
        Args:
            itemset: Bộ các item
            
        Returns:
            Số lượng support (hoặc 0 nếu không tìm thấy)
        """
        return self.support_counts.get(itemset, 0)
    
    def get_support_percentage(self, itemset: Tuple[str, ...]) -> float:
        """
        Lấy phần trăm support của một itemset
        
        Args:
            itemset: Bộ các item
            
        Returns:
            Phần trăm support (0.0 nếu không tìm thấy)
        """
        if self.total_transactions == 0:
            return 0.0
        return self.get_support(itemset) / self.total_transactions
    
    def get_total_count(self) -> int:
        """
        Lấy tổng số itemset phổ biến
        
        Returns:
            Tổng số itemset
        """
        return sum(len(items) for items in self.itemsets.values())
    
    def get_stats(self) -> Dict:
        """
        Lấy thống kê về các itemset
        
        Returns:
            Từ điển chứa thống kê
        """
        stats = {
            'total_itemsets': self.get_total_count(),
            'total_transactions': self.total_transactions,
            'sizes': {}
        }
        
        for size in sorted(self.itemsets.keys()):
            stats['sizes'][size] = len(self.itemsets[size])
        
        return stats
    
    def to_list(self) -> List[FrequentItemset]:
        """
        Chuyển đổi thành danh sách các đối tượng FrequentItemset
        
        Returns:
            Danh sách các FrequentItemset
        """
        result = []
        for itemset in self.get_all_itemsets():
            support_count = self.get_support(itemset)
            support_pct = self.get_support_percentage(itemset)
            result.append(FrequentItemset(
                itemset=itemset,
                support_count=support_count,
                support_percentage=support_pct
            ))
        return result
    
    def __str__(self):
        """Biểu diễn chuỗi"""
        lines = []
        lines.append("="*70)
        lines.append("DANH SÁCH ITEMSET PHỔ BIẾN")
        lines.append("="*70)
        
        for size in sorted(self.itemsets.keys()):
            lines.append(f"\nKích thước {size} ({len(self.itemsets[size])} itemsets):")
            for itemset in self.itemsets[size]:
                support_count = self.get_support(itemset)
                support_pct = self.get_support_percentage(itemset)
                items_str = ', '.join(itemset)
                lines.append(f"  {{{items_str}}} - support: {support_count} ({support_pct:.2%})")
        
        lines.append("\n" + "="*70)
        lines.append(f"Tổng: {self.get_total_count()} itemsets")
        lines.append("="*70)
        
        return '\n'.join(lines)
