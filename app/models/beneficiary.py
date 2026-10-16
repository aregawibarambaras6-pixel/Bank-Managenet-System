from datetime import datetime
from app.extensions import db


class Beneficiary(db.Model):
    """Saved beneficiary accounts for quick transfers."""
    __tablename__ = 'beneficiaries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(20), nullable=False)
    bank_name = db.Column(db.String(100), default='CBC Bank', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Beneficiary {self.name} - {self.account_number}>'
