from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from app.extensions import db
from app.models.account import Account
from app.models.transaction import Transaction
from app.forms.banking_forms import DepositForm, WithdrawForm, TransferForm, CreateAccountForm
from app.utils.decorators import customer_required

banking_bp = Blueprint('banking', __name__)

@banking_bp.route('/dashboard')
@customer_required
def dashboard():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    
    # Calculate aggregate balance
    total_balance = sum(acc.balance for acc in accounts)
    
    # Collect recent transactions across all user accounts
    account_ids = [acc.id for acc in accounts]
    recent_transactions = Transaction.query.filter(
        Transaction.account_id.in_(account_ids)
    ).order_by(Transaction.timestamp.desc()).limit(10).all() if account_ids else []

    deposit_form = DepositForm()
    withdraw_form = WithdrawForm()
    transfer_form = TransferForm()
    new_account_form = CreateAccountForm()

    return render_template(
        'dashboard.html',
        accounts=accounts,
        total_balance=total_balance,
        recent_transactions=recent_transactions,
        deposit_form=deposit_form,
        withdraw_form=withdraw_form,
        transfer_form=transfer_form,
        new_account_form=new_account_form
    )

@banking_bp.route('/deposit', methods=['POST'])
@customer_required
def deposit():
    form = DepositForm()
    account_id = request.form.get('account_id', type=int)
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()

    if not account:
        flash('Target account not found or access denied.', 'danger')
        return redirect(url_for('banking.dashboard'))

    if form.validate_on_submit():
        amount = float(form.amount.data)
        try:
            new_balance = account.deposit(amount)
            
            txn = Transaction(
                reference_id=Transaction.generate_reference(),
                account_id=account.id,
                transaction_type='deposit',
                amount=amount,
                balance_after=new_balance,
                description=form.description.data or 'Direct Deposit',
                related_account='SELF-DEPOSIT'
            )
            db.session.add(txn)
            db.session.commit()

            flash(f'Successfully deposited ${amount:,.2f} into account #{account.account_number}. Current balance: ${new_balance:,.2f}', 'success')
        except ValueError as err:
            flash(str(err), 'danger')
    else:
        for error in form.amount.errors:
            flash(f'Deposit Error: {error}', 'danger')

    return redirect(url_for('banking.dashboard'))

@banking_bp.route('/withdraw', methods=['POST'])
@customer_required
def withdraw():
    form = WithdrawForm()
    account_id = request.form.get('account_id', type=int)
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()

    if not account:
        flash('Account not found.', 'danger')
        return redirect(url_for('banking.dashboard'))

    if form.validate_on_submit():
        amount = float(form.amount.data)
        try:
            new_balance = account.withdraw(amount)
            
            txn = Transaction(
                reference_id=Transaction.generate_reference(),
                account_id=account.id,
                transaction_type='withdrawal',
                amount=amount,
                balance_after=new_balance,
                description=form.description.data or 'Cash Withdrawal',
                related_account='ATM / E-CASH'
            )
            db.session.add(txn)
            db.session.commit()

            flash(f'Successfully withdrew ${amount:,.2f} from account #{account.account_number}. Remaining balance: ${new_balance:,.2f}', 'warning')
        except ValueError as err:
            flash(f'Withdrawal Failed: {str(err)}', 'danger')
    else:
        for error in form.amount.errors:
            flash(f'Withdrawal Error: {error}', 'danger')

    return redirect(url_for('banking.dashboard'))

@banking_bp.route('/transfer', methods=['POST'])
@customer_required
def transfer():
    form = TransferForm()
    sender_account_id = request.form.get('account_id', type=int)
    sender_account = Account.query.filter_by(id=sender_account_id, user_id=current_user.id).first()

    if not sender_account:
        flash('Sender account not found.', 'danger')
        return redirect(url_for('banking.dashboard'))

    if form.validate_on_submit():
        recipient_number = form.recipient_account.data.strip()
        amount = float(form.amount.data)

        # Validation 1: Prevent transferring to same account
        if recipient_number == sender_account.account_number:
            flash('Cannot transfer money to the same account.', 'danger')
            return redirect(url_for('banking.dashboard'))

        # Validation 2: Locate recipient account
        recipient_account = Account.query.filter_by(account_number=recipient_number).first()
        if not recipient_account:
            flash(f'Recipient account #{recipient_number} was not found. Please verify the account number.', 'danger')
            return redirect(url_for('banking.dashboard'))

        if recipient_account.status != 'active':
            flash('The recipient account is not active and cannot receive transfers.', 'danger')
            return redirect(url_for('banking.dashboard'))

        # Validation 3: Check funds
        if sender_account.balance < amount:
            flash(f'Transfer failed: Insufficient funds. Available balance: ${sender_account.balance:,.2f}', 'danger')
            return redirect(url_for('banking.dashboard'))

        try:
            # Atomic Transfer Execution
            sender_account.balance -= amount
            recipient_account.balance += amount

            tx_ref = Transaction.generate_reference()

            # Sender Ledger Entry
            sender_txn = Transaction(
                reference_id=tx_ref,
                account_id=sender_account.id,
                transaction_type='transfer_out',
                amount=amount,
                balance_after=sender_account.balance,
                description=f'Transfer to {recipient_account.owner.full_name or recipient_account.account_number}: {form.description.data}',
                related_account=recipient_account.account_number
            )
            # Recipient Ledger Entry
            recipient_txn = Transaction(
                reference_id=f"{tx_ref}-REC",
                account_id=recipient_account.id,
                transaction_type='transfer_in',
                amount=amount,
                balance_after=recipient_account.balance,
                description=f'Transfer from {sender_account.owner.full_name or sender_account.account_number}: {form.description.data}',
                related_account=sender_account.account_number
            )

            db.session.add(sender_txn)
            db.session.add(recipient_txn)
            db.session.commit()

            recipient_name = recipient_account.owner.full_name or recipient_account.owner.username
            flash(f'Successfully transferred ${amount:,.2f} to {recipient_name} (#{recipient_account.account_number}). Ref: {tx_ref}', 'success')
        except Exception as err:
            db.session.rollback()
            flash(f'Transfer failed due to system error: {str(err)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Transfer Error ({field}): {error}', 'danger')

    return redirect(url_for('banking.dashboard'))

@banking_bp.route('/accounts/create', methods=['POST'])
@customer_required
def create_account():
    form = CreateAccountForm()
    if form.validate_on_submit():
        initial_deposit = float(form.initial_deposit.data)
        account_num = Account.generate_account_number()
        
        new_account = Account(
            account_number=account_num,
            user_id=current_user.id,
            account_type=form.account_type.data,
            balance=initial_deposit,
            currency='USD',
            status='active'
        )
        db.session.add(new_account)
        db.session.flush()

        if initial_deposit > 0:
            txn = Transaction(
                reference_id=Transaction.generate_reference(),
                account_id=new_account.id,
                transaction_type='deposit',
                amount=initial_deposit,
                balance_after=initial_deposit,
                description='Opening Balance Deposit',
                related_account='APEX-RESERVE-001'
            )
            db.session.add(txn)

        db.session.commit()
        flash(f'New {new_account.account_type.title()} Account (#{account_num}) opened successfully with ${initial_deposit:,.2f}!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Account Creation Error: {error}', 'danger')

    return redirect(url_for('banking.dashboard'))

@banking_bp.route('/transactions')
@customer_required
def transactions():
    user_account_ids = [acc.id for acc in current_user.accounts]
    
    # Filter by transaction type if provided
    filter_type = request.args.get('type')
    query = Transaction.query.filter(Transaction.account_id.in_(user_account_ids))
    
    if filter_type:
        query = query.filter_by(transaction_type=filter_type)
        
    all_transactions = query.order_by(Transaction.timestamp.desc()).all() if user_account_ids else []

    return render_template(
        'transactions.html',
        transactions=all_transactions,
        filter_type=filter_type
    )
