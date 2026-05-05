"""
So sánh hiệu năng của các thuật toán khai phá luật kết hợp
"""

from typing import Dict, List, Tuple
import time
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class AlgorithmResult:
    """Kết quả thực thi của một thuật toán"""
    algorithm_name: str
    total_itemsets: int
    total_rules: int
    execution_time: float
    min_support: int
    min_confidence: float
    itemsets_by_size: Dict[int, int]  # {kích_thước: số_lượng}
    memory_usage: float = 0.0  # MB
    
    def __str__(self):
        """Biểu diễn chuỗi"""
        return (
            f"{self.algorithm_name}:\n"
            f"  Itemset: {self.total_itemsets}\n"
            f"  Rules: {self.total_rules}\n"
            f"  Time: {self.execution_time:.2f}s\n"
            f"  Memory: {self.memory_usage:.2f}MB"
        )


class AlgorithmComparator:
    """So sánh các thuật toán khai phá luật kết hợp"""
    
    def __init__(self):
        """Khởi tạo trình so sánh"""
        self.results: Dict[str, AlgorithmResult] = {}
    
    def add_result(self, result: AlgorithmResult):
        """
        Thêm kết quả của một thuật toán
        
        Args:
            result: Kết quả thực thi
        """
        self.results[result.algorithm_name] = result
    
    def compare_execution_time(self) -> Dict[str, float]:
        """
        So sánh thời gian thực thi
        
        Returns:
            Từ điển {thuật_toán: thời_gian}
        """
        return {
            name: result.execution_time 
            for name, result in self.results.items()
        }
    
    def compare_itemset_count(self) -> Dict[str, int]:
        """
        So sánh số lượng itemset tìm được
        
        Returns:
            Từ điển {thuật_toán: số_itemset}
        """
        return {
            name: result.total_itemsets
            for name, result in self.results.items()
        }
    
    def compare_rule_count(self) -> Dict[str, int]:
        """
        So sánh số lượng luật tìm được
        
        Returns:
            Từ điển {thuật_toán: số_luật}
        """
        return {
            name: result.total_rules
            for name, result in self.results.items()
        }
    
    def get_fastest_algorithm(self) -> Tuple[str, float]:
        """
        Lấy thuật toán chạy nhanh nhất
        
        Returns:
            (tên_thuật_toán, thời_gian)
        """
        if not self.results:
            return None, 0
        
        fastest = min(
            self.results.items(),
            key=lambda x: x[1].execution_time
        )
        return fastest[0], fastest[1].execution_time
    
    def get_slowest_algorithm(self) -> Tuple[str, float]:
        """
        Lấy thuật toán chạy chậm nhất
        
        Returns:
            (tên_thuật_toán, thời_gian)
        """
        if not self.results:
            return None, 0
        
        slowest = max(
            self.results.items(),
            key=lambda x: x[1].execution_time
        )
        return slowest[0], slowest[1].execution_time
    
    def get_speedup(self, baseline_algorithm: str) -> Dict[str, float]:
        """
        Tính toán speedup so với thuật toán cơ sở
        
        Args:
            baseline_algorithm: Tên thuật toán dùng làm cơ sở
            
        Returns:
            Từ điển {thuật_toán: speedup}
        """
        if baseline_algorithm not in self.results:
            return {}
        
        baseline_time = self.results[baseline_algorithm].execution_time
        
        if baseline_time == 0:
            return {}
        
        speedups = {}
        for name, result in self.results.items():
            speedups[name] = baseline_time / result.execution_time
        
        return speedups
    
    def get_memory_efficiency(self) -> Dict[str, float]:
        """
        Lấy hiệu suất bộ nhớ: itemset / bộ nhớ
        
        Returns:
            Từ điển {thuật_toán: hiệu_suất}
        """
        efficiency = {}
        for name, result in self.results.items():
            if result.memory_usage > 0:
                efficiency[name] = result.total_itemsets / result.memory_usage
            else:
                efficiency[name] = 0
        return efficiency
    
    def get_time_efficiency(self) -> Dict[str, float]:
        """
        Lấy hiệu suất thời gian: itemset / thời_gian
        
        Returns:
            Từ điển {thuật_toán: hiệu_suất (itemset/s)}
        """
        efficiency = {}
        for name, result in self.results.items():
            if result.execution_time > 0:
                efficiency[name] = result.total_itemsets / result.execution_time
            else:
                efficiency[name] = 0
        return efficiency
    
    def get_comprehensive_comparison(self) -> Dict:
        """
        Lấy so sánh toàn diện
        
        Returns:
            Từ điển chứa tất cả các so sánh
        """
        return {
            'execution_time': self.compare_execution_time(),
            'itemset_count': self.compare_itemset_count(),
            'rule_count': self.compare_rule_count(),
            'time_efficiency': self.get_time_efficiency(),
            'memory_efficiency': self.get_memory_efficiency()
        }


def create_comparison_report(comparator: AlgorithmComparator) -> str:
    """
    Tạo báo cáo so sánh chi tiết
    
    Args:
        comparator: Đối tượng so sánh
        
    Returns:
        Chuỗi văn bản chứa báo cáo
    """
    lines = []
    lines.append("="*80)
    lines.append("BÁO CÁO SO SÁNH THUẬT TOÁN")
    lines.append("="*80)
    
    # 1. Thống kê cơ bản
    lines.append("\n1. THỐNG KÊ CƠ BẢN")
    lines.append("-"*80)
    
    for name in sorted(comparator.results.keys()):
        result = comparator.results[name]
        lines.append(f"\n{name}:")
        lines.append(f"  • Itemset: {result.total_itemsets}")
        lines.append(f"  • Luật: {result.total_rules}")
        lines.append(f"  • Thời gian: {result.execution_time:.4f}s")
        if result.memory_usage > 0:
            lines.append(f"  • Bộ nhớ: {result.memory_usage:.2f}MB")
    
    # 2. So sánh thời gian
    lines.append("\n\n2. SO SÁNH THỜI GIAN THỰC TH")
    lines.append("-"*80)
    
    time_comparison = comparator.compare_execution_time()
    fastest_algo, fastest_time = comparator.get_fastest_algorithm()
    slowest_algo, slowest_time = comparator.get_slowest_algorithm()
    
    lines.append(f"Nhanh nhất: {fastest_algo} ({fastest_time:.4f}s)")
    lines.append(f"Chậm nhất: {slowest_algo} ({slowest_time:.4f}s)")
    
    if fastest_time > 0:
        slowdown = slowest_time / fastest_time
        lines.append(f"Chênh lệch: {slowdown:.2f}x")
    
    # 3. So sánh số lượng kết quả
    lines.append("\n\n3. SO SÁNH SỐ LƯỢNG KẾT QUẢ")
    lines.append("-"*80)
    
    itemset_count = comparator.compare_itemset_count()
    max_itemsets = max(itemset_count.values()) if itemset_count else 0
    
    for name in sorted(itemset_count.keys()):
        count = itemset_count[name]
        if max_itemsets > 0:
            percentage = (count / max_itemsets) * 100
            lines.append(f"{name}: {count} itemsets ({percentage:.1f}% of max)")
        else:
            lines.append(f"{name}: {count} itemsets")
    
    # 4. Hiệu suất
    lines.append("\n\n4. HIỆU SUẤT (ITEMSET/GIÂY)")
    lines.append("-"*80)
    
    time_eff = comparator.get_time_efficiency()
    for name in sorted(time_eff.keys()):
        lines.append(f"{name}: {time_eff[name]:.2f} itemsets/s")
    
    lines.append("\n" + "="*80)
    
    return '\n'.join(lines)


def create_performance_summary(comparator: AlgorithmComparator) -> Dict:
    """
    Tạo bản tóm tắt hiệu năng
    
    Args:
        comparator: Đối tượng so sánh
        
    Returns:
        Từ điển chứa tóm tắt
    """
    fastest_algo, fastest_time = comparator.get_fastest_algorithm()
    slowest_algo, slowest_time = comparator.get_slowest_algorithm()
    
    return {
        'total_algorithms': len(comparator.results),
        'fastest_algorithm': fastest_algo,
        'fastest_time': fastest_time,
        'slowest_algorithm': slowest_algo,
        'slowest_time': slowest_time,
        'time_comparison': comparator.compare_execution_time(),
        'itemset_comparison': comparator.compare_itemset_count(),
        'time_efficiency': comparator.get_time_efficiency()
    }


class ParameterSensitivityAnalyzer:
    """Phân tích độ nhạy cảm của thuật toán theo tham số"""
    
    def __init__(self, algorithm_name: str):
        """
        Khởi tạo bộ phân tích
        
        Args:
            algorithm_name: Tên của thuật toán
        """
        self.algorithm_name = algorithm_name
        self.results_by_support = defaultdict(list)
        self.results_by_confidence = defaultdict(list)
    
    def add_support_sensitivity(self, min_support: int, result: AlgorithmResult):
        """
        Thêm kết quả cho phân tích độ nhạy theo support
        
        Args:
            min_support: Giá trị min_support
            result: Kết quả thực thi
        """
        self.results_by_support[min_support].append(result)
    
    def add_confidence_sensitivity(self, min_confidence: float, result: AlgorithmResult):
        """
        Thêm kết quả cho phân tích độ nhạy theo confidence
        
        Args:
            min_confidence: Giá trị min_confidence
            result: Kết quả thực thi
        """
        self.results_by_confidence[min_confidence].append(result)
    
    def analyze_support_sensitivity(self) -> Dict[int, Dict]:
        """
        Phân tích ảnh hưởng của min_support
        
        Returns:
            Từ điển {min_support: {thống_kê}}
        """
        analysis = {}
        
        for support, results in sorted(self.results_by_support.items()):
            if results:
                avg_time = sum(r.execution_time for r in results) / len(results)
                avg_itemsets = sum(r.total_itemsets for r in results) / len(results)
                
                analysis[support] = {
                    'avg_execution_time': avg_time,
                    'avg_itemsets': avg_itemsets,
                    'num_runs': len(results)
                }
        
        return analysis
    
    def analyze_confidence_sensitivity(self) -> Dict[float, Dict]:
        """
        Phân tích ảnh hưởng của min_confidence
        
        Returns:
            Từ điển {min_confidence: {thống_kê}}
        """
        analysis = {}
        
        for confidence, results in sorted(self.results_by_confidence.items()):
            if results:
                avg_time = sum(r.execution_time for r in results) / len(results)
                avg_rules = sum(r.total_rules for r in results) / len(results)
                
                analysis[confidence] = {
                    'avg_execution_time': avg_time,
                    'avg_rules': avg_rules,
                    'num_runs': len(results)
                }
        
        return analysis


def create_sensitivity_report(analyzer: ParameterSensitivityAnalyzer) -> str:
    """
    Tạo báo cáo phân tích độ nhạy cảm
    
    Args:
        analyzer: Bộ phân tích độ nhạy cảm
        
    Returns:
        Chuỗi văn bản chứa báo cáo
    """
    lines = []
    lines.append("="*80)
    lines.append(f"PHÂN TÍCH ĐỘ NHẠY CẢM: {analyzer.algorithm_name}")
    lines.append("="*80)
    
    # Phân tích support
    if analyzer.results_by_support:
        lines.append("\n1. ẢNH HƯỞNG CỦA MIN_SUPPORT")
        lines.append("-"*80)
        
        support_analysis = analyzer.analyze_support_sensitivity()
        for support in sorted(support_analysis.keys()):
            stats = support_analysis[support]
            lines.append(f"\nMin Support = {support}:")
            lines.append(f"  • Itemsets: {stats['avg_itemsets']:.0f}")
            lines.append(f"  • Thời gian: {stats['avg_execution_time']:.4f}s")
    
    # Phân tích confidence
    if analyzer.results_by_confidence:
        lines.append("\n\n2. ẢNH HƯỞNG CỦA MIN_CONFIDENCE")
        lines.append("-"*80)
        
        confidence_analysis = analyzer.analyze_confidence_sensitivity()
        for confidence in sorted(confidence_analysis.keys()):
            stats = confidence_analysis[confidence]
            lines.append(f"\nMin Confidence = {confidence:.2f}:")
            lines.append(f"  • Luật: {stats['avg_rules']:.0f}")
            lines.append(f"  • Thời gian: {stats['avg_execution_time']:.4f}s")
    
    lines.append("\n" + "="*80)
    
    return '\n'.join(lines)
