from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(19), unique=True, nullable=False, index=True)
    card_holder = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    card_type = db.Column(db.String(20), default='virtual', nullable=False)   # 'virtual', 'physical'
    card_network = db.Column(db.String(20), default='Visa', nullable=False)   # 'Visa', 'Mastercard'
    card_design = db.Column(db.String(30), default='emerald', nullable=False) # 'emerald', 'navy', 'platinum', 'gold'
    cvv = db.Column(db.String(4), nullable=False)
    expiry_date = db.Column(db.String(7), nullable=False)                     # MM/YY
    pin_hash = db.Column(db.String(256), nullable=False)
    status = db.Column(db.String(20), default='active', nullable=False)       # 'active', 'frozen', 'blocked'
    daily_limit = db.Column(db.Float, default=2500.00, nullable=False)
    daily_spent = db.Column(db.Float, default=0.00, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('cards', lazy=True, order_by='desc(Card.created_at)'))
    account = db.relationship('Account', backref=db.backref('cards', lazy=True))

    def set_pin(self, pin_str):
        self.pin_hash = generate_password_hash(str(pin_str))

    def check_pin(self, pin_str):
        return check_password_hash(self.pin_hash, str(pin_str))

    @property
    def masked_number(self):
        """Returns standard masked card format: •••• •••• •••• 1234"""
        if len(self.card_number) >= 16:
            clean = self.card_number.replace(' ', '')
            last4 = clean[-4:]
            return f"•••• •••• •••• {last4}"
        return self.card_number

    @property
    def formatted_number(self):
        """Returns 16-digit card number in 4-digit groups."""
        clean = self.card_number.replace(' ', '')
        return f"{clean[:4]} {clean[4:8]} {clean[8:12]} {clean[12:16]}"

    @staticmethod
    def generate_card_number(network='Visa'):
        """Generate a realistic 16-digit card number."""
        while True:
            if network.lower() == 'mastercard':
                prefix = str(random.choice([51, 52, 53, 54, 55]))
            else:
                prefix = '4'
            
            remaining_digits = 16 - len(prefix)
            rest = ''.join([str(random.randint(0, 9)) for _ in range(remaining_digits)])
            candidate = f"{prefix}{rest}"
            
            formatted = f"{candidate[:4]} {candidate[4:8]} {candidate[8:12]} {candidate[12:16]}"
            if not Card.query.filter_by(card_number=formatted).first():
                return formatted

    @staticmethod
    def generate_cvv():
        return f"{random.randint(100, 999)}"

    @staticmethod
    def generate_expiry(years_ahead=3):
        future = datetime.utcnow() + timedelta(days=365 * years_ahead)
        return future.strftime("%m/%y")

    def __repr__(self):
        return f'<Card {self.masked_number} [{self.card_type.title()}] - {self.status.upper()}>'

