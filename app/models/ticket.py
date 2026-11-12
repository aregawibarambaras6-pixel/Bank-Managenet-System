from datetime import datetime
import random
import string
from app.extensions import db

class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'

    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(24), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=True)
    subject = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='General Inquiry')
    priority = db.Column(db.String(20), default='MEDIUM', nullable=False)  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    status = db.Column(db.String(20), default='OPEN', nullable=False)      # 'OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED'
    message = db.Column(db.Text, nullable=False)
    manager_reply = db.Column(db.Text, nullable=True)
    assigned_manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('tickets', lazy=True, order_by='desc(SupportTicket.created_at)'))
    transaction = db.relationship('Transaction', backref=db.backref('disputes', lazy=True))
    assigned_manager = db.relationship('User', foreign_keys=[assigned_manager_id])

    @staticmethod
    def generate_ticket_number():
        while True:
            code = ''.join(random.choices(string.digits, k=6))
            num = f"TKT-{code}"
            if not SupportTicket.query.filter_by(ticket_number=num).first():
                return num

    def __repr__(self):
        return f'<SupportTicket {self.ticket_number} [{self.category}] - {self.status}>'

