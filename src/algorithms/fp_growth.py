"""
Thuat toan FP-Growth - Khai pha mau tan suat su dung FP-Tree
"""

from typing import List, Set, Dict, Tuple, Optional
from collections import defaultdict
import time


class FPNode:
    """Nut trong FP-Tree"""
    
    def __init__(self, item: str, count: int = 0, parent: Optional['FPNode'] = None):
        """
        Khoi tao nut FP-Tree
        
        Args:
            item: Nhan hang
            count: So luong support
            parent: Nut cha
        """
        self.item = item
        self.count = count
        self.parent = parent
        self.children = {}
        self.link = None  # Link to next node with same item
    
    def increment(self, count: int) -> None:
        """Tang so luong cua nut"""
        self.count += count
    
    def display(self, indent: int = 0) -> str:
        """Hien thi nut (dung cho giai lap loi)"""
        result = ""
        result += "  " * indent + f"{self.item}:{self.count}\n"
        for child in self.children.values():
            result += child.display(indent + 1)
        return result


class FPTree:
    """FP-Tree dung cho khai pha mau tan suat"""
    
    def __init__(self, transactions: List[Set[str]], 
                 min_support: int,
                 root_value: str = 'root',
                 root_count: int = 0):
        """
        Xay dung FP-Tree
        
        Args:
            transactions: Danh sach giao dich
            min_support: So luong support toi thieu
            root_value: Nhan cua nut goc
            root_count: So luong cua nut goc
        """
        self.min_support = min_support
        self.root = FPNode(root_value, root_count)
        self.header_table = {}  # {item: (so_luong, lien_ket_nut)}
        self.frequent_items = self._get_frequent_items(transactions)
        self._build_tree(transactions)
    
    def _get_frequent_items(self, transactions: List[Set[str]]) -> Dict[str, int]:
        """Lay cac hang voi so luong cua chung"""
        item_counts = defaultdict(int)
        
        for transaction in transactions:
            for item in transaction:
                item_counts[item] += 1
        
        # Loc theo min_support
        return {
            item: count for item, count in item_counts.items()
            if count >= self.min_support
        }
    
    def _build_tree(self, transactions: List[Set[str]]) -> None:
        """Xay dung FP-Tree tu cac giao dich"""
        for transaction in transactions:
            # Loc va sap xep cac hang theo tan suat giam dan, tie-break theo ten item (tang dan)
            sorted_items = sorted(
                [item for item in transaction if item in self.frequent_items],
                key=lambda x: (-self.frequent_items[x], x)
            )
            
            if sorted_items:
                self._insert_transaction(sorted_items, self.root, 1)
    
    def _insert_transaction(self, items: List[str], node: FPNode, count: int) -> None:
        """De quy chen giao dich vao cay"""
        if not items:
            return
        
        first_item = items[0]
        
        if first_item in node.children:
            child = node.children[first_item]
            child.increment(count)
            # QUAN TRONG: phai cap nhat header_table khi node da ton tai
            self.header_table[first_item][0] += count
        else:
            # Tao nut moi
            child = FPNode(first_item, count, node)
            node.children[first_item] = child
            
            # Cap nhat bang header
            if first_item in self.header_table:
                self.header_table[first_item][0] += count
                # Lien ket den chuoi nut
                current = self.header_table[first_item][1]
                while current.link:
                    current = current.link
                current.link = child
            else:
                self.header_table[first_item] = [count, child]
        
        # De quy chen cac hang con lai
        if len(items) > 1:
            self._insert_transaction(items[1:], child, count)
    
    def get_paths(self, item: str) -> Tuple[List[List[str]], List[int]]:
        """Lay tat ca cac duong trong cay co dung voi hang"""
        paths = []
        counts = []
        
        if item not in self.header_table:
            return paths, counts
        
        node = self.header_table[item][1]
        
        while node:
            path = []
            parent = node.parent
            
            while parent.item != 'root':
                path.append(parent.item)
                parent = parent.parent
            
            if path:
                paths.append(list(reversed(path)))
                counts.append(node.count)
            
            node = node.link
        
        return paths, counts


class FPGrowth:
    """Thuat toan FP-Growth dung cho khai pha itemset pho bien"""
    
    def __init__(self, min_support: int = 100, min_confidence: float = 0.5):
        """
        Khoi tao FP-Growth
        
        Args:
            min_support: So luong support toi thieu (tuyet doi)
            min_confidence: Do tin cay toi thieu cho luat ket hop
        """
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.frequent_itemsets = {}  # {kich_thuoc_itemset: [itemsets]}
        self.support_counts = {}  # {tuple_itemset: so_luong}
        self.execution_time = 0
    
    def fit(self, transactions: List[Set[str]]) -> dict:
        self.num_transactions = len(transactions)
        """
        Chay thuat toan FP-Growth
        
        Args:
            transactions: Danh sach giao dich (moi giao dich la mot tap hop cac item)
            
        Returns:
            Tu dien voi ket qua va thong ke
        """
        start_time = time.time()
        print("="*70)
        print("THUAT TOAN FP-GROWTH - KHAI PHA MAU TAN SUAT")
        print("="*70)
        print(f"So giao dich: {len(transactions)}")
        print(f"Support toi thieu: {self.min_support}")
        print()
        
        # Xay dung FP-Tree
        print("Xay dung FP-Tree...")
        tree = FPTree(transactions, self.min_support)
        print(f"FP-Tree duoc xay dung voi {len(tree.frequent_items)} hang pho bien")
        print()
        
        # Khai pha mau
        self._mine_tree(tree, [], transactions)
        
        self.execution_time = time.time() - start_time
        
        # In tom tat
        print()
        print("="*70)
        total_itemsets = sum(len(items) for items in self.frequent_itemsets.values())
        print(f"Tong itemset pho bien: {total_itemsets}")
        print(f"Thoi gian thuc thi: {self.execution_time:.2f} giay")
        print("="*70)
        
        return {
            'frequent_itemsets': self.frequent_itemsets,
            'support_counts': self.support_counts,
            'total_itemsets': total_itemsets,
            'execution_time': self.execution_time
        }
    
    def _mine_tree(self, tree: FPTree, prefix: List[str], 
                   original_transactions: List[Set[str]]) -> None:
        """
        Khai pha FP-Tree de quy
        
        Args:
            tree: FP-Tree can khai pha
            prefix: Tien to itemset hien tai
            original_transactions: Cac giao dich goc (dung de xac thuc)
        """
        # Sap xep theo tan suat (tang dan dung cho khai pha tu duoi len tren)
        items = sorted(tree.header_table.items(), 
                      key=lambda x: x[1][0])
        
        for item, (support, _) in items:
            # Tao itemset moi
            new_itemset = tuple(sorted(prefix + [item]))
            
            # Luu itemset pho bien
            self.support_counts[new_itemset] = support
            size = len(new_itemset)
            if size not in self.frequent_itemsets:
                self.frequent_itemsets[size] = []
            self.frequent_itemsets[size].append(new_itemset)
            
            # In tien trinh
            if len(self.support_counts) % 1000 == 0:
                total = sum(len(items) for items in self.frequent_itemsets.values())
                print(f"  Tien trinh: Tim thay {total} itemsets")
            
            # Lay co so mau tu le
            paths, path_counts = tree.get_paths(item)
            
            if paths:
                # Xay dung cac giao dich tu dieu kien
                cond_transactions = []
                for path, count in zip(paths, path_counts):
                    for _ in range(count):
                        cond_transactions.append(set(path))
                
                # Xay dung FP-Tree tu dieu kien
                cond_tree = FPTree(cond_transactions, self.min_support)
                
                # Khai pha de quy
                if cond_tree.header_table:
                    self._mine_tree(cond_tree, list(new_itemset), original_transactions)
    
    def generate_rules(self) -> List[Dict]:
        """
        Sinh cac luat ket hop tu itemset pho bien
        
        Returns:
            Danh sach cac luat ket hop voi cac chi so
        """
        from itertools import combinations
        
        rules = []
        N = getattr(self, 'num_transactions', 1)
        
        # Chi dung itemsets co kich thuoc >= 2
        for itemset_size in self.frequent_itemsets:
            if itemset_size < 2:
                continue
            
            for itemset in self.frequent_itemsets[itemset_size]:
                itemset_support = self.support_counts[itemset]
                
                # Sinh tat ca cac cap antecedent/consequent co the
                for i in range(1, len(itemset)):
                    for antecedent_items in combinations(itemset, i):
                        antecedent = tuple(sorted(antecedent_items))
                        consequent = tuple(sorted(set(itemset) - set(antecedent)))
                        
                        if not consequent:
                            continue
                        
                        antecedent_support = self.support_counts.get(antecedent, 0)
                        if antecedent_support == 0:
                            continue
                        
                        consequent_support = self.support_counts.get(consequent, 0)
                        
                        confidence = itemset_support / antecedent_support
                        
                        if confidence >= self.min_confidence:
                            # Lift = P(AuB) / (P(A) * P(B))
                            # Voi absolute counts: lift = sup(AuB)*N / (sup(A)*sup(B))
                            if consequent_support > 0:
                                lift = (itemset_support * N) / (antecedent_support * consequent_support)
                            else:
                                lift = 1.0
                            
                            rules.append({
                                'antecedent': antecedent,
                                'consequent': consequent,
                                'support': itemset_support,
                                'confidence': confidence,
                                'lift': lift
                            })
        
        return sorted(rules, key=lambda x: x['confidence'], reverse=True)
    
    def get_results_summary(self) -> str:
        """Lay tom tat ket qua"""
        summary = []
        summary.append("="*70)
        summary.append("TOM TAT KET QUA FP-GROWTH")
        summary.append("="*70)
        
        for size in sorted(self.frequent_itemsets.keys()):
            count = len(self.frequent_itemsets[size])
            summary.append(f"Kich thuoc {size}: {count} itemsets")
        
        summary.append("-"*70)
        total = sum(len(items) for items in self.frequent_itemsets.values())
        summary.append(f"Tong itemset pho bien: {total}")
        summary.append(f"Thoi gian thuc thi: {self.execution_time:.2f}s")
        summary.append("="*70)
        
        return "\n".join(summary)
