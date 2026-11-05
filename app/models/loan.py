from datetime import datetime
import random
import string
from app.extensions import db

class Loan(db.Model):
    __tablename__ = 'loans'

    id = db.Column(db.Integer, primary_key=True)
    loan_reference = db.Column(db.String(24), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    loan_type = db.Column(db.String(50), nullable=False, default='Personal Loan')
    amount = db.Column(db.Float, nullable=False)
    annual_rate = db.Column(db.Float, nullable=False, default=7.5)
    term_months = db.Column(db.Integer, nullable=False, default=12)
    monthly_payment = db.Column(db.Float, nullable=False, default=0.0)
    total_payable = db.Column(db.Float, nullable=False, default=0.0)
    total_interest = db.Column(db.Float, nullable=False, default=0.0)
    purpose = db.Column(db.String(255), nullable=False)
    monthly_income = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='PENDING', nullable=False)  # 'PENDING', 'APPROVED', 'REJECTED'
    manager_notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    user = db.relationship('User', backref=db.backref('loans', lazy=True, order_by='desc(Loan.created_at)'))
    account = db.relationship('Account', backref=db.backref('loans', lazy=True))

    @staticmethod
    def generate_loan_reference():
        """Generate unique loan reference, e.g. LN-83921045"""
        while True:
            code = ''.join(random.choices(string.digits, k=8))
            ref = f"LN-{code}"
            if not Loan.query.filter_by(loan_reference=ref).first():
                return ref

    def __repr__(self):
        return f'<Loan {self.loan_reference} [{self.loan_type}] ${self.amount:,.2f} - {self.status}>'

