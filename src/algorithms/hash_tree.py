"""
Hash Tree - Cấu trúc dữ liệu đếm candidate itemsets hiệu quả trong Apriori.

Thuật toán chuẩn Agrawal et al. 1994:
  Insert:  Route candidate theo item[depth] tại mỗi level, lưu nguyên vẹn ở leaf.
  Count:   Với mỗi transaction, sinh tất cả C(n,k) k-subset đã sort,
           route từng subset xuống tree y như khi insert.
           Tại leaf: so sánh subset == candidate để tăng support.
"""

from __future__ import annotations
from typing import List, Set, Dict, Optional
from itertools import combinations
import pickle
import os
from pathlib import Path
from dotenv import load_dotenv


# ---------------------------------------------------------------------------
# Tìm project root (thư mục chứa .env hoặc chứa src/)
# ---------------------------------------------------------------------------
def _find_project_root() -> Path:
    """Leo ngược từ vị trí file này để tìm project root."""
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / '.env').exists() or (parent / 'src').exists():
            return parent
    return Path.cwd()


_PROJECT_ROOT = _find_project_root()


# ---------------------------------------------------------------------------
# HashTreeNode
# ---------------------------------------------------------------------------

class HashTreeNode:
    """Nút trong Hash Tree."""

    __slots__ = ('depth', 'max_leaf_count', 'is_leaf',
                 'itemsets', 'children', 'item_mapping', 'modulo')

    def __init__(self, depth: int, max_leaf_count: int,
                 item_mapping: Dict[str, int], modulo: int):
        self.depth = depth
        self.max_leaf_count = max_leaf_count
        self.is_leaf = True
        self.itemsets: List[tuple] = []
        self.children: Dict[int, HashTreeNode] = {}
        self.item_mapping = item_mapping
        self.modulo = modulo

    # ------------------------------------------------------------------
    # Hash function
    # ------------------------------------------------------------------

    def _hash(self, item: str) -> int:
        if item in self.item_mapping:
            return self.item_mapping[item] % self.modulo
        return abs(hash(item)) % self.modulo  # fallback

    # ------------------------------------------------------------------
    # Insert
    # ------------------------------------------------------------------

    def insert(self, itemset: tuple) -> None:
        """Thêm candidate itemset (đã sort) vào cây."""
        if self.is_leaf:
            self.itemsets.append(itemset)
            if len(self.itemsets) > self.max_leaf_count:
                self._split()
            return

        # Internal node: route theo item[self.depth]
        if self.depth >= len(itemset):
            # Itemset quá ngắn để route thêm → giữ ở đây
            self.itemsets.append(itemset)
            return

        b = self._hash(itemset[self.depth])
        if b not in self.children:
            self.children[b] = HashTreeNode(
                self.depth + 1, self.max_leaf_count, self.item_mapping, self.modulo
            )
        self.children[b].insert(itemset)

    def _split(self) -> None:
        """Chuyển leaf → internal node, phân phối lại itemsets."""
        self.is_leaf = False
        old = self.itemsets
        self.itemsets = []   # itemsets "tồn dư" (edge-case depth >= len)

        for itemset in old:
            if self.depth >= len(itemset):
                self.itemsets.append(itemset)
                continue
            b = self._hash(itemset[self.depth])
            if b not in self.children:
                self.children[b] = HashTreeNode(
                    self.depth + 1, self.max_leaf_count, self.item_mapping, self.modulo
                )
            self.children[b].insert(itemset)

    # ------------------------------------------------------------------
    # Count support
    # ------------------------------------------------------------------

    def count_subset(self, subset: tuple, depth: int,
                     support: Dict[tuple, int]) -> None:
        """
        Route subset (đã sort) xuống cây và đếm nếu tìm thấy ở leaf.

        Quy tắc route PHẢI khớp với quy tắc insert:
          - Internal node tại depth d → hash subset[d] → đi xuống child tương ứng.
          - Leaf → duyệt danh sách candidates, tăng support nếu candidate == subset.
        """
        if self.is_leaf:
            for candidate in self.itemsets:
                if candidate == subset:
                    support[candidate] = support.get(candidate, 0) + 1
            return

        if depth >= len(subset):
            # Không route được nữa → kiểm tra phần itemsets tồn dư ở internal
            for candidate in self.itemsets:
                if candidate == subset:
                    support[candidate] = support.get(candidate, 0) + 1
            return

        b = self._hash(subset[depth])
        if b in self.children:
            self.children[b].count_subset(subset, depth + 1, support)

        # Kiểm tra itemsets tồn dư (edge-case) lưu tại chính internal node này
        for candidate in self.itemsets:
            if candidate == subset:
                support[candidate] = support.get(candidate, 0) + 1


# ---------------------------------------------------------------------------
# HashTree  (public API)
# ---------------------------------------------------------------------------

class HashTree:
    """Hash Tree để đếm support cho candidate itemsets trong Apriori."""

    def __init__(self):
        """
        Tự động load cấu hình từ .env (tìm từ project root):
          HASH_TREE_MAX_LEAF_COUNT    (default: 10)
          HASH_TREE_MODULO            (default: 10)
          HASH_TREE_ITEM_MAPPING_FILE (default: data/processed/item_mapping.pkl)
        """
        env_path = _PROJECT_ROOT / '.env'
        load_dotenv(dotenv_path=env_path, override=False)

        self.max_leaf_count = int(os.getenv('HASH_TREE_MAX_LEAF_COUNT', '10'))
        self.modulo = int(os.getenv('HASH_TREE_MODULO', '10'))

        # Resolve đường dẫn item_mapping relative với project root
        mapping_rel = os.getenv(
            'HASH_TREE_ITEM_MAPPING_FILE', 'data/processed/item_mapping.pkl'
        )
        mapping_path = Path(mapping_rel)
        if not mapping_path.is_absolute():
            mapping_path = _PROJECT_ROOT / mapping_path

        if not mapping_path.exists():
            raise FileNotFoundError(
                f"[HashTree] item_mapping không tìm thấy: {mapping_path}\n"
                f"  Project root: {_PROJECT_ROOT}\n"
                "  Hãy chạy preprocessing trước hoặc kiểm tra HASH_TREE_ITEM_MAPPING_FILE trong .env"
            )

        with open(mapping_path, 'rb') as f:
            self.item_mapping: Dict[str, int] = pickle.load(f)

        self.root = HashTreeNode(0, self.max_leaf_count, self.item_mapping, self.modulo)
        self._itemset_size: Optional[int] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def insert(self, itemset: List[str]) -> None:
        """Thêm một candidate itemset (tự động sort → tuple)."""
        t = tuple(sorted(itemset))
        if self._itemset_size is None:
            self._itemset_size = len(t)
        self.root.insert(t)

    def count_support(self, transactions: List[Set[str]],
                      itemset_size: int) -> Dict[tuple, int]:
        """
        Đếm support cho tất cả candidates trong cây.

        Với mỗi transaction T:
          1. Sinh tất cả C(|T|, k) k-subset đã sort.
          2. Route từng subset xuống cây → leaf → so sánh == candidate.

        Trả về: {candidate_tuple: support_count}
        """
        support_counts: Dict[tuple, int] = {}
        k = itemset_size

        for transaction in transactions:
            items = sorted(transaction)
            if len(items) < k:
                continue
            for subset in combinations(items, k):
                self.root.count_subset(subset, 0, support_counts)

        return support_counts
