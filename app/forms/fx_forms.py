from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class FXExchangeForm(FlaskForm):
    source_account_id = SelectField(
        'Source Currency Account',
        coerce=int,
        validators=[DataRequired(message="Please select a source account.")]
    )
    destination_account_id = SelectField(
        'Target Destination Account',
        coerce=int,
        validators=[DataRequired(message="Please select a destination account.")]
    )
    amount = DecimalField(
        'Exchange Amount',
        validators=[
            DataRequired(message="Please enter an amount to convert."),
            NumberRange(min=1.0, max=250000.0, message="Conversion amount must be between 1.00 and 250,000.00.")
        ]
    )
    submit = SubmitField('Execute Instant Exchange')

class AdminFXRateUpdateForm(FlaskForm):
    currency_code = StringField('Currency Code', validators=[DataRequired()])
    rate_to_usd = DecimalField(
        'Exchange Rate (USD Equivalent)',
        validators=[
            DataRequired(),
            NumberRange(min=0.00001, max=10000.0, message="Valid exchange rate required.")
        ]
    )
    spread_pct = DecimalField(
        'Institutional Spread Markup (%)',
        validators=[
            DataRequired(),
            NumberRange(min=0.0, max=20.0, message="Spread must be between 0.0% and 20.0%.")
        ]
    )
    submit = SubmitField('Save Exchange Rate')

