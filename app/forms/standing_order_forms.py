from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

class StandingOrderForm(FlaskForm):
    source_account_id = SelectField(
        'Source Funding Account',
        coerce=int,
        validators=[DataRequired(message="Please select a funding account.")]
    )
    title = StringField(
        'Mandate Purpose / Label',
        validators=[
            DataRequired(message="Please specify a purpose for this standing order."),
            Length(min=3, max=100, message="Title must be between 3 and 100 characters.")
        ]
    )
    destination_type = SelectField(
        'Transfer Type',
        choices=[
            ('INTERNAL_TRANSFER', 'Internal Account / CBC Transfer'),
            ('EXTERNAL_BENEFICIARY', 'External Beneficiary Wire'),
            ('BILL_PAY', 'Automated Utility & Bill Payment')
        ],
        default='INTERNAL_TRANSFER',
        validators=[DataRequired()]
    )
    destination_account = StringField(
        'Target Account / Payee Number',
        validators=[
            DataRequired(message="Please enter the destination account number or payee reference."),
            Length(min=4, max=50)
        ]
    )
    amount = DecimalField(
        'Recurring Debit Amount',
        validators=[
            DataRequired(),
            NumberRange(min=5.0, max=50000.0, message="Recurring amount must be between $5.00 and $50,000.00.")
        ]
    )
    frequency = SelectField(
        'Execution Frequency',
        choices=[
            ('DAILY', 'Daily (Every 24 Hours)'),
            ('WEEKLY', 'Weekly (Every 7 Days)'),
            ('BI_WEEKLY', 'Bi-Weekly (Every 14 Days)'),
            ('MONTHLY', 'Monthly (Every 30 Days)'),
            ('QUARTERLY', 'Quarterly (Every 90 Days)')
        ],
        default='MONTHLY',
        validators=[DataRequired()]
    )
    submit = SubmitField('Activate Standing Order')
