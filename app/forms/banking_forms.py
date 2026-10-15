from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

class DepositForm(FlaskForm):
    amount = DecimalField('Deposit Amount ($)', validators=[
        DataRequired(),
        NumberRange(min=5.0, max=100000.0, message='Deposit must be between $5.00 and $100,000.00')
    ])
    description = StringField('Memo / Description', default='Digital Deposit', validators=[Length(max=100)])
    submit = SubmitField('Confirm Deposit')

class WithdrawForm(FlaskForm):
    amount = DecimalField('Withdrawal Amount ($)', validators=[
        DataRequired(),
        NumberRange(min=5.0, max=50000.0, message='Withdrawal must be between $5.00 and $50,000.00')
    ])
    description = StringField('Memo / Purpose', default='Cash Withdrawal', validators=[Length(max=100)])
    submit = SubmitField('Confirm Withdrawal')

class TransferForm(FlaskForm):
    recipient_account = StringField('Recipient Account Number', validators=[
        DataRequired(),
        Length(min=8, max=20, message='Account number must be 8-20 characters')
    ])
    amount = DecimalField('Transfer Amount ($)', validators=[
        DataRequired(),
        NumberRange(min=1.0, max=50000.0, message='Transfer amount must be between $1.00 and $50,000.00')
    ])
    description = StringField('Transfer Note', default='Instant Interbank Transfer', validators=[Length(max=100)])
    submit = SubmitField('Execute Wire Transfer')

class CreateAccountForm(FlaskForm):
    account_type = SelectField('Account Type', choices=[
        ('checking', 'Standard Checking Account'),
        ('savings', 'High-Yield Savings Account')
    ], default='checking')
    initial_deposit = DecimalField('Starting Balance ($)', validators=[
        DataRequired(),
        NumberRange(min=25.0, max=100000.0, message='Minimum initial deposit is $25.00')
    ], default=100.0)
    submit = SubmitField('Open New Account')
