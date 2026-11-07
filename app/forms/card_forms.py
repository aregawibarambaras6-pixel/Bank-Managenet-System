from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, PasswordField, SubmitField
from wtforms.validators import DataRequired, NumberRange, EqualTo, Regexp

class IssueCardForm(FlaskForm):
    account_id = SelectField(
        'Linked Bank Account',
        coerce=int,
        validators=[DataRequired(message="Please select an active account to link with this card.")]
    )
    card_type = SelectField(
        'Card Format',
        choices=[
            ('virtual', 'Instant Virtual Card (Online & Mobile Pay)'),
            ('physical', 'Physical Chip & Contactless Card (Delivery & ATM)')
        ],
        default='virtual',
        validators=[DataRequired()]
    )
    card_network = SelectField(
        'Payment Network',
        choices=[
            ('Visa', 'Visa Debit (Worldwide Acceptance)'),
            ('Mastercard', 'Mastercard World Debit')
        ],
        default='Visa',
        validators=[DataRequired()]
    )
    card_design = SelectField(
        'Card Design Edition',
        choices=[
            ('emerald', 'Emerald Prestige (Signature Deep Green)'),
            ('navy', 'Apex Navy (Executive Dark Navy)'),
            ('platinum', 'Platinum Titanium (Brushed Silver)'),
            ('gold', 'Apex Gold Reserve (Luxury Gold Hue)')
        ],
        default='emerald',
        validators=[DataRequired()]
    )
    daily_limit = DecimalField(
        'Daily Spending Limit ($)',
        default=2500.00,
        validators=[
            DataRequired(),
            NumberRange(min=50.00, max=25000.00, message="Daily limit must be between $50 and $25,000.")
        ]
    )
    pin = PasswordField(
        'Set 4-Digit Card PIN',
        validators=[
            DataRequired(message="PIN is required."),
            Regexp(r'^\d{4}$', message="PIN must be exactly 4 digits.")
        ]
    )
    confirm_pin = PasswordField(
        'Confirm 4-Digit PIN',
        validators=[
            DataRequired(),
            EqualTo('pin', message="PIN confirmation does not match.")
        ]
    )
    submit = SubmitField('Issue Card')


class UpdateCardLimitForm(FlaskForm):
    daily_limit = DecimalField(
        'New Daily Limit ($)',
        validators=[
            DataRequired(),
            NumberRange(min=50.00, max=50000.00, message="Limit must be between $50 and $50,000.")
        ]
    )
    submit = SubmitField('Update Limit')


class ChangeCardPinForm(FlaskForm):
    current_pin = PasswordField(
        'Current PIN',
        validators=[
            DataRequired(),
            Regexp(r'^\d{4}$', message="Current PIN must be 4 digits.")
        ]
    )
    new_pin = PasswordField(
        'New 4-Digit PIN',
        validators=[
            DataRequired(),
            Regexp(r'^\d{4}$', message="New PIN must be 4 digits.")
        ]
    )
    confirm_new_pin = PasswordField(
        'Confirm New PIN',
        validators=[
            DataRequired(),
            EqualTo('new_pin', message="PIN confirmation does not match.")
        ]
    )
    submit = SubmitField('Update PIN')
