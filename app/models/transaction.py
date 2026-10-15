import uuid
from datetime import datetime
from app.extensions import db

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    reference_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'deposit', 'withdrawal', 'transfer_in', 'transfer_out'
    amount = db.Column(db.Float, nullable=False)
    balance_after = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    related_account = db.Column(db.String(30), nullable=True)  # recipient or sender account
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    @staticmethod
    def generate_reference():
        """Generate a unique transaction reference code."""
        return f"TXN-{uuid.uuid4().hex[:10].upper()}"

    def __repr__(self):
        return f'<Transaction {self.reference_id} [{self.transaction_type}] ${self.amount:,.2f}>'
