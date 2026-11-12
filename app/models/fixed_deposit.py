from datetime import datetime, timedelta
import random
import string
from app.extensions import db

class FixedDeposit(db.Model):
    __tablename__ = 'fixed_deposits'

    id = db.Column(db.Integer, primary_key=True)
    deposit_reference = db.Column(db.String(24), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    plan_name = db.Column(db.String(60), nullable=False)
    principal_amount = db.Column(db.Float, nullable=False)
    annual_rate = db.Column(db.Float, nullable=False)  # e.g. 6.5
    term_months = db.Column(db.Integer, nullable=False) # e.g. 3, 6, 12, 24, 36
    projected_interest = db.Column(db.Float, nullable=False)
    maturity_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='active', nullable=False)  # 'active', 'matured', 'liquidated'
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    maturity_date = db.Column(db.DateTime, nullable=False)
    liquidated_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    user = db.relationship('User', backref=db.backref('fixed_deposits', lazy=True, order_by='desc(FixedDeposit.start_date)'))
    account = db.relationship('Account', backref=db.backref('fixed_deposits', lazy=True))

    @staticmethod
    def generate_reference():
        while True:
            code = ''.join(random.choices(string.digits, k=8))
            ref = f"FD-{code}"
            if not FixedDeposit.query.filter_by(deposit_reference=ref).first():
                return ref

    @property
    def is_matured(self):
        return datetime.utcnow() >= self.maturity_date and self.status == 'active'

    def __repr__(self):
        return f'<FixedDeposit {self.deposit_reference} [${self.principal_amount:,.2f} @ {self.annual_rate}%] - {self.status.upper()}>'
