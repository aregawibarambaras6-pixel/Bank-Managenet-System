from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange
from app.models.user import User

class LoginForm(FlaskForm):
    login_id = StringField('Username or Email', validators=[DataRequired(), Length(min=3, max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    account_type = SelectField('Account Type', choices=[('checking', 'Checking Account (Everyday Banking)'), ('savings', 'High-Yield Savings Account (4.5% APY)')], default='checking')
    initial_deposit = DecimalField('Initial Deposit ($)', validators=[DataRequired(), NumberRange(min=25, max=50000, message='Initial deposit must be between $25 and $50,000')], default=500.0)
    submit = SubmitField('Create Banking Account')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data.strip()).first():
            raise ValidationError('This username is already taken. Please choose another.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.strip().lower()).first():
            raise ValidationError('An account with this email address already exists.')
