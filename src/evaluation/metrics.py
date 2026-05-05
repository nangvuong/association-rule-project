"""
Tính toán các chỉ số đánh giá cho khai phá luật kết hợp
"""

from typing import Dict, List, Tuple, Set


class SupportMetric:
    """Tính toán chỉ số Support"""
    
    @staticmethod
    def calculate(itemset: Tuple[str, ...], 
                  itemset_count: int,
                  total_transactions: int) -> float:
        """
        Tính Support của một itemset
        
        Args:
            itemset: Bộ các item
            itemset_count: Số giao dịch chứa itemset này
            total_transactions: Tổng số giao dịch
            
        Returns:
            Giá trị support (0.0 - 1.0)
        """
        if total_transactions == 0:
            return 0.0
        return itemset_count / total_transactions
    
    @staticmethod
    def calculate_percentage(itemset_count: int, 
                           total_transactions: int) -> float:
        """
        Tính Support dưới dạng phần trăm
        
        Args:
            itemset_count: Số giao dịch chứa itemset
            total_transactions: Tổng số giao dịch
            
        Returns:
            Giá trị support (0% - 100%)
        """
        return SupportMetric.calculate(None, itemset_count, total_transactions) * 100


class ConfidenceMetric:
    """Tính toán chỉ số Confidence"""
    
    @staticmethod
    def calculate(antecedent_consequent_count: int,
                  antecedent_count: int) -> float:
        """
        Tính Confidence của một luật: P(B|A) = P(A,B) / P(A)
        
        Args:
            antecedent_consequent_count: Số giao dịch chứa cả antecedent và consequent
            antecedent_count: Số giao dịch chứa antecedent
            
        Returns:
            Giá trị confidence (0.0 - 1.0)
        """
        if antecedent_count == 0:
            return 0.0
        return antecedent_consequent_count / antecedent_count


class LiftMetric:
    """Tính toán chỉ số Lift"""
    
    @staticmethod
    def calculate(antecedent_count: int,
                  consequent_count: int,
                  both_count: int,
                  total_transactions: int) -> float:
        """
        Tính Lift của một luật: Lift(A=>B) = P(A,B) / (P(A) * P(B))
        
        Ý nghĩa:
        - Lift > 1: A và B có quan hệ dương (xảy ra cùng nhau nhiều hơn độc lập)
        - Lift = 1: A và B độc lập
        - Lift < 1: A và B có quan hệ âm (xảy ra cùng nhau ít hơn độc lập)
        
        Args:
            antecedent_count: Số giao dịch chứa A
            consequent_count: Số giao dịch chứa B
            both_count: Số giao dịch chứa cả A và B
            total_transactions: Tổng số giao dịch
            
        Returns:
            Giá trị lift
        """
        if antecedent_count == 0 or consequent_count == 0 or total_transactions == 0:
            return 0.0
        
        prob_a = antecedent_count / total_transactions
        prob_b = consequent_count / total_transactions
        prob_ab = both_count / total_transactions
        
        expected_prob = prob_a * prob_b
        
        if expected_prob == 0:
            return 0.0
        
        return prob_ab / expected_prob


class LeverageMetric:
    """Tính toán chỉ số Leverage"""
    
    @staticmethod
    def calculate(antecedent_count: int,
                  consequent_count: int,
                  both_count: int,
                  total_transactions: int) -> float:
        """
        Tính Leverage của một luật: Leverage(A=>B) = P(A,B) - P(A)*P(B)
        
        Ý nghĩa: Độ chênh lệch giữa xác suất thực tế và xác suất độc lập
        
        Args:
            antecedent_count: Số giao dịch chứa A
            consequent_count: Số giao dịch chứa B
            both_count: Số giao dịch chứa cả A và B
            total_transactions: Tổng số giao dịch
            
        Returns:
            Giá trị leverage
        """
        if total_transactions == 0:
            return 0.0
        
        prob_a = antecedent_count / total_transactions
        prob_b = consequent_count / total_transactions
        prob_ab = both_count / total_transactions
        
        return prob_ab - (prob_a * prob_b)


class ConvictionMetric:
    """Tính toán chỉ số Conviction"""
    
    @staticmethod
    def calculate(antecedent_count: int,
                  consequent_count: int,
                  both_count: int,
                  total_transactions: int) -> float:
        """
        Tính Conviction của một luật: Conviction(A=>B) = (1 - P(B)) / (1 - P(A,B)/P(A))
        
        Ý nghĩa: Mức độ phụ thuộc của A vào B
        
        Args:
            antecedent_count: Số giao dịch chứa A
            consequent_count: Số giao dịch chứa B
            both_count: Số giao dịch chứa cả A và B
            total_transactions: Tổng số giao dịch
            
        Returns:
            Giá trị conviction
        """
        if antecedent_count == 0 or total_transactions == 0:
            return 0.0
        
        confidence = ConfidenceMetric.calculate(both_count, antecedent_count)
        prob_b = consequent_count / total_transactions
        
        denominator = 1 - confidence
        if denominator == 0:
            return float('inf')
        
        return (1 - prob_b) / denominator


def calculate_all_metrics(antecedent_support: int,
                         consequent_support: int,
                         combined_support: int,
                         total_transactions: int) -> Dict[str, float]:
    """
    Tính toán tất cả các chỉ số cho một luật
    
    Args:
        antecedent_support: Số lượng support của antecedent
        consequent_support: Số lượng support của consequent
        combined_support: Số lượng support của combined itemset
        total_transactions: Tổng số giao dịch
        
    Returns:
        Từ điển chứa tất cả các chỉ số
    """
    return {
        'support': SupportMetric.calculate(None, combined_support, total_transactions),
        'confidence': ConfidenceMetric.calculate(combined_support, antecedent_support),
        'lift': LiftMetric.calculate(antecedent_support, consequent_support, 
                                     combined_support, total_transactions),
        'leverage': LeverageMetric.calculate(antecedent_support, consequent_support,
                                            combined_support, total_transactions),
        'conviction': ConvictionMetric.calculate(antecedent_support, consequent_support,
                                                combined_support, total_transactions)
    }


class MetricsAnalyzer:
    """Lớp tổng hợp để phân tích các chỉ số"""
    
    def __init__(self, total_transactions: int):
        """
        Khởi tạo trình phân tích
        
        Args:
            total_transactions: Tổng số giao dịch
        """
        self.total_transactions = total_transactions
        self.metrics_list = []
    
    def add_rule_metrics(self, antecedent_support: int,
                        consequent_support: int,
                        combined_support: int) -> Dict[str, float]:
        """
        Thêm và tính toán chỉ số cho một luật
        
        Args:
            antecedent_support: Số lượng support của antecedent
            consequent_support: Số lượng support của consequent
            combined_support: Số lượng support của combined itemset
            
        Returns:
            Từ điển chỉ số
        """
        metrics = calculate_all_metrics(
            antecedent_support, consequent_support, combined_support,
            self.total_transactions
        )
        self.metrics_list.append(metrics)
        return metrics
    
    def get_summary(self) -> Dict[str, Dict[str, float]]:
        """
        Lấy tóm tắt thống kê cho tất cả chỉ số
        
        Returns:
            Từ điển chứa thống kê min, max, avg, etc.
        """
        if not self.metrics_list:
            return {}
        
        summary = {}
        
        for metric_name in ['support', 'confidence', 'lift', 'leverage', 'conviction']:
            values = [m[metric_name] for m in self.metrics_list]
            
            # Loại bỏ giá trị infinite
            valid_values = [v for v in values if v != float('inf') and v != float('-inf')]
            
            if valid_values:
                summary[metric_name] = {
                    'min': min(valid_values),
                    'max': max(valid_values),
                    'avg': sum(valid_values) / len(valid_values),
                    'total': len(valid_values)
                }
        
        return summary
    
    def get_stats(self) -> Dict:
        """
        Lấy thống kê chi tiết về các chỉ số
        
        Returns:
            Từ điển chứa thống kê
        """
        if not self.metrics_list:
            return {
                'total_rules': 0,
                'avg_support': 0.0,
                'avg_confidence': 0.0,
                'avg_lift': 0.0
            }
        
        supports = [m['support'] for m in self.metrics_list]
        confidences = [m['confidence'] for m in self.metrics_list]
        lifts = [m['lift'] for m in self.metrics_list if m['lift'] != float('inf')]
        
        return {
            'total_rules': len(self.metrics_list),
            'avg_support': sum(supports) / len(supports) if supports else 0.0,
            'avg_confidence': sum(confidences) / len(confidences) if confidences else 0.0,
            'avg_lift': sum(lifts) / len(lifts) if lifts else 0.0,
            'min_confidence': min(confidences) if confidences else 0.0,
            'max_confidence': max(confidences) if confidences else 0.0
        }


def categorize_by_metrics(rules: List[Dict], 
                         metric_name: str,
                         thresholds: List[float]) -> Dict[str, List[Dict]]:
    """
    Phân loại các luật theo giá trị của một chỉ số
    
    Args:
        rules: Danh sách các luật (mỗi luật là từ điển có metric_name)
        metric_name: Tên chỉ số để phân loại ('confidence', 'lift', etc.)
        thresholds: Danh sách ngưỡng để phân loại
        
    Returns:
        Từ điển {khoảng: [luật]}
    """
    categories = {}
    thresholds = sorted(thresholds)
    
    # Tạo các khoảng
    for i in range(len(thresholds) + 1):
        if i == 0:
            categories[f"< {thresholds[0]}"] = []
        elif i == len(thresholds):
            categories[f">= {thresholds[-1]}"] = []
        else:
            categories[f"{thresholds[i-1]} - {thresholds[i]}"] = []
    
    # Phân loại các luật
    for rule in rules:
        value = rule.get(metric_name, 0)
        
        for i, threshold in enumerate(thresholds):
            if value < threshold:
                key = f"< {thresholds[0]}" if i == 0 else f"{thresholds[i-1]} - {threshold}"
                categories[key].append(rule)
                break
        else:
            categories[f">= {thresholds[-1]}"].append(rule)
    
    return categories


def print_metrics_summary(metrics_dict: Dict[str, Dict[str, float]]) -> str:
    """
    Tạo chuỗi văn bản để in tóm tắt chỉ số
    
    Args:
        metrics_dict: Từ điển chỉ số từ MetricsAnalyzer.get_summary()
        
    Returns:
        Chuỗi văn bản
    """
    lines = []
    lines.append("="*80)
    lines.append("TÓM TẮT CÁC CHỈ SỐ")
    lines.append("="*80)
    
    for metric_name, stats in metrics_dict.items():
        lines.append(f"\n{metric_name.upper()}:")
        lines.append(f"  Min:   {stats['min']:.4f}")
        lines.append(f"  Max:   {stats['max']:.4f}")
        lines.append(f"  Avg:   {stats['avg']:.4f}")
        lines.append(f"  Count: {stats['total']}")
    
    lines.append("\n" + "="*80)
    return '\n'.join(lines)
