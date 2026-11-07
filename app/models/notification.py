from datetime import datetime
from app.extensions import db

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(20), default='info', nullable=False)  # 'info', 'success', 'warning', 'danger'
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('notifications', lazy=True, order_by='desc(Notification.created_at)'))

    def __repr__(self):
        return f'<Notification {self.id} for User {self.user_id}: {self.title}>'
