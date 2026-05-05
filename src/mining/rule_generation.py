"""
Tiện ích để sinh các luật kết hợp từ itemset phổ biến
"""

from typing import List, Dict, Tuple, Set
from itertools import combinations
from math import log


class AssociationRule:
    """Đại diện cho một luật kết hợp"""
    
    def __init__(self, antecedent: Tuple[str, ...], 
                 consequent: Tuple[str, ...],
                 support: int, 
                 confidence: float, 
                 lift: float,
                 total_transactions: int = None):
        """
        Khởi tạo luật kết hợp
        
        Args:
            antecedent: Tập hợp các item ở phía trái
            consequent: Tập hợp các item ở phía phải
            support: Số lượng support của toàn bộ itemset
            confidence: Độ tin cậy của luật
            lift: Chỉ số lift
            total_transactions: Tổng số giao dịch (để tính support percentage)
        """
        self.antecedent = antecedent
        self.consequent = consequent
        self.support = support
        self.confidence = confidence
        self.lift = lift
        self.total_transactions = total_transactions
    
    @property
    def support_percentage(self) -> float:
        """Tính phần trăm support"""
        if self.total_transactions is None or self.total_transactions == 0:
            return 0.0
        return self.support / self.total_transactions
    
    def __str__(self):
        """Biểu diễn chuỗi"""
        antecedent_str = ', '.join(self.antecedent)
        consequent_str = ', '.join(self.consequent)
        return (f"{{{antecedent_str}}} => {{{consequent_str}}}\n"
                f"  Support: {self.support} ({self.support_percentage:.2%}), "
                f"Confidence: {self.confidence:.4f}, Lift: {self.lift:.4f}")
    
    def __repr__(self):
        """Biểu diễn chi tiết"""
        return (f"AssociationRule(antecedent={self.antecedent}, "
                f"consequent={self.consequent}, support={self.support}, "
                f"confidence={self.confidence:.4f}, lift={self.lift:.4f})")
    
    def to_dict(self) -> Dict:
        """Chuyển đổi thành từ điển"""
        return {
            'antecedent': self.antecedent,
            'consequent': self.consequent,
            'support': self.support,
            'support_percentage': self.support_percentage,
            'confidence': self.confidence,
            'lift': self.lift
        }


def generate_association_rules(
        frequent_itemsets: Dict[int, List[Tuple[str, ...]]],
        support_counts: Dict[Tuple[str, ...], int],
        min_confidence: float,
        total_transactions: int = None) -> List[AssociationRule]:
    """
    Sinh các luật kết hợp từ các itemset phổ biến
    
    Args:
        frequent_itemsets: Từ điển {kích_thước: [itemsets]}
        support_counts: Từ điển {itemset: support_count}
        min_confidence: Độ tin cậy tối thiểu
        total_transactions: Tổng số giao dịch
        
    Returns:
        Danh sách các luật kết hợp
    """
    rules = []
    
    # Chỉ xử lý các itemset có kích thước >= 2
    for itemset_size in frequent_itemsets:
        if itemset_size < 2:
            continue
        
        for itemset in frequent_itemsets[itemset_size]:
            itemset_support = support_counts[itemset]
            
            # Sinh tất cả các cặp antecedent/consequent có thể
            for antecedent_size in range(1, itemset_size):
                for antecedent_items in combinations(itemset, antecedent_size):
                    antecedent = tuple(sorted(antecedent_items))
                    consequent = tuple(sorted(set(itemset) - set(antecedent)))
                    
                    if not consequent:
                        continue
                    
                    antecedent_support = support_counts.get(antecedent, 0)
                    consequent_support = support_counts.get(consequent, 0)
                    
                    # Cả antecedent và consequent phải có trong itemsets phổ biến
                    if antecedent_support == 0 or consequent_support == 0:
                        continue
                    
                    # Tính toán các chỉ số
                    # Lift = P(A∪B) / (P(A) * P(B)) = support(A∪B) * total_transactions / (support(A) * support(B))
                    confidence = itemset_support / antecedent_support
                    lift = (itemset_support * total_transactions) / (antecedent_support * consequent_support)
                    
                    # Chỉ giữ lại các luật thỏa mãn min_confidence
                    if confidence >= min_confidence:
                        rule = AssociationRule(
                            antecedent=antecedent,
                            consequent=consequent,
                            support=itemset_support,
                            confidence=confidence,
                            lift=lift,
                            total_transactions=total_transactions
                        )
                        rules.append(rule)
    
    return rules


def filter_rules(rules: List[AssociationRule], 
                min_confidence: float = None,
                min_lift: float = None,
                min_support: float = None) -> List[AssociationRule]:
    """
    Lọc các luật kết hợp theo các tiêu chí
    
    Args:
        rules: Danh sách các luật
        min_confidence: Độ tin cậy tối thiểu
        min_lift: Chỉ số lift tối thiểu
        min_support: Phần trăm support tối thiểu
        
    Returns:
        Danh sách các luật sau khi lọc
    """
    filtered = rules
    
    if min_confidence is not None:
        filtered = [r for r in filtered if r.confidence >= min_confidence]
    
    if min_lift is not None:
        filtered = [r for r in filtered if r.lift >= min_lift]
    
    if min_support is not None:
        filtered = [r for r in filtered if r.support_percentage >= min_support]
    
    return filtered


def sort_rules(rules: List[AssociationRule],
              key: str = 'confidence',
              reverse: bool = True) -> List[AssociationRule]:
    """
    Sắp xếp các luật kết hợp
    
    Args:
        rules: Danh sách các luật
        key: Khóa để sắp xếp ('confidence', 'lift', 'support')
        reverse: Sắp xếp giảm dần hay tăng dần
        
    Returns:
        Danh sách các luật sau khi sắp xếp
    """
    if key == 'confidence':
        return sorted(rules, key=lambda r: r.confidence, reverse=reverse)
    elif key == 'lift':
        return sorted(rules, key=lambda r: r.lift, reverse=reverse)
    elif key == 'support':
        return sorted(rules, key=lambda r: r.support, reverse=reverse)
    else:
        return rules


def print_rules(rules: List[AssociationRule], limit: int = None) -> str:
    """
    Tạo chuỗi văn bản để in các luật
    
    Args:
        rules: Danh sách các luật
        limit: Giới hạn số luật để in (None = in hết)
        
    Returns:
        Chuỗi văn bản chứa các luật
    """
    lines = []
    lines.append("="*80)
    lines.append("CÁC LUẬT KẾT HỢP")
    lines.append("="*80)
    
    if not rules:
        lines.append("Không tìm thấy luật nào")
    else:
        display_count = limit if limit is not None else len(rules)
        for i, rule in enumerate(rules[:display_count], 1):
            lines.append(f"\nLuật {i}:")
            antecedent_str = ', '.join(rule.antecedent)
            consequent_str = ', '.join(rule.consequent)
            lines.append(f"  {{{antecedent_str}}} => {{{consequent_str}}}")
            lines.append(f"  Support: {rule.support} ({rule.support_percentage:.2%})")
            lines.append(f"  Confidence: {rule.confidence:.4f}")
            lines.append(f"  Lift: {rule.lift:.4f}")
        
        if limit is not None and len(rules) > limit:
            lines.append(f"\n... và {len(rules) - limit} luật khác")
    
    lines.append("\n" + "="*80)
    lines.append(f"Tổng: {len(rules)} luật")
    lines.append("="*80)
    
    return '\n'.join(lines)


def get_rules_summary(rules: List[AssociationRule]) -> Dict:
    """
    Lấy tóm tắt thống kê về các luật
    
    Args:
        rules: Danh sách các luật
        
    Returns:
        Từ điển chứa các thống kê
    """
    if not rules:
        return {
            'total_rules': 0,
            'avg_confidence': 0.0,
            'avg_lift': 0.0,
            'max_confidence': 0.0,
            'max_lift': 0.0,
            'min_confidence': 0.0,
            'min_lift': 0.0
        }
    
    confidences = [r.confidence for r in rules]
    lifts = [r.lift for r in rules]
    
    return {
        'total_rules': len(rules),
        'avg_confidence': sum(confidences) / len(confidences),
        'avg_lift': sum(lifts) / len(lifts),
        'max_confidence': max(confidences),
        'max_lift': max(lifts),
        'min_confidence': min(confidences),
        'min_lift': min(lifts)
    }


def export_rules_to_dict(rules: List[AssociationRule]) -> List[Dict]:
    """
    Xuất các luật thành danh sách từ điển
    
    Args:
        rules: Danh sách các luật
        
    Returns:
        Danh sách các từ điển
    """
    return [rule.to_dict() for rule in rules]
