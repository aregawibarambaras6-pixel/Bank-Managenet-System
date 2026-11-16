from datetime import datetime, timedelta
import random
import string
from app.extensions import db

class StandingOrder(db.Model):
    __tablename__ = 'standing_orders'

    id = db.Column(db.Integer, primary_key=True)
    order_reference = db.Column(db.String(24), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    source_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    destination_type = db.Column(db.String(30), nullable=False, default='INTERNAL_TRANSFER')
    destination_account = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(20), nullable=False, default='MONTHLY')  # 'DAILY', 'WEEKLY', 'BI_WEEKLY', 'MONTHLY', 'QUARTERLY'
    status = db.Column(db.String(20), default='ACTIVE', nullable=False)  # 'ACTIVE', 'PAUSED', 'CANCELLED', 'COMPLETED'
    next_execution_date = db.Column(db.DateTime, nullable=False)
    last_execution_date = db.Column(db.DateTime, nullable=True)
    total_executions = db.Column(db.Integer, default=0, nullable=False)
    total_transferred = db.Column(db.Float, default=0.0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('standing_orders', lazy=True, order_by='desc(StandingOrder.created_at)'))
    source_account = db.relationship('Account', backref=db.backref('standing_orders', lazy=True))

    @staticmethod
    def generate_reference():
        while True:
            code = ''.join(random.choices(string.digits, k=6))
            ref = f"SO-{code}"
            if not StandingOrder.query.filter_by(order_reference=ref).first():
                return ref

    def calculate_next_date(self, from_date=None):
        base = from_date or datetime.utcnow()
        freq = self.frequency.upper()
        if freq == 'DAILY':
            return base + timedelta(days=1)
        elif freq == 'WEEKLY':
            return base + timedelta(days=7)
        elif freq == 'BI_WEEKLY':
            return base + timedelta(days=14)
        elif freq == 'MONTHLY':
            return base + timedelta(days=30)
        elif freq == 'QUARTERLY':
            return base + timedelta(days=90)
        return base + timedelta(days=30)

    @property
    def is_due(self):
        return self.status == 'ACTIVE' and datetime.utcnow() >= self.next_execution_date

    def __repr__(self):
        return f'<StandingOrder {self.order_reference} [{self.title}] ${self.amount:,.2f} ({self.frequency}) - {self.status}>'

