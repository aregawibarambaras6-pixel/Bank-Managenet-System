from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SelectField, SubmitField, TelField
from wtforms.validators import DataRequired, NumberRange, Length


class CBCTransferForm(FlaskForm):
    """Transfer to another CBC bank account."""
    recipient_account = StringField('CBC Account Number', validators=[
        DataRequired(),
        Length(min=8, max=20, message='Account number must be 8-20 characters')
    ])
    amount = DecimalField('Amount (Birr)', validators=[
        DataRequired(),
        NumberRange(min=1.0, max=500000.0, message='Amount must be between 1.00 and 500,000.00 Birr')
    ])
    description = StringField('Remark', default='CBC Transfer', validators=[Length(max=100)])
    submit = SubmitField('Transfer to CBC Account')


class BeneficiaryForm(FlaskForm):
    """Add / manage beneficiary."""
    name = StringField('Beneficiary Full Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    account_number = StringField('Account Number', validators=[
        DataRequired(),
        Length(min=8, max=20)
    ])
    bank_name = SelectField('Bank', choices=[
        ('CBC Bank', 'CBC Bank'),
        ('Awash Bank', 'Awash Bank'),
        ('Dashen Bank', 'Dashen Bank'),
        ('Bank of Abyssinia', 'Bank of Abyssinia'),
        ('Wegagen Bank', 'Wegagen Bank'),
        ('Other', 'Other Bank')
    ], default='CBC Bank')
    submit = SubmitField('Save Beneficiary')


class OwnAccountTransferForm(FlaskForm):
    """Transfer between own accounts."""
    from_account = SelectField('From Account', coerce=int, validators=[DataRequired()])
    to_account = SelectField('To Account', coerce=int, validators=[DataRequired()])
    amount = DecimalField('Amount (Birr)', validators=[
        DataRequired(),
        NumberRange(min=1.0, max=500000.0)
    ])
    description = StringField('Remark', default='Own Account Transfer', validators=[Length(max=100)])
    submit = SubmitField('Transfer Between Accounts')


class CBCCashOutForm(FlaskForm):
    """CBC Cash-out via code (agent banking)."""
    phone_number = StringField('Receiver Phone Number', validators=[
        DataRequired(),
        Length(min=10, max=15, message='Enter a valid phone number')
    ])
    amount = DecimalField('Amount (Birr)', validators=[
        DataRequired(),
        NumberRange(min=10.0, max=25000.0, message='Amount must be between 10 and 25,000 Birr')
    ])
    submit = SubmitField('Generate Cash-Out Code')


class ATMCashOutForm(FlaskForm):
    """Cardless ATM cash-out."""
    amount = DecimalField('Amount (Birr)', validators=[
        DataRequired(),
        NumberRange(min=100.0, max=10000.0, message='ATM cash-out: 100 - 10,000 Birr')
    ])
    submit = SubmitField('Generate ATM Code')


class OtherBankTransferForm(FlaskForm):
    """Transfer to another bank."""
    bank_name = SelectField('Destination Bank', choices=[
        ('Awash Bank', 'Awash Bank'),
        ('Dashen Bank', 'Dashen Bank'),
        ('Bank of Abyssinia', 'Bank of Abyssinia'),
        ('Wegagen Bank', 'Wegagen Bank'),
        ('Nib International Bank', 'Nib International Bank'),
        ('Cooperative Bank of Oromia', 'Cooperative Bank of Oromia'),
        ('Bunna Bank', 'Bunna Bank'),
        ('Zemen Bank', 'Zemen Bank'),
    ], validators=[DataRequired()])
    recipient_account = StringField('Recipient Account Number', validators=[
        DataRequired(),
        Length(min=8, max=20)
    ])
    recipient_name = StringField('Recipient Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    amount = DecimalField('Amount (Birr)', validators=[
        DataRequired(),
        NumberRange(min=1.0, max=200000.0)
    ])
    description = StringField('Remark', default='Inter-Bank Transfer', validators=[Length(max=100)])
    submit = SubmitField('Send to Other Bank')


class AirtimeForm(FlaskForm):
    """Top-up airtime for mobile."""
    provider = SelectField('Service Provider', choices=[
        ('Ethio Telecom', 'Ethio Telecom'),
        ('Safaricom Ethiopia', 'Safaricom Ethiopia'),
    ], default='Ethio Telecom', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[
        DataRequired(),
        Length(min=10, max=15, message='Enter a valid phone number')
    ])
    amount = DecimalField('Amount (Birr)', validators=[
        DataRequired(),
        NumberRange(min=5.0, max=5000.0, message='Airtime: 5 - 5,000 Birr')
    ])
    submit = SubmitField('Buy Airtime')
