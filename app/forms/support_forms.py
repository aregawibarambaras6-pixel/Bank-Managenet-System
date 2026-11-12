from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class SupportTicketForm(FlaskForm):
    category = SelectField(
        'Inquiry Category',
        choices=[
            ('General Inquiry', 'General Banking & Services'),
            ('Transaction Dispute', 'Transaction Dispute / Charge Inquiry'),
            ('Card Security', 'Card Security & Fraud Concern'),
            ('Wire Transfer Issue', 'Wire Transfer Delay / Tracking'),
            ('Account Settings', 'Account Access & Security')
        ],
        default='General Inquiry',
        validators=[DataRequired()]
    )
    transaction_id = SelectField(
        'Associated Ledger Transaction (Optional)',
        coerce=int,
        choices=[(0, '-- None / Not a Transaction Dispute --')]
    )
    priority = SelectField(
        'Urgency Level',
        choices=[
            ('LOW', 'Low - General Questions'),
            ('MEDIUM', 'Medium - Account Issues'),
            ('HIGH', 'High - Card or Transfer Block'),
            ('CRITICAL', 'Critical - Suspected Fraud / Emergency')
        ],
        default='MEDIUM',
        validators=[DataRequired()]
    )
    subject = StringField(
        'Subject',
        validators=[
            DataRequired(),
            Length(min=5, max=150, message="Subject must be between 5 and 150 characters.")
        ]
    )
    message = TextAreaField(
        'Detailed Description',
        validators=[
            DataRequired(),
            Length(min=10, max=2500, message="Message must be between 10 and 2,500 characters.")
        ]
    )
    submit = SubmitField('Submit Support Ticket')


class ManagerTicketReplyForm(FlaskForm):
    status = SelectField(
        'Update Ticket Status',
        choices=[
            ('IN_PROGRESS', 'In Progress / Under Investigation'),
            ('RESOLVED', 'Resolved (Investigation Complete)'),
            ('CLOSED', 'Closed')
        ],
        validators=[DataRequired()]
    )
    reply = TextAreaField(
        'Official Branch Resolution / Response',
        validators=[
            DataRequired(message="Please provide a response before submitting."),
            Length(min=5, max=2500)
        ]
    )
    submit = SubmitField('Send Response & Update')
