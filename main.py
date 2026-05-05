"""
Pipeline chính: Raw data → Preprocessing → Transactions →
                Frequent Itemsets → Association Rules → Evaluation + Visualization
"""

import os
import sys
import time
from pathlib import Path

# ── Thêm project root vào sys.path ────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / '.env')


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def _header(title: str) -> None:
    print()
    print("═" * 70)
    print(f"  {title}")
    print("═" * 70)


def _step(n: int, desc: str) -> None:
    print(f"\n── Bước {n}: {desc} {'─' * (55 - len(desc))}")


# ══════════════════════════════════════════════════════════════════════════════
# Bước 0 – Load cấu hình
# ══════════════════════════════════════════════════════════════════════════════

def load_config() -> dict:
    return {
        # Preprocessing
        "raw_data_path": PROJECT_ROOT / os.getenv("RAW_DATA_PATH", "data/raw/online_retail_II.xlsx"),
        "output_dir":    PROJECT_ROOT / os.getenv("OUTPUT_DIR", "data/processed"),
        "min_support_count":          int(os.getenv("MIN_SUPPORT_COUNT", 50)),
        "min_support_percentage":   float(os.getenv("MIN_SUPPORT_PERCENTAGE", 0.1)),
        "min_items_per_transaction":  int(os.getenv("MIN_ITEMS_PER_TRANSACTION", 2)),
        # Mining
        "min_support":    int(os.getenv("MINING_MIN_SUPPORT", 100)),
        "min_confidence": float(os.getenv("MINING_MIN_CONFIDENCE", 0.5)),
        "algorithm":      os.getenv("SELECTED_ALGORITHM", "all").lower(),
        "use_hash_tree":  os.getenv("APRIORI_USE_HASH_TREE", "false").lower() == "true",
        # Output
        "mining_output_dir": PROJECT_ROOT / os.getenv("MINING_OUTPUT_DIR", "outputs/frequent_itemsets"),
        "save_rules":     os.getenv("SAVE_RULES", "true").lower() == "true",
    }


# ══════════════════════════════════════════════════════════════════════════════
# Bước 1 – Preprocessing
# ══════════════════════════════════════════════════════════════════════════════

def run_preprocessing(cfg: dict) -> list:
    """
    Chạy pipeline tiền xử lý.
    Nếu đã có file processed, bỏ qua và load trực tiếp.
    """
    from src.mining import DatasetLoader

    processed_dir = cfg["output_dir"]
    pkl_file = processed_dir / "transaction_list.pkl"

    if pkl_file.exists():
        print("  [SKIP] Dữ liệu đã được xử lý trước – load trực tiếp từ cache.")
        loader = DatasetLoader(processed_dir)
        transactions = loader.load_transactions()
        print(f"  Đã load {len(transactions):,} giao dịch từ {processed_dir}")
        return transactions

    # Chưa có → chạy preprocessing
    from src.preprocessing.pipeline import PreprocessingPipeline
    pipeline = PreprocessingPipeline(
        raw_data_path=cfg["raw_data_path"],
        output_dir=processed_dir,
        min_support_count=cfg["min_support_count"],
        min_support_percentage=cfg["min_support_percentage"],
        min_items_per_transaction=cfg["min_items_per_transaction"],
    )
    pipeline.run()

    loader = DatasetLoader(processed_dir)
    return loader.load_transactions()


# ══════════════════════════════════════════════════════════════════════════════
# Bước 2 – Khai phá Frequent Itemsets
# ══════════════════════════════════════════════════════════════════════════════

def run_mining(transactions: list, cfg: dict) -> dict:
    """
    Chạy các thuật toán khai phá theo SELECTED_ALGORITHM.
    Trả về dict {algo_name: {'itemsets': ..., 'support_counts': ..., 'time': ...}}
    """
    from src.algorithms.apriori import Apriori
    from src.algorithms.fp_growth import FPGrowth

    algo = cfg["algorithm"]
    ms   = cfg["min_support"]
    ht   = cfg["use_hash_tree"]
    results = {}

    # ── Apriori ───────────────────────────────────────────────────────────────
    if algo in ("all", "apriori"):
        label = "Apriori+HashTree" if ht else "Apriori"
        print(f"\n  Đang chạy {label} (min_support={ms})...")
        t0 = time.perf_counter()
        apr = Apriori(min_support=ms, min_confidence=cfg["min_confidence"],
                      use_hash_tree=ht)
        fit_result = apr.fit(transactions)
        elapsed = time.perf_counter() - t0
        results["apriori"] = {
            "algo_obj":      apr,
            "itemsets":      fit_result["frequent_itemsets"],
            "support_counts": fit_result["support_counts"],
            "total_itemsets": fit_result["total_itemsets"],
            "time":          elapsed,
            "label":         label,
        }
        print(f"  ✓ {label}: {fit_result['total_itemsets']:,} itemsets | {elapsed:.2f}s")

    # ── FP-Growth ─────────────────────────────────────────────────────────────
    if algo in ("all", "fpgrowth"):
        print(f"\n  Đang chạy FP-Growth (min_support={ms})...")
        t0 = time.perf_counter()
        fp = FPGrowth(min_support=ms, min_confidence=cfg["min_confidence"])
        fit_result = fp.fit(transactions)
        elapsed = time.perf_counter() - t0
        results["fpgrowth"] = {
            "algo_obj":      fp,
            "itemsets":      fit_result["frequent_itemsets"],
            "support_counts": fit_result["support_counts"],
            "total_itemsets": fit_result["total_itemsets"],
            "time":          elapsed,
            "label":         "FP-Growth",
        }
        print(f"  ✓ FP-Growth: {fit_result['total_itemsets']:,} itemsets | {elapsed:.2f}s")

    return results


# ══════════════════════════════════════════════════════════════════════════════
# Bước 3 – Sinh Association Rules
# ══════════════════════════════════════════════════════════════════════════════

def run_rule_generation(mining_results: dict, cfg: dict) -> dict:
    """Sinh rules từ frequent itemsets của từng thuật toán."""
    rules_map = {}

    for key, res in mining_results.items():
        algo_obj = res["algo_obj"]
        t0 = time.perf_counter()
        rules = algo_obj.generate_rules()
        elapsed = time.perf_counter() - t0
        rules_map[key] = {"rules": rules, "time": elapsed, "label": res["label"]}
        print(f"  ✓ {res['label']}: {len(rules):,} rules | {elapsed:.2f}s")

    return rules_map


# ══════════════════════════════════════════════════════════════════════════════
# Bước 4 – Lưu kết quả
# ══════════════════════════════════════════════════════════════════════════════

def save_results(mining_results: dict, rules_map: dict, cfg: dict) -> None:
    """Lưu itemsets và rules ra file CSV."""
    import csv

    out_dir = cfg["mining_output_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)

    for key, res in mining_results.items():
        label = res["label"].replace("+", "_").replace(" ", "_")

        # Lưu frequent itemsets
        itemset_file = out_dir / f"itemsets_{label}.csv"
        with open(itemset_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["itemset", "size", "support_count"])
            for size, itemsets in res["itemsets"].items():
                for it in itemsets:
                    writer.writerow([" | ".join(it), size, res["support_counts"].get(it, 0)])
        print(f"  ✓ Itemsets → {itemset_file.name}")

        # Lưu rules
        if cfg["save_rules"] and key in rules_map:
            rules_file = out_dir / f"rules_{label}.csv"
            with open(rules_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["antecedent", "consequent", "support", "confidence", "lift"])
                for r in rules_map[key]["rules"]:
                    writer.writerow([
                        " | ".join(r["antecedent"]),
                        " | ".join(r["consequent"]),
                        r["support"],
                        round(r["confidence"], 6),
                        round(r["lift"], 6),
                    ])
            print(f"  ✓ Rules    → {rules_file.name}")


# ══════════════════════════════════════════════════════════════════════════════
# Bước 5 – Evaluation + Visualization
# ══════════════════════════════════════════════════════════════════════════════

def run_evaluation(mining_results: dict, rules_map: dict, cfg: dict) -> None:
    """In thống kê và vẽ biểu đồ so sánh."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
        HAS_MATPLOTLIB = True
    except ImportError:
        HAS_MATPLOTLIB = False
        print("  [SKIP] matplotlib chưa được cài – bỏ qua visualization.")

    N = len(mining_results)
    if N == 0:
        return

    # ── Bảng tóm tắt ──────────────────────────────────────────────────────────
    print()
    header = f"  {'Thuật toán':<22} {'Itemsets':>10} {'Rules':>8} {'Fit (s)':>10} {'Rule gen (s)':>14}"
    print(header)
    print("  " + "─" * 66)

    for key in mining_results:
        res   = mining_results[key]
        r_res = rules_map.get(key, {})
        label = res["label"]
        n_it  = res["total_itemsets"]
        n_ru  = len(r_res.get("rules", []))
        t_fit = res["time"]
        t_ru  = r_res.get("time", 0)
        print(f"  {label:<22} {n_it:>10,} {n_ru:>8,} {t_fit:>10.2f} {t_ru:>14.2f}")

    # Top-10 rules của thuật toán đầu tiên
    first_key = next(iter(rules_map))
    top_rules = sorted(rules_map[first_key]["rules"],
                       key=lambda r: r["confidence"], reverse=True)[:10]
    if top_rules:
        print(f"\n  Top 10 rules ({mining_results[first_key]['label']}) theo Confidence:")
        print("  " + "─" * 66)
        for i, r in enumerate(top_rules, 1):
            ant = ", ".join(r["antecedent"])
            con = ", ".join(r["consequent"])
            print(f"  {i:2}. {{{ant}}} → {{{con}}}")
            print(f"      conf={r['confidence']:.4f}  lift={r['lift']:.4f}  sup={r['support']}")

    if not HAS_MATPLOTLIB or N < 2:
        return

    # ── Biểu đồ so sánh ───────────────────────────────────────────────────────
    labels   = [r["label"] for r in mining_results.values()]
    t_fits   = [r["time"]  for r in mining_results.values()]
    n_items  = [r["total_itemsets"] for r in mining_results.values()]
    n_rules  = [len(rules_map.get(k, {}).get("rules", [])) for k in mining_results]

    colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"][:N]
    x = range(N)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(
        f"So sánh thuật toán  (min_support={cfg['min_support']}, min_confidence={cfg['min_confidence']})",
        fontsize=13, fontweight="bold"
    )

    def _bar(ax, values, title, ylabel):
        bars = ax.bar(labels, values, color=colors, alpha=0.85, width=0.5)
        for bar, v in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.01,
                    f"{v:.2f}s" if isinstance(v, float) else f"{v:,}",
                    ha="center", va="bottom", fontsize=10)
        ax.set_title(title, fontweight="bold")
        ax.set_ylabel(ylabel)
        ax.grid(axis="y", alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)

    _bar(axes[0], t_fits,  "Thời gian khai phá Itemsets", "Giây")
    _bar(axes[1], n_items, "Số Frequent Itemsets",        "Itemsets")
    _bar(axes[2], n_rules, "Số Association Rules",        "Rules")

    plt.tight_layout()
    out_png = cfg["mining_output_dir"] / "comparison.png"
    plt.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"\n  ✓ Biểu đồ → {out_png}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    pipeline_start = time.perf_counter()

    _header("ASSOCIATION RULE MINING PIPELINE")
    print(f"  Project root : {PROJECT_ROOT}")

    cfg = load_config()
    print(f"  Algorithm    : {cfg['algorithm'].upper()}")
    print(f"  min_support  : {cfg['min_support']}")
    print(f"  min_confidence: {cfg['min_confidence']}")
    print(f"  hash_tree    : {cfg['use_hash_tree']}")

    # ── Bước 1: Preprocessing ─────────────────────────────────────────────────
    _step(1, "Preprocessing → Transaction Format")
    transactions = run_preprocessing(cfg)
    print(f"  Tổng giao dịch: {len(transactions):,}")

    # ── Bước 2: Frequent Itemsets ─────────────────────────────────────────────
    _step(2, "Khai phá Frequent Itemsets")
    mining_results = run_mining(transactions, cfg)

    # ── Bước 3: Association Rules ─────────────────────────────────────────────
    _step(3, "Sinh Association Rules")
    rules_map = run_rule_generation(mining_results, cfg)

    # ── Bước 4: Lưu kết quả ───────────────────────────────────────────────────
    _step(4, "Lưu kết quả ra file")
    save_results(mining_results, rules_map, cfg)

    # ── Bước 5: Evaluation + Visualization ────────────────────────────────────
    _step(5, "Evaluation + Visualization")
    run_evaluation(mining_results, rules_map, cfg)

    # ── Tổng kết ──────────────────────────────────────────────────────────────
    total = time.perf_counter() - pipeline_start
    print()
    print("═" * 70)
    print(f"  Pipeline hoàn tất trong {total:.2f}s")
    print(f"  Output: {cfg['mining_output_dir']}")
    print("═" * 70)


if __name__ == "__main__":
    main()
