from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

LOAN_TYPE_RATES = {
    'Personal Loan': 8.5,
    'Home Mortgage': 6.2,
    'Auto Loan': 7.0,
    'Business Loan': 9.0,
    'Education Loan': 5.5,
}

class LoanApplicationForm(FlaskForm):
    account_id = SelectField(
        'Disbursement Account',
        coerce=int,
        validators=[DataRequired(message="Please select an account for loan disbursal.")]
    )
    loan_type = SelectField(
        'Loan Category',
        choices=[
            ('Personal Loan', 'Personal Loan (Fixed 8.5% APR)'),
            ('Home Mortgage', 'Home Mortgage Loan (Fixed 6.2% APR)'),
            ('Auto Loan', 'Auto Vehicle Loan (Fixed 7.0% APR)'),
            ('Business Loan', 'Small Business Loan (Fixed 9.0% APR)'),
            ('Education Loan', 'Higher Education Loan (Fixed 5.5% APR)')
        ],
        default='Personal Loan',
        validators=[DataRequired()]
    )
    amount = DecimalField(
        'Loan Amount Requested ($)',
        validators=[
            DataRequired(message="Please specify a loan amount."),
            NumberRange(min=500, max=500000, message="Loan amount must be between $500 and $500,000.")
        ]
    )
    term_months = SelectField(
        'Repayment Term',
        coerce=int,
        choices=[
            (6, '6 Months'),
            (12, '12 Months (1 Year)'),
            (24, '24 Months (2 Years)'),
            (36, '36 Months (3 Years)'),
            (48, '48 Months (4 Years)'),
            (60, '60 Months (5 Years)'),
            (120, '120 Months (10 Years)')
        ],
        default=12,
        validators=[DataRequired()]
    )
    monthly_income = DecimalField(
        'Verified Monthly Income ($)',
        validators=[
            DataRequired(message="Monthly income is required for credit assessment."),
            NumberRange(min=500, message="Monthly income must be at least $500.")
        ]
    )
    purpose = StringField(
        'Loan Purpose / Intended Use',
        validators=[
            DataRequired(message="Please provide the purpose for this loan."),
            Length(min=5, max=255, message="Purpose must be between 5 and 255 characters.")
        ]
    )
    submit = SubmitField('Submit Loan Application')


class LoanReviewForm(FlaskForm):
    decision = SelectField(
        'Review Decision',
        choices=[('APPROVE', 'Approve & Disburse Funds'), ('REJECT', 'Reject Application')],
        validators=[DataRequired()]
    )
    manager_notes = TextAreaField(
        'Underwriter / Manager Notes',
        validators=[Length(max=255, message="Notes cannot exceed 255 characters.")]
    )
    submit = SubmitField('Submit Decision')

