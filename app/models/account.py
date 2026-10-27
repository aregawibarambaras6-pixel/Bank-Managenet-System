import random
from datetime import datetime
from app.extensions import db

class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_type = db.Column(db.String(20), default='checking', nullable=False)  # 'checking', 'savings'
    balance = db.Column(db.Float, default=0.0, nullable=False)
    currency = db.Column(db.String(5), default='USD', nullable=False)
    status = db.Column(db.String(20), default='active', nullable=False)  # 'active', 'frozen', 'closed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    transactions = db.relationship('Transaction', backref='account', lazy=True, cascade='all, delete-orphan', order_by='desc(Transaction.timestamp)')

    @staticmethod
    def generate_account_number():
        """Generate unique 13-digit CBC bank account number starting with 1000 (e.g. 1000547919649)."""
        while True:
            number = f"1000{random.randint(100000000, 999999999)}"
            if not Account.query.filter_by(account_number=number).first():
                return number

    def deposit(self, amount, description="Deposit"):
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")
        if self.status != 'active':
            raise ValueError("Account is not active.")
        
        self.balance += amount
        return self.balance

    def withdraw(self, amount, description="Withdrawal"):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than zero.")
        if self.status != 'active':
            raise ValueError("Account is not active.")
        if self.balance < amount:
            raise ValueError("Insufficient balance.")
        
        self.balance -= amount
        return self.balance

    def __repr__(self):
        return f'<Account {self.account_number} ({self.account_type}) - ${self.balance:,.2f}>'
