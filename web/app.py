"""
Flask web app – Association Rule Mining Demo
"""

import os
import sys
import time
from pathlib import Path

# Đảm bảo import được src/
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
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


@app.route("/api/mine", methods=["POST"])
def api_mine():
    """Chạy thuật toán khai phá.
    Body: {"algorithm": "apriori|apriori_ht|fpgrowth",
           "min_support": 100, "min_confidence": 0.5}
    """
    data           = request.get_json(force=True)
    algorithm      = data.get("algorithm", "apriori")
    min_support    = int(data.get("min_support", 100))
    min_confidence = float(data.get("min_confidence", 0.5))
    use_hash_tree  = algorithm == "apriori_ht"

    if min_support < 1:
        return jsonify({"error": "min_support phải >= 1"}), 400
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
