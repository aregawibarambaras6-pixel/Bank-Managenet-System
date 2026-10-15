from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.forms.auth_forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_manager:
            return redirect(url_for('manager.dashboard'))
        return redirect(url_for('banking.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.login_id.data.strip()
        user = User.query.filter(
            (User.username.ilike(identifier)) | (User.email.ilike(identifier))
        ).first()

        raw_password = form.password.data
        if user and (user.check_password(raw_password) or user.check_password(raw_password.strip())):
            login_user(user, remember=form.remember_me.data)
            flash(f'Welcome back, {user.full_name or user.username}!', 'success')
            
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)

            # Strict 1-to-1 Portal Redirection based on role
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            elif user.is_manager:
                return redirect(url_for('manager.dashboard'))
            return redirect(url_for('banking.dashboard'))
        else:
            flash('Invalid username/email or password. Please try again.', 'danger')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('banking.dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        # 1. Create User
        user = User(
            full_name=form.full_name.data.strip(),
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            role='customer'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()  # Generates user.id before commit

        # 2. Automatically Provision Bank Account
        initial_amount = float(form.initial_deposit.data)
        account_num = Account.generate_account_number()
        account = Account(
            account_number=account_num,
            user_id=user.id,
            account_type=form.account_type.data,
            balance=initial_amount,
            currency='USD',
            status='active'
        )
        db.session.add(account)
        db.session.flush()

        # 3. Create Opening Deposit Transaction Record
        if initial_amount > 0:
            txn = Transaction(
                reference_id=Transaction.generate_reference(),
                account_id=account.id,
                transaction_type='deposit',
                amount=initial_amount,
                balance_after=initial_amount,
                description='Initial Account Opening Deposit',
                related_account='APEX-RESERVE-001'
            )
            db.session.add(txn)

        db.session.commit()
        login_user(user)

        flash(f'Congratulations {user.full_name}! Your account #{account_num} is active with a starting balance of ${initial_amount:,.2f}.', 'success')
        return redirect(url_for('banking.dashboard'))

    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been safely logged out of Apex Bank.', 'info')
    return redirect(url_for('main.index'))
