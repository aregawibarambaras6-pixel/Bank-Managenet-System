from datetime import datetime
from app.extensions import db

class CurrencyRate(db.Model):
    __tablename__ = 'currency_rates'

    id = db.Column(db.Integer, primary_key=True)
    currency_code = db.Column(db.String(5), unique=True, nullable=False, index=True)
    currency_name = db.Column(db.String(50), nullable=False)
    symbol = db.Column(db.String(10), nullable=False, default='$')
    rate_to_usd = db.Column(db.Float, nullable=False, default=1.0)
    spread_pct = db.Column(db.Float, default=0.8, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_rate(cls, code):
        rate_obj = cls.query.filter_by(currency_code=code.upper(), is_active=True).first()
        return rate_obj.rate_to_usd if rate_obj else 1.0

    @classmethod
    def get_spread(cls, code):
        rate_obj = cls.query.filter_by(currency_code=code.upper(), is_active=True).first()
        return rate_obj.spread_pct if rate_obj else 0.8

    def __repr__(self):
        return f'<CurrencyRate {self.currency_code} = {self.rate_to_usd} USD (Spread: {self.spread_pct}%)>'

