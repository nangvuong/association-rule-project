"""
Flask web app – Association Rule Mining Demo
"""

import os
import sys
import time
import tempfile
from pathlib import Path

# Đảm bảo import được src/
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import pandas as pd
from flask_cors import CORS

from models import db, Transaction, MiningRun, FrequentItemset, AssociationRule


# ── Khởi tạo app ──────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "arm-secret-dev-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql://arm_user:arm_password@localhost:5432/arm_db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100 MB max upload

db.init_app(app)

with app.app_context():
    db.create_all()


# ══════════════════════════════════════════════════════════════════════════════
# Helper: chạy thuật toán từ transactions trong DB
# ══════════════════════════════════════════════════════════════════════════════

def _get_transactions_from_db():
    rows = Transaction.query.all()
    return [set(r.items) for r in rows]


def _run_algorithm(algorithm: str, min_support: int, min_confidence: float,
                   use_hash_tree: bool):
    """Chạy thuật toán, lưu kết quả vào DB, trả về MiningRun.id"""
    from src.algorithms.apriori import Apriori
    from src.algorithms.fp_growth import FPGrowth

    transactions = _get_transactions_from_db()
    if not transactions:
        raise ValueError("Không có giao dịch nào trong database.")

    t0 = time.perf_counter()

    if algorithm in ("apriori", "apriori_ht"):
        algo = Apriori(min_support=min_support, min_confidence=min_confidence,
                       use_hash_tree=use_hash_tree)
    else:
        algo = FPGrowth(min_support=min_support, min_confidence=min_confidence)

    fit_result = algo.fit(transactions)
    rules_list = algo.generate_rules()
    elapsed = time.perf_counter() - t0

    # Lưu MiningRun
    run = MiningRun(
        algorithm=algorithm,
        min_support=min_support,
        min_confidence=min_confidence,
        use_hash_tree=use_hash_tree,
        n_transactions=len(transactions),
        n_itemsets=fit_result["total_itemsets"],
        n_rules=len(rules_list),
        exec_time=round(elapsed, 3),
    )
    db.session.add(run)
    db.session.flush()  # lấy run.id

    # Lưu frequent itemsets
    for size, itemsets in fit_result["frequent_itemsets"].items():
        for it in itemsets:
            db.session.add(FrequentItemset(
                run_id=run.id,
                itemset=list(it),
                size=size,
                support_count=fit_result["support_counts"].get(it, 0),
            ))

    # Lưu association rules
    for r in rules_list:
        db.session.add(AssociationRule(
            run_id=run.id,
            antecedent=list(r["antecedent"]),
            consequent=list(r["consequent"]),
            support=r["support"],
            confidence=r["confidence"],
            lift=r["lift"],
        ))

    db.session.commit()
    return run.id


# ══════════════════════════════════════════════════════════════════════════════
# Routes – Pages
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    total_tx    = Transaction.query.count()
    total_runs  = MiningRun.query.count()
    latest_runs = MiningRun.query.order_by(MiningRun.ran_at.desc()).limit(5).all()
    return render_template("index.html",
                           total_tx=total_tx,
                           total_runs=total_runs,
                           latest_runs=latest_runs)


@app.route("/transactions")
def transactions_page():
    page = request.args.get("page", 1, type=int)
    per_page = 20
    txs = Transaction.query.order_by(Transaction.created_at.desc()).paginate(
        page=page, per_page=per_page)
    return render_template("transactions.html", txs=txs)


@app.route("/mining")
def mining_page():
    runs = MiningRun.query.order_by(MiningRun.ran_at.desc()).all()
    return render_template("mining.html", runs=runs)


@app.route("/rules/<int:run_id>")
def rules_page(run_id):
    run = MiningRun.query.get_or_404(run_id)
    page = request.args.get("page", 1, type=int)
    sort = request.args.get("sort", "confidence")
    order_col = {
        "confidence": AssociationRule.confidence,
        "lift":       AssociationRule.lift,
        "support":    AssociationRule.support,
    }.get(sort, AssociationRule.confidence)

    rules = (AssociationRule.query
             .filter_by(run_id=run_id)
             .order_by(order_col.desc())
             .paginate(page=page, per_page=25))
    return render_template("rules.html", run=run, rules=rules, sort=sort)


# ══════════════════════════════════════════════════════════════════════════════
# Routes – API
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/api/transactions", methods=["POST"])
def api_add_transaction():
    """Thêm một hoặc nhiều giao dịch.
    Body JSON: {"invoice_no": "INV001", "items": ["ITEM A", "ITEM B"]}
    hoặc danh sách: [{"invoice_no": ..., "items": [...]}, ...]
    """
    data = request.get_json(force=True)
    if isinstance(data, dict):
        data = [data]

    added = []
    for row in data:
        invoice_no = row.get("invoice_no", "").strip()
        items      = row.get("items", [])
        if not invoice_no or not items:
            return jsonify({"error": "Thiếu invoice_no hoặc items"}), 400

        tx = Transaction(invoice_no=invoice_no,
                         items=[str(i).strip().upper() for i in items],
                         source=row.get("source", "manual"))
        db.session.add(tx)
        added.append(invoice_no)

    db.session.commit()
    return jsonify({"added": len(added), "invoices": added}), 201


@app.route("/api/transactions/<int:tx_id>", methods=["DELETE"])
def api_delete_transaction(tx_id):
    tx = Transaction.query.get_or_404(tx_id)
    db.session.delete(tx)
    db.session.commit()
    return jsonify({"deleted": tx_id})


@app.route("/api/transactions/import", methods=["POST"])
def api_import_transactions():
    """Import từ file processed (transaction_list.pkl) vào DB."""
    import pickle
    pkl = PROJECT_ROOT / "data" / "processed" / "transaction_list.pkl"
    if not pkl.exists():
        return jsonify({"error": "Chưa có file processed. Hãy chạy preprocessing trước."}), 404

    with open(pkl, "rb") as f:
        tx_list = pickle.load(f)

    # Xóa transactions cũ được import
    Transaction.query.filter_by(source="imported").delete()
    db.session.commit()

    for i, items in enumerate(tx_list, 1):
        db.session.add(Transaction(
            invoice_no=f"IMP-{i:06d}",
            items=sorted(list(items)),
            source="imported",
        ))
    db.session.commit()
    return jsonify({"imported": len(tx_list)})


@app.route("/api/transactions/upload", methods=["POST"])
def api_upload_transactions():
    """Upload và xử lý file giao dịch dạng UCI (xlsx/csv).
    Thực hiện các bước tiền xử lý tương tự eda.ipynb:
      1. Load data
      2. Clean: xóa missing, cancelled, invalid price, duplicates, empty description
      3. Filter rare items
      4. Transform: group by Invoice → transaction list
      5. Import vào DB
    """
    if "file" not in request.files:
        return jsonify({"error": "Không tìm thấy file trong request."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Chưa chọn file."}), 400

    filename = file.filename.lower()
    if not (filename.endswith(".xlsx") or filename.endswith(".xls") or filename.endswith(".csv")):
        return jsonify({"error": "Chỉ hỗ trợ file .xlsx, .xls hoặc .csv"}), 400

    # Read params
    min_support_count = int(request.form.get("min_support_count", 50))
    min_support_pct = float(request.form.get("min_support_percentage", 0.1))
    min_items = int(request.form.get("min_items_per_transaction", 2))
    replace_old = request.form.get("replace_old", "true").lower() == "true"

    # Save to temp file and load with pandas
    upload_dir = PROJECT_ROOT / "data" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = upload_dir / file.filename
    file.save(str(tmp_path))

    try:
        # ── STEP 1: Load ──────────────────────────────────────────────
        if filename.endswith(".csv"):
            df = pd.read_csv(str(tmp_path))
        else:
            df = pd.read_excel(str(tmp_path))

        original_rows = len(df)

        # Validate required columns
        required_cols = {"Invoice", "Description"}
        existing_cols = set(df.columns)
        missing_cols = required_cols - existing_cols
        if missing_cols:
            return jsonify({
                "error": f"File thiếu các cột bắt buộc: {', '.join(missing_cols)}. "
                         f"Cần ít nhất: Invoice, Description. "
                         f"Các cột hiện có: {', '.join(df.columns.tolist())}"
            }), 400

        stats = {"original_rows": original_rows, "columns": df.columns.tolist()}

        # ── STEP 2: Clean ─────────────────────────────────────────────
        df_clean = df.copy()
        cleaning_steps = []

        # 2a. Remove missing Invoice / Description
        before = len(df_clean)
        drop_subset = ["Invoice", "Description"]
        if "Customer ID" in df_clean.columns:
            drop_subset.append("Customer ID")
        df_clean = df_clean.dropna(subset=drop_subset)
        removed = before - len(df_clean)
        cleaning_steps.append({"step": "Xóa dòng thiếu dữ liệu (Invoice/Description/Customer ID)",
                               "removed": removed, "remaining": len(df_clean)})

        # 2b. Remove cancelled transactions
        before = len(df_clean)
        df_clean = df_clean[~df_clean["Invoice"].astype(str).str.startswith("C")]
        if "Quantity" in df_clean.columns:
            df_clean = df_clean[df_clean["Quantity"] > 0]
        removed = before - len(df_clean)
        cleaning_steps.append({"step": "Xóa giao dịch bị hủy (Invoice bắt đầu bằng 'C', Quantity ≤ 0)",
                               "removed": removed, "remaining": len(df_clean)})

        # 2c. Remove non-positive prices
        if "Price" in df_clean.columns:
            before = len(df_clean)
            df_clean = df_clean[df_clean["Price"] > 0]
            removed = before - len(df_clean)
            cleaning_steps.append({"step": "Xóa dòng có giá ≤ 0",
                                   "removed": removed, "remaining": len(df_clean)})

        # 2d. Remove duplicates
        before = len(df_clean)
        dedup_cols = ["Invoice"]
        if "StockCode" in df_clean.columns:
            dedup_cols.append("StockCode")
        if "Customer ID" in df_clean.columns:
            dedup_cols.append("Customer ID")
        if len(dedup_cols) > 1:
            df_clean = df_clean.drop_duplicates(subset=dedup_cols, keep="first")
        removed = before - len(df_clean)
        cleaning_steps.append({"step": "Xóa dòng trùng lặp",
                               "removed": removed, "remaining": len(df_clean)})

        # 2e. Clean descriptions
        before = len(df_clean)
        df_clean["Description"] = df_clean["Description"].astype(str).str.strip()
        df_clean = df_clean[df_clean["Description"].str.len() > 0]
        df_clean = df_clean[df_clean["Description"] != "nan"]
        removed = before - len(df_clean)
        cleaning_steps.append({"step": "Xóa mô tả trống / chỉ có khoảng trắng",
                               "removed": removed, "remaining": len(df_clean)})

        stats["cleaning"] = cleaning_steps
        stats["cleaned_rows"] = len(df_clean)

        if len(df_clean) == 0:
            return jsonify({"error": "Sau khi làm sạch, không còn dòng dữ liệu nào.", "stats": stats}), 400

        # ── STEP 3: Filter rare items ─────────────────────────────────
        item_counts = df_clean["Description"].value_counts()
        total_unique_items_before = len(item_counts)
        min_count_relative = int(len(df_clean) * (min_support_pct / 100))
        threshold = max(min_support_count, min_count_relative)

        rare_items = item_counts[item_counts < threshold].index.tolist()
        common_items = item_counts[item_counts >= threshold].index.tolist()

        before = len(df_clean)
        df_clean = df_clean[df_clean["Description"].isin(common_items)]
        removed = before - len(df_clean)

        stats["filtering"] = {
            "threshold": threshold,
            "total_unique_items_before": total_unique_items_before,
            "rare_items_removed": len(rare_items),
            "common_items_kept": len(common_items),
            "rows_removed": removed,
            "remaining": len(df_clean),
        }

        if len(df_clean) == 0:
            return jsonify({"error": "Sau khi lọc item hiếm, không còn dòng dữ liệu nào.",
                            "stats": stats}), 400

        # ── STEP 4: Transform to transactions ─────────────────────────
        transactions_df = df_clean.groupby("Invoice")["Description"].apply(list).reset_index()
        transactions_df.columns = ["Invoice", "Items"]
        total_before_filter = len(transactions_df)

        # Filter by min items
        transactions_df = transactions_df[transactions_df["Items"].apply(len) >= min_items]
        transaction_list = [set(items) for items in transactions_df["Items"]]

        avg_items = sum(len(t) for t in transaction_list) / max(len(transaction_list), 1)

        stats["transformation"] = {
            "total_invoices": total_before_filter,
            "after_min_items_filter": len(transaction_list),
            "removed_short_transactions": total_before_filter - len(transaction_list),
            "min_items": min_items,
            "avg_items_per_transaction": round(avg_items, 2),
            "unique_items": len(set().union(*transaction_list)) if transaction_list else 0,
        }

        if not transaction_list:
            return jsonify({"error": "Sau khi chuyển đổi, không có giao dịch hợp lệ nào.",
                            "stats": stats}), 400

        # ── STEP 5: Import vào DB ─────────────────────────────────────
        if replace_old:
            deleted = Transaction.query.filter_by(source="file_upload").delete()
            db.session.commit()
            stats["deleted_old"] = deleted

        invoices = transactions_df["Invoice"].astype(str).tolist()
        for i, (inv, items) in enumerate(zip(invoices, transaction_list)):
            db.session.add(Transaction(
                invoice_no=str(inv),
                items=sorted(list(items)),
                source="file_upload",
            ))

        db.session.commit()

        stats["imported"] = len(transaction_list)
        stats["sample_transactions"] = [
            {"invoice": str(invoices[i]), "items": sorted(list(transaction_list[i]))[:10],
             "total_items": len(transaction_list[i])}
            for i in range(min(5, len(transaction_list)))
        ]

        return jsonify(stats), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Lỗi xử lý file: {str(e)}"}), 500
    finally:
        # Clean up temp file
        if tmp_path.exists():
            tmp_path.unlink()


@app.route("/api/mine", methods=["POST"])
def api_mine():
    """Chạy thuật toán khai phá.
    Body: {"algorithm": "apriori_ht",
           "min_support_pct": 1.07, "min_confidence": 0.6}
    """
    import math

    data           = request.get_json(force=True)
    algorithm      = data.get("algorithm", "apriori_ht")
    min_confidence = float(data.get("min_confidence", 0.6))
    use_hash_tree  = algorithm in ("apriori_ht", "apriori")

    # Tính min_support từ phần trăm
    n_transactions = Transaction.query.count()
    if n_transactions == 0:
        return jsonify({"error": "Không có giao dịch nào trong database."}), 400

    min_support_pct = float(data.get("min_support_pct", 1.07))
    min_support = max(1, math.ceil(n_transactions * min_support_pct / 100))

    if not (0 < min_confidence <= 1):
        return jsonify({"error": "min_confidence phải trong (0, 1]"}), 400

    try:
        run_id = _run_algorithm(algorithm, min_support, min_confidence, use_hash_tree)
        run    = MiningRun.query.get(run_id)
        return jsonify({
            "run_id":     run_id,
            "algorithm":  run.algorithm,
            "n_itemsets": run.n_itemsets,
            "n_rules":    run.n_rules,
            "exec_time":  run.exec_time,
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Lỗi thuật toán: {e}"}), 500


@app.route("/api/runs", methods=["GET"])
def api_runs():
    runs = MiningRun.query.order_by(MiningRun.ran_at.desc()).limit(20).all()
    return jsonify([r.to_dict() for r in runs])


@app.route("/api/runs/<int:run_id>", methods=["DELETE"])
def api_delete_run(run_id):
    run = MiningRun.query.get_or_404(run_id)
    db.session.delete(run)
    db.session.commit()
    return jsonify({"deleted": run_id})


@app.route("/api/rules/<int:run_id>", methods=["GET"])
def api_rules(run_id):
    limit = request.args.get("limit", 50, type=int)
    sort  = request.args.get("sort", "confidence")
    order_col = {
        "confidence": AssociationRule.confidence,
        "lift":       AssociationRule.lift,
        "support":    AssociationRule.support,
    }.get(sort, AssociationRule.confidence)

    rules = (AssociationRule.query
             .filter_by(run_id=run_id)
             .order_by(order_col.desc())
             .limit(limit).all())
    return jsonify([r.to_dict() for r in rules])


@app.route("/api/stats", methods=["GET"])
def api_stats():
    return jsonify({
        "total_transactions": Transaction.query.count(),
        "total_runs":         MiningRun.query.count(),
        "total_rules":        AssociationRule.query.count(),
        "total_itemsets":     FrequentItemset.query.count(),
    })


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
