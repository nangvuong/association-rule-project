"""
Database models và khởi tạo schema cho ARM web app.
"""

import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Text, Integer, Float, DateTime, JSON, Boolean, ForeignKey, String
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class Transaction(db.Model):
    __tablename__ = "transactions"

    id         = db.Column(Integer, primary_key=True)
    invoice_no = db.Column(String(50), nullable=False, index=True)
    items      = db.Column(JSON, nullable=False)        # ["ITEM A", "ITEM B", ...]
    source     = db.Column(String(20), default="manual") # 'imported' | 'manual'
    created_at = db.Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "invoice_no": self.invoice_no,
            "items": self.items,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
        }


class MiningRun(db.Model):
    __tablename__ = "mining_runs"

    id             = db.Column(Integer, primary_key=True)
    algorithm      = db.Column(String(30), nullable=False)   # apriori | apriori_ht | fpgrowth
    min_support    = db.Column(Integer, nullable=False)
    min_confidence = db.Column(Float, nullable=False)
    use_hash_tree  = db.Column(Boolean, default=False)
    n_transactions = db.Column(Integer)
    n_itemsets     = db.Column(Integer)
    n_rules        = db.Column(Integer)
    exec_time      = db.Column(Float)                        # seconds
    ran_at         = db.Column(DateTime, default=datetime.utcnow)

    itemsets = relationship("FrequentItemset", backref="run",
                            cascade="all, delete-orphan", lazy="dynamic")
    rules    = relationship("AssociationRule", backref="run",
                            cascade="all, delete-orphan", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "algorithm": self.algorithm,
            "min_support": self.min_support,
            "min_confidence": self.min_confidence,
            "use_hash_tree": self.use_hash_tree,
            "n_transactions": self.n_transactions,
            "n_itemsets": self.n_itemsets,
            "n_rules": self.n_rules,
            "exec_time": self.exec_time,
            "ran_at": self.ran_at.isoformat(),
        }


class FrequentItemset(db.Model):
    __tablename__ = "frequent_itemsets"

    id            = db.Column(Integer, primary_key=True)
    run_id        = db.Column(Integer, ForeignKey("mining_runs.id"), nullable=False, index=True)
    itemset       = db.Column(JSON, nullable=False)    # ["ITEM A", "ITEM B"]
    size          = db.Column(Integer, nullable=False)
    support_count = db.Column(Integer, nullable=False)


class AssociationRule(db.Model):
    __tablename__ = "association_rules"

    id         = db.Column(Integer, primary_key=True)
    run_id     = db.Column(Integer, ForeignKey("mining_runs.id"), nullable=False, index=True)
    antecedent = db.Column(JSON, nullable=False)
    consequent = db.Column(JSON, nullable=False)
    support    = db.Column(Integer, nullable=False)
    confidence = db.Column(Float, nullable=False)
    lift       = db.Column(Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "run_id": self.run_id,
            "antecedent": self.antecedent,
            "consequent": self.consequent,
            "support": self.support,
            "confidence": round(self.confidence, 4),
            "lift": round(self.lift, 4),
        }
