from datetime import datetime
import random
import string
from app.extensions import db

class FXConversion(db.Model):
    __tablename__ = 'fx_conversions'

    id = db.Column(db.Integer, primary_key=True)
    reference_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    from_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    to_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    from_currency = db.Column(db.String(5), nullable=False)
    to_currency = db.Column(db.String(5), nullable=False)
    from_amount = db.Column(db.Float, nullable=False)
    to_amount = db.Column(db.Float, nullable=False)
    exchange_rate = db.Column(db.Float, nullable=False)
    spread_fee = db.Column(db.Float, default=0.0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('fx_conversions', lazy=True, order_by='desc(FXConversion.created_at)'))
    from_account = db.relationship('Account', foreign_keys=[from_account_id])
    to_account = db.relationship('Account', foreign_keys=[to_account_id])

    @staticmethod
    def generate_reference():
        while True:
            code = ''.join(random.choices(string.digits, k=8))
            ref = f"FX-{code}"
            if not FXConversion.query.filter_by(reference_id=ref).first():
                return ref

    def __repr__(self):
        return f'<FXConversion {self.reference_id}: {self.from_amount} {self.from_currency} -> {self.to_amount} {self.to_currency} @ {self.exchange_rate}>'

