"""
Thuật toán Apriori - Khai phá itemset phổ biến theo cấp độ
"""

from typing import List, Set, Dict, Tuple, Optional
from itertools import combinations
import time
import os
from pathlib import Path


class Apriori:
    """Thuật toán Apriori để khai phá itemset phổ biến"""
    
    def __init__(self, min_support: int = 100, 
                 min_confidence: float = 0.5,
                 use_hash_tree: bool = False):
        """
        Khởi tạo Apriori
        
        Args:
            min_support: Số lượng support tối thiểu (tuyệt đối)
            min_confidence: Độ tin cậy tối thiểu cho luật kết hợp
            use_hash_tree: Có dùng hash tree để tối ưu hóa hay không
        
        Note: Tất cả các tham số HashTree được tự động tải từ .env:
              - HASH_TREE_MAX_LEAF_COUNT
              - HASH_TREE_MODULO
              - HASH_TREE_ITEM_MAPPING_FILE
        """
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.use_hash_tree = use_hash_tree
        self.frequent_itemsets = {}  # {kích_thước_itemset: [itemsets]}
        self.support_counts = {}  # {tuple_itemset: số_lượng}
        self.execution_time = 0
    
    def fit(self, transactions: List[Set[str]]) -> dict:
        self.num_transactions = len(transactions)
        """
        Chạy thuật toán Apriori
        
        Args:
            transactions: Danh sách giao dịch (mỗi giao dịch là một tập hợp các item)
            
        Returns:
            Từ điển với kết quả và thống kê
        """
        start_time = time.time()
        print("="*70)
        print("THUẬT TOÁN APRIORI - KHAI PHÁ ITEMSET PHỔ BIẾN")
        print("="*70)
        print(f"Số giao dịch: {len(transactions)}")
        print(f"Support tối thiểu: {self.min_support}")
        print()
        
        # Bước 1: Tìm các 1-itemset phổ biến
        L1 = self._find_frequent_1_itemsets(transactions)
        
        if not L1:
            print("Không tìm thấy itemset phổ biến nào!")
            self.execution_time = time.time() - start_time
            return {
                'frequent_itemsets': {},
                'support_counts': {},
                'total_itemsets': 0,
                'execution_time': self.execution_time
            }
        
        self.frequent_itemsets[1] = list(L1.keys())
        self.support_counts.update(L1)
        
        # Bước 2: Sinh candidate itemset lặp đi lặp lại
        current_itemsets = L1
        itemset_size = 1
        
        while current_itemsets and itemset_size < 20:  # Giới hạn hợp lý
            itemset_size += 1
            
            # Sinh candidates
            candidates = self._apriori_gen(list(current_itemsets.keys()), itemset_size)
            
            if not candidates:
                break
            
            print(f"Cấp độ {itemset_size}: Sinh {len(candidates)} candidates")
            
            # Đếm support
            candidate_support = self._count_support(candidates, transactions)
            
            # Lọc theo min_support
            frequent = {
                itemset: count for itemset, count in candidate_support.items()
                if count >= self.min_support
            }
            
            if not frequent:
                print(f"Cấp độ {itemset_size}: Không có itemset phổ biến")
                break
            
            print(f"Cấp độ {itemset_size}: Tìm thấy {len(frequent)} itemset phổ biến")
            
            self.frequent_itemsets[itemset_size] = list(frequent.keys())
            self.support_counts.update(frequent)
            current_itemsets = frequent
        
        self.execution_time = time.time() - start_time
        
        # In tóm tắt
        print()
        print("="*70)
        total_itemsets = sum(len(items) for items in self.frequent_itemsets.values())
        print(f"Tổng itemset phổ biến: {total_itemsets}")
        print(f"Thời gian thực thi: {self.execution_time:.2f} giây")
        print("="*70)
        
        return {
            'frequent_itemsets': self.frequent_itemsets,
            'support_counts': self.support_counts,
            'total_itemsets': total_itemsets,
            'execution_time': self.execution_time
        }
    
    def _find_frequent_1_itemsets(self, transactions: List[Set[str]]) -> Dict[tuple, int]:
        """Tìm tất cả các 1-itemset phổ biến"""
        item_counts = {}
        
        for transaction in transactions:
            for item in transaction:
                key = (item,)
                item_counts[key] = item_counts.get(key, 0) + 1
        
        # Lọc theo min_support
        frequent_1 = {
            itemset: count for itemset, count in item_counts.items()
            if count >= self.min_support
        }
        
        print(f"Cấp độ 1: Tìm thấy {len(frequent_1)} 1-itemset phổ biến")
        
        return frequent_1
    
    def _apriori_gen(self, itemsets: List[tuple], k: int) -> List[tuple]:
        """
        Sinh candidate k-itemset từ (k-1)-itemset
        
        Args:
            itemsets: Danh sách các (k-1)-itemset phổ biến
            k: Kích thước của candidates cần sinh
            
        Returns:
            Danh sách các k-itemset candidates
        """
        candidates = set()
        
        # Bước self-join: kết hợp itemsets kích thước k-1
        for i in range(len(itemsets)):
            for j in range(i + 1, len(itemsets)):
                itemset1 = set(itemsets[i])
                itemset2 = set(itemsets[j])
                
                # Kết hợp nếu k-2 item đầu tiên giống nhau
                if len(itemset1 & itemset2) == k - 2:
                    candidate = tuple(sorted(itemset1 | itemset2))
                    if len(candidate) == k:
                        candidates.add(candidate)
        
        # Bước pruning: xóa candidates có tập con không phổ biến
        pruned = []
        for candidate in candidates:
            # Kiểm tra tất cả các (k-1)-subset
            is_valid = True
            for i in range(len(candidate)):
                subset = candidate[:i] + candidate[i+1:]
                if subset not in itemsets:
                    is_valid = False
                    break
            
            if is_valid:
                pruned.append(candidate)
        
        return pruned
    
    def _count_support(self, candidates: List[tuple], 
                      transactions: List[Set[str]]) -> Dict[tuple, int]:
        """Đếm support cho các candidate itemsets"""
        
        if self.use_hash_tree:
            return self._count_support_with_hash_tree(candidates, transactions)
        else:
            return self._count_support_basic(candidates, transactions)
    
    def _count_support_basic(self, candidates: List[tuple], 
                            transactions: List[Set[str]]) -> Dict[tuple, int]:
        """Đếm support bằng phương pháp cơ bản (không dùng hash tree)"""
        support_counts = {}
        
        for transaction in transactions:
            for candidate in candidates:
                if all(item in transaction for item in candidate):
                    key = tuple(sorted(candidate))
                    support_counts[key] = support_counts.get(key, 0) + 1
        
        return support_counts
    
    def _count_support_with_hash_tree(self, candidates: List[tuple],
                                     transactions: List[Set[str]]) -> Dict[tuple, int]:
        """Đếm support bằng hash tree (tối ưu hơn brute force)"""
        from .hash_tree import HashTree
        from itertools import combinations as _comb
        
        if not candidates:
            return {}
        
        itemset_size = len(candidates[0])
        
        try:
            # Tạo hash tree và insert tất cả candidates
            hash_tree = HashTree()
            candidate_set = set(candidates)  # để filter nhanh
            
            for candidate in candidates:
                hash_tree.insert(list(candidate))
            
            # Xây tập hợp tất cả items trong candidates để filter transaction
            candidate_items = set(item for c in candidates for item in c)
            
            support_counts: Dict[tuple, int] = {}
            total = len(transactions)
            
            for idx, transaction in enumerate(transactions):
                # Tối ưu: chỉ xét items trong transaction có trong candidates
                filtered = sorted(transaction & candidate_items)
                if len(filtered) < itemset_size:
                    continue
                
                # Sinh C(|filtered|, k) subsets, route từng cái qua hash tree
                for subset in _comb(filtered, itemset_size):
                    hash_tree.root.count_subset(subset, 0, support_counts)
                
                # In tiến trình mỗi 20%
                if (idx + 1) % max(1, total // 5) == 0:
                    print(f"  [Hash Tree] Đã xử lý {idx+1}/{total} transactions...")
            
            return support_counts
            
        except Exception as e:
            print(f"  [Hash Tree] Lỗi: {e} → fallback về basic counting")
            return self._count_support_basic(candidates, transactions)

    
    def generate_rules(self) -> List[Dict]:
        """
        Sinh các luật kết hợp từ itemset phổ biến
        
        Returns:
            Danh sách các luật kết hợp với các chỉ số
        """
        rules = []
        N = getattr(self, 'num_transactions', 1)
        
        # Chỉ dùng itemsets có kích thước >= 2
        for itemset_size in self.frequent_itemsets:
            if itemset_size < 2:
                continue
            
            for itemset in self.frequent_itemsets[itemset_size]:
                itemset_support = self.support_counts[itemset]
                
                # Sinh tất cả các cặp antecedent/consequent có thể
                for i in range(1, len(itemset)):
                    for antecedent_items in combinations(itemset, i):
                        antecedent = tuple(sorted(antecedent_items))
                        consequent = tuple(sorted(set(itemset) - set(antecedent)))
                        
                        if not consequent:
                            continue
                        
                        antecedent_support = self.support_counts.get(antecedent, 0)
                        if antecedent_support == 0:
                            continue
                        
                        # Consequent support: lấy từ support_counts nếu có,
                        # nếu không thì đếm trực tiếp từ support_counts (vẫn là frequent)
                        consequent_support = self.support_counts.get(consequent, 0)
                        
                        confidence = itemset_support / antecedent_support
                        
                        if confidence >= self.min_confidence:
                            # Lift = P(A∪B) / (P(A) * P(B))
                            # Với absolute counts: lift = (sup(A∪B)/N) / ((sup(A)/N) * (sup(B)/N))
                            #                           = sup(A∪B) * N / (sup(A) * sup(B))
                            if consequent_support > 0:
                                lift = (itemset_support * N) / (antecedent_support * consequent_support)
                            else:
                                lift = 1.0  # fallback nếu không có support riêng lẻ
                            
                            rules.append({
                                'antecedent': antecedent,
                                'consequent': consequent,
                                'support': itemset_support,
                                'confidence': confidence,
                                'lift': lift
                            })
        
        return sorted(rules, key=lambda x: x['confidence'], reverse=True)
    
    def get_results_summary(self) -> str:
        """Lấy tóm tắt kết quả"""
        summary = []
        summary.append("="*70)
        summary.append("TÓM TẮT KẾT QUẢ APRIORI")
        summary.append("="*70)
        
        for size in sorted(self.frequent_itemsets.keys()):
            count = len(self.frequent_itemsets[size])
            summary.append(f"Kích thước {size}: {count} itemsets")
        
        summary.append("-"*70)
        total = sum(len(items) for items in self.frequent_itemsets.values())
        summary.append(f"Tổng itemset phổ biến: {total}")
        summary.append(f"Thời gian thực thi: {self.execution_time:.2f}s")
        summary.append("="*70)
        
        return "\n".join(summary)
