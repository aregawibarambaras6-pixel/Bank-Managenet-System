from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange

DEPOSIT_PLANS = {
    '3m': {'name': 'Growth 3-Month Certificate', 'rate': 4.8, 'months': 3},
    '6m': {'name': 'Prestige 6-Month Certificate', 'rate': 5.5, 'months': 6},
    '12m': {'name': 'Prime 1-Year Certificate', 'rate': 6.2, 'months': 12},
    '24m': {'name': 'Apex Treasury 2-Year Certificate', 'rate': 7.0, 'months': 24},
    '36m': {'name': 'Apex Ultra 3-Year Certificate', 'rate': 7.8, 'months': 36}
}

class OpenDepositForm(FlaskForm):
    account_id = SelectField(
        'Source Funding Account',
        coerce=int,
        validators=[DataRequired(message="Please select an account to fund this deposit.")]
    )
    plan = SelectField(
        'Investment Term & Guaranteed Yield',
        choices=[
            ('3m', 'Growth 3-Month Plan (4.8% APY)'),
            ('6m', 'Prestige 6-Month Plan (5.5% APY)'),
            ('12m', 'Prime 1-Year Plan (6.2% APY)'),
            ('24m', 'Apex Treasury 2-Year Plan (7.0% APY)'),
            ('36m', 'Apex Ultra 3-Year Plan (7.8% APY)')
        ],
        default='12m',
        validators=[DataRequired()]
    )
    amount = DecimalField(
        'Deposit Principal ($)',
        validators=[
            DataRequired(),
            NumberRange(min=500.00, max=500000.00, message="Deposit must be between $500 and $500,000.")
        ]
    )
    submit = SubmitField('Lock & Open Deposit')

