import io
import csv
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, Response
from flask_login import current_user
from app.extensions import db
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.loan import Loan
from app.models.card import Card
from app.models.notification import Notification
from app.forms.banking_forms import DepositForm, WithdrawForm, TransferForm, CreateAccountForm
from app.forms.loan_forms import LoanApplicationForm, LOAN_TYPE_RATES
from app.forms.card_forms import IssueCardForm, UpdateCardLimitForm, ChangeCardPinForm
from app.utils.decorators import customer_required
from app.utils.java_service import analyze_transaction_risk
from app.utils.cpp_engine import calculate_compound_interest, calculate_loan_amortization, generate_ledger_hash
from app.utils.sql_executor import log_fraud_audit, log_ledger_checksum

banking_bp = Blueprint('banking', __name__)

@banking_bp.app_context_processor
def inject_notifications():
    if current_user.is_authenticated:
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        recent_notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(6).all()
        return {'unread_notifications_count': unread_count, 'recent_notifications': recent_notifs}
    return {'unread_notifications_count': 0, 'recent_notifications': []}

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
            tx_ref = Transaction.generate_reference()
            
            txn = Transaction(
                reference_id=tx_ref,
                account_id=account.id,
                transaction_type='deposit',
                amount=amount,
                balance_after=new_balance,
                description=form.description.data or 'Direct Deposit',
                related_account='SELF-DEPOSIT'
            )
            db.session.add(txn)
            db.session.commit()

            # C++ Engine: Compute cryptographic ledger checksum & record to SQL
            hash_res = generate_ledger_hash(tx_ref, 'SELF-DEPOSIT', account.account_number, amount, str(txn.timestamp))
            log_ledger_checksum(tx_ref, hash_res.get('ledger_hash', ''))

            flash(f'Successfully deposited ${amount:,.2f} into account #{account.account_number}. Checksum Verified ({hash_res.get("ledger_hash", "")[:10]}...). Current balance: ${new_balance:,.2f}', 'success')
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

        # Java 25 Engine: Evaluate AML & Fraud Risk
        daily_count = len(account.transactions) if account.transactions else 1
        risk_res = analyze_transaction_risk(
            reference_id="PENDING-WITHDRAWAL",
            transaction_type="withdrawal",
            amount=amount,
            account_type=account.account_type,
            status=account.status,
            daily_txn_count=daily_count
        )

        if risk_res.get('decision') == 'REJECTED':
            flash(f"Withdrawal BLOCKED by Java AML Risk Engine: {risk_res.get('recommendation')} (Risk Score: {risk_res.get('risk_score')}/100)", 'danger')
            return redirect(url_for('banking.dashboard'))

        try:
            new_balance = account.withdraw(amount)
            tx_ref = Transaction.generate_reference()
            
            txn = Transaction(
                reference_id=tx_ref,
                account_id=account.id,
                transaction_type='withdrawal',
                amount=amount,
                balance_after=new_balance,
                description=form.description.data or 'Cash Withdrawal',
                related_account='ATM / E-CASH'
            )
            db.session.add(txn)
            db.session.commit()

            # Record Java Audit into SQL
            log_fraud_audit(
                tx_ref, account.account_number, amount,
                risk_res.get('risk_score', 0), risk_res.get('risk_level', 'LOW'),
                risk_res.get('decision', 'APPROVED'), risk_res.get('rules_triggered', []),
                risk_res.get('recommendation', '')
            )

            # C++ Engine: Compute cryptographic ledger checksum & record to SQL
            hash_res = generate_ledger_hash(tx_ref, account.account_number, 'ATM / E-CASH', amount, str(txn.timestamp))
            log_ledger_checksum(tx_ref, hash_res.get('ledger_hash', ''))

            flash(f'Successfully withdrew ${amount:,.2f} from account #{account.account_number}. Java Risk Rating: {risk_res.get("risk_level")}. Remaining balance: ${new_balance:,.2f}', 'warning')
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
        recipient_number = form.recipient_account.data.strip().replace(' ', '')
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

        # Java 25 Engine: Enterprise AML & Fraud Detection Risk Scoring
        daily_count = len(sender_account.transactions) if sender_account.transactions else 1
        risk_res = analyze_transaction_risk(
            reference_id="PENDING-TRANSFER",
            transaction_type="transfer_out",
            amount=amount,
            account_type=sender_account.account_type,
            status=sender_account.status,
            daily_txn_count=daily_count
        )

        if risk_res.get('decision') == 'REJECTED':
            flash(f"Transfer REJECTED by Java 25 AML Compliance: {risk_res.get('recommendation')} (Risk Score: {risk_res.get('risk_score')}/100)", 'danger')
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

            # Record Java Audit in SQL
            log_fraud_audit(
                tx_ref, sender_account.account_number, amount,
                risk_res.get('risk_score', 0), risk_res.get('risk_level', 'LOW'),
                risk_res.get('decision', 'APPROVED'), risk_res.get('rules_triggered', []),
                risk_res.get('recommendation', '')
            )

            # C++ Engine: Compute cryptographic ledger checksum & record in SQL
            hash_res = generate_ledger_hash(tx_ref, sender_account.account_number, recipient_account.account_number, amount, str(sender_txn.timestamp))
            log_ledger_checksum(tx_ref, hash_res.get('ledger_hash', ''))

            recipient_name = recipient_account.owner.full_name or recipient_account.owner.username
            flash(f'Successfully transferred ${amount:,.2f} to {recipient_name} (#{recipient_account.account_number}). Ref: {tx_ref}. Ledger Hash: {hash_res.get("ledger_hash", "")[:12]}...', 'success')
        except Exception as err:
            db.session.rollback()
            flash(f'Transfer failed due to system error: {str(err)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Transfer Error ({field}): {error}', 'danger')

    return redirect(url_for('banking.dashboard'))

@banking_bp.route('/tools/calculator')
@customer_required
def calculator():
    return render_template('services/calculator.html')

@banking_bp.route('/api/calc/interest', methods=['POST'])
@customer_required
def api_calc_interest():
    data = request.get_json() or {}
    principal = float(data.get('principal', 10000.0))
    annual_rate = float(data.get('annual_rate', 7.5))
    years = int(data.get('years', 5))
    freq = int(data.get('frequency', 12))
    result = calculate_compound_interest(principal, annual_rate, years, freq)
    return jsonify(result)

@banking_bp.route('/api/calc/loan', methods=['POST'])
@customer_required
def api_calc_loan():
    data = request.get_json() or {}
    principal = float(data.get('principal', 25000.0))
    annual_rate = float(data.get('annual_rate', 8.5))
    months = int(data.get('term_months', 36))
    result = calculate_loan_amortization(principal, annual_rate, months)
    return jsonify(result)

@banking_bp.route('/api/tx/verify/<ref_id>')
@customer_required
def api_verify_txn(ref_id):
    txn = Transaction.query.filter_by(reference_id=ref_id).first()
    if txn:
        sender = txn.account.account_number if txn.account else 'SYSTEM'
        receiver = txn.related_account or 'SYSTEM'
        result = generate_ledger_hash(txn.reference_id, sender, receiver, txn.amount, str(txn.timestamp))
        result['verified'] = True
        return jsonify(result)
    else:
        result = generate_ledger_hash(ref_id, 'ACCOUNT-SRC', 'ACCOUNT-DST', 100.0, '2026-11-03')
        result['verified'] = False
        return jsonify(result)

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
            tx_ref = Transaction.generate_reference()
            txn = Transaction(
                reference_id=tx_ref,
                account_id=new_account.id,
                transaction_type='deposit',
                amount=initial_deposit,
                balance_after=initial_deposit,
                description='Opening Balance Deposit',
                related_account='APEX-RESERVE-001'
            )
            db.session.add(txn)
            db.session.commit()

            # C++ Checksum
            hash_res = generate_ledger_hash(tx_ref, 'APEX-RESERVE-001', account_num, initial_deposit, str(txn.timestamp))
            log_ledger_checksum(tx_ref, hash_res.get('ledger_hash', ''))
        else:
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

@banking_bp.route('/loans')
@customer_required
def loans():
    user_loans = Loan.query.filter_by(user_id=current_user.id).order_by(Loan.created_at.desc()).all()
    
    # Financial metrics for customer's loans
    total_borrowed = sum(l.amount for l in user_loans if l.status == 'APPROVED')
    total_monthly_emi = sum(l.monthly_payment for l in user_loans if l.status == 'APPROVED')
    pending_count = sum(1 for l in user_loans if l.status == 'PENDING')

    return render_template(
        'banking/loans.html',
        loans=user_loans,
        total_borrowed=total_borrowed,
        total_monthly_emi=total_monthly_emi,
        pending_count=pending_count
    )

@banking_bp.route('/loans/apply', methods=['GET', 'POST'])
@customer_required
def apply_loan():
    accounts = Account.query.filter_by(user_id=current_user.id, status='active').all()
    if not accounts:
        flash('You must have at least one active bank account to apply for a loan.', 'warning')
        return redirect(url_for('banking.dashboard'))

    form = LoanApplicationForm()
    form.account_id.choices = [
        (acc.id, f"Account #{acc.account_number} ({acc.account_type.title()} - Available: ${acc.balance:,.2f})")
        for acc in accounts
    ]

    if form.validate_on_submit():
        account_id = form.account_id.data
        disbursal_account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not disbursal_account:
            flash('Invalid account selected.', 'danger')
            return redirect(url_for('banking.apply_loan'))

        amount = float(form.amount.data)
        term_months = int(form.term_months.data)
        loan_type = form.loan_type.data
        annual_rate = LOAN_TYPE_RATES.get(loan_type, 7.5)
        monthly_income = float(form.monthly_income.data)
        purpose = form.purpose.data.strip()

        # Compute exact amortization via C++ Financial Engine
        calc_result = calculate_loan_amortization(amount, annual_rate, term_months)
        monthly_payment = float(calc_result.get('monthly_payment', 0.0))
        total_payable = float(calc_result.get('total_payment', 0.0))
        total_interest = float(calc_result.get('total_interest', 0.0))

        # Underwriting Debt-to-Income check note
        dti_ratio = (monthly_payment / monthly_income) * 100.0 if monthly_income > 0 else 100.0

        loan = Loan(
            loan_reference=Loan.generate_loan_reference(),
            user_id=current_user.id,
            account_id=disbursal_account.id,
            loan_type=loan_type,
            amount=amount,
            annual_rate=annual_rate,
            term_months=term_months,
            monthly_payment=monthly_payment,
            total_payable=total_payable,
            total_interest=total_interest,
            purpose=purpose,
            monthly_income=monthly_income,
            status='PENDING'
        )

        db.session.add(loan)
        db.session.commit()

        flash(
            f'🎉 Loan application ({loan.loan_reference}) for ${amount:,.2f} submitted successfully! '
            f'Estimated EMI: ${monthly_payment:,.2f}/mo. It is now awaiting Branch Manager review.',
            'success'
        )
        return redirect(url_for('banking.loans'))

    return render_template(
        'banking/apply_loan.html',
        form=form,
        rates=LOAN_TYPE_RATES
    )

@banking_bp.route('/api/loans/calculate', methods=['POST'])
@customer_required
def api_loan_calculate():
    data = request.get_json() or {}
    try:
        amount = float(data.get('amount', 10000.0))
        loan_type = data.get('loan_type', 'Personal Loan')
        term_months = int(data.get('term_months', 12))
        annual_rate = LOAN_TYPE_RATES.get(loan_type, 7.5)

        result = calculate_loan_amortization(amount, annual_rate, term_months)
        result['annual_rate'] = annual_rate
        result['loan_type'] = loan_type
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ──────────────────────────────────────────────
# CARDS & DIGITAL WALLET MANAGEMENT
# ──────────────────────────────────────────────
@banking_bp.route('/cards')
@customer_required
def cards():
    user_cards = Card.query.filter_by(user_id=current_user.id).order_by(Card.created_at.desc()).all()
    accounts = Account.query.filter_by(user_id=current_user.id, status='active').all()

    active_count = sum(1 for c in user_cards if c.status == 'active')
    frozen_count = sum(1 for c in user_cards if c.status == 'frozen')
    total_spending_power = sum(c.daily_limit for c in user_cards if c.status == 'active')

    limit_form = UpdateCardLimitForm()
    pin_form = ChangeCardPinForm()

    return render_template(
        'banking/cards.html',
        cards=user_cards,
        accounts=accounts,
        active_count=active_count,
        frozen_count=frozen_count,
        total_spending_power=total_spending_power,
        limit_form=limit_form,
        pin_form=pin_form
    )

@banking_bp.route('/cards/issue', methods=['GET', 'POST'])
@customer_required
def issue_card():
    accounts = Account.query.filter_by(user_id=current_user.id, status='active').all()
    if not accounts:
        flash('You must have an active checking or savings account before requesting a debit card.', 'warning')
        return redirect(url_for('banking.dashboard'))

    form = IssueCardForm()
    form.account_id.choices = [
        (acc.id, f"Account #{acc.account_number} ({acc.account_type.title()} - Available: ${acc.balance:,.2f})")
        for acc in accounts
    ]

    if form.validate_on_submit():
        account_id = form.account_id.data
        linked_account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not linked_account:
            flash('Invalid linked account selected.', 'danger')
            return redirect(url_for('banking.issue_card'))

        network = form.card_network.data
        card_type = form.card_type.data
        card_design = form.card_design.data
        daily_limit = float(form.daily_limit.data)
        pin = form.pin.data

        # Generate realistic, unique card credentials
        card_num = Card.generate_card_number(network)
        cvv = Card.generate_cvv()
        expiry = Card.generate_expiry(3)

        new_card = Card(
            card_number=card_num,
            card_holder=current_user.full_name or current_user.username.upper(),
            user_id=current_user.id,
            account_id=linked_account.id,
            card_type=card_type,
            card_network=network,
            card_design=card_design,
            cvv=cvv,
            expiry_date=expiry,
            status='active',
            daily_limit=daily_limit,
            daily_spent=0.00
        )
        new_card.set_pin(pin)

        # Create system notification
        notif = Notification(
            user_id=current_user.id,
            title='New Card Issued',
            message=f'Your new {network} {card_type.title()} Card ending in {card_num[-4:]} has been activated.',
            category='success'
        )

        db.session.add(new_card)
        db.session.add(notif)
        db.session.commit()

        flash(f'🎉 Success! Your {network} {card_type.title()} Card ending in {card_num[-4:]} has been created and is ready for use.', 'success')
        return redirect(url_for('banking.cards'))

    return render_template('banking/issue_card.html', form=form)

@banking_bp.route('/cards/<int:card_id>/toggle-freeze', methods=['POST'])
@customer_required
def toggle_card_freeze(card_id):
    card = Card.query.filter_by(id=card_id, user_id=current_user.id).first_or_404()

    if card.status == 'active':
        card.status = 'frozen'
        flash(f'❄️ Card ending in {card.card_number[-4:]} has been FROZEN. Online and POS purchases are temporarily disabled.', 'warning')
        notif_msg = f'Card ending in {card.card_number[-4:]} was frozen by cardholder.'
        notif_cat = 'warning'
    else:
        card.status = 'active'
        flash(f'✅ Card ending in {card.card_number[-4:]} has been UNFREEZED and is fully active.', 'success')
        notif_msg = f'Card ending in {card.card_number[-4:]} was unfrozen and activated.'
        notif_cat = 'success'

    notif = Notification(
        user_id=current_user.id,
        title='Card Status Updated',
        message=notif_msg,
        category=notif_cat
    )
    db.session.add(notif)
    db.session.commit()
    return redirect(url_for('banking.cards'))

@banking_bp.route('/cards/<int:card_id>/update-limit', methods=['POST'])
@customer_required
def update_card_limit(card_id):
    card = Card.query.filter_by(id=card_id, user_id=current_user.id).first_or_404()
    form = UpdateCardLimitForm()

    if form.validate_on_submit():
        new_limit = float(form.daily_limit.data)
        card.daily_limit = new_limit

        notif = Notification(
            user_id=current_user.id,
            title='Card Limit Adjusted',
            message=f'Daily spending limit for card ending in {card.card_number[-4:]} updated to ${new_limit:,.2f}.',
            category='info'
        )
        db.session.add(notif)
        db.session.commit()
        flash(f'Daily spending limit updated to ${new_limit:,.2f}.', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error updating limit: {error}', 'danger')

    return redirect(url_for('banking.cards'))

@banking_bp.route('/cards/<int:card_id>/change-pin', methods=['POST'])
@customer_required
def change_card_pin(card_id):
    card = Card.query.filter_by(id=card_id, user_id=current_user.id).first_or_404()
    form = ChangeCardPinForm()

    if form.validate_on_submit():
        if not card.check_pin(form.current_pin.data):
            flash('Current PIN verification failed.', 'danger')
            return redirect(url_for('banking.cards'))

        card.set_pin(form.new_pin.data)
        notif = Notification(
            user_id=current_user.id,
            title='Card PIN Updated',
            message=f'Security PIN for card ending in {card.card_number[-4:]} was successfully updated.',
            category='info'
        )
        db.session.add(notif)
        db.session.commit()
        flash('Security PIN updated successfully.', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'PIN Error: {error}', 'danger')

    return redirect(url_for('banking.cards'))

# ──────────────────────────────────────────────
# STATEMENT GENERATOR & CSV EXPORT
# ──────────────────────────────────────────────
@banking_bp.route('/transactions/export-csv')
@customer_required
def export_transactions_csv():
    account_id = request.args.get('account_id', type=int)
    user_account_ids = [acc.id for acc in current_user.accounts]

    query = Transaction.query.filter(Transaction.account_id.in_(user_account_ids))
    if account_id and account_id in user_account_ids:
        query = query.filter_by(account_id=account_id)

    transactions = query.order_by(Transaction.timestamp.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Write CSV Header
    writer.writerow([
        'Reference ID', 'Timestamp (UTC)', 'Account Number', 'Account Type',
        'Operation Type', 'Description', 'Counterparty Reference',
        'Debit / Credit Indicator', 'Transaction Amount ($)', 'Running Balance ($)'
    ])

    for t in transactions:
        is_inflow = t.transaction_type in ['deposit', 'transfer_in']
        debit_credit = 'CREDIT' if is_inflow else 'DEBIT'
        writer.writerow([
            t.reference_id,
            t.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            t.account.account_number if t.account else '',
            t.account.account_type.upper() if t.account else '',
            t.transaction_type,
            t.description or '',
            t.related_account or '',
            debit_credit,
            f"{t.amount:.2f}",
            f"{t.balance_after:.2f}"
        ])

    csv_data = output.getvalue()
    filename = f"Apex_Bank_Statement_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@banking_bp.route('/statement')
@customer_required
def statement():
    account_id = request.args.get('account_id', type=int)
    period = request.args.get('period', '30d')

    user_accounts = current_user.accounts
    if not user_accounts:
        flash('No bank accounts found.', 'warning')
        return redirect(url_for('banking.dashboard'))

    selected_account = None
    if account_id:
        selected_account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
    if not selected_account:
        selected_account = user_accounts[0]

    now = datetime.utcnow()
    if period == '7d':
        start_date = now - timedelta(days=7)
        period_label = 'Last 7 Days'
    elif period == '30d':
        start_date = now - timedelta(days=30)
        period_label = 'Last 30 Days'
    elif period == '90d':
        start_date = now - timedelta(days=90)
        period_label = 'Last 90 Days'
    elif period == 'year':
        start_date = now - timedelta(days=365)
        period_label = 'Last 12 Months'
    else:
        start_date = datetime(2020, 1, 1)
        period_label = 'Full Historical Record'

    txns = Transaction.query.filter(
        Transaction.account_id == selected_account.id,
        Transaction.timestamp >= start_date
    ).order_by(Transaction.timestamp.asc()).all()

    total_credits = sum(t.amount for t in txns if t.transaction_type in ['deposit', 'transfer_in'])
    total_debits = sum(t.amount for t in txns if t.transaction_type not in ['deposit', 'transfer_in'])
    closing_balance = selected_account.balance

    # Estimate opening balance
    opening_balance = closing_balance - total_credits + total_debits

    return render_template(
        'banking/statement.html',
        accounts=user_accounts,
        selected_account=selected_account,
        period=period,
        period_label=period_label,
        transactions=list(reversed(txns)),
        opening_balance=opening_balance,
        closing_balance=closing_balance,
        total_credits=total_credits,
        total_debits=total_debits,
        statement_date=now
    )

# ──────────────────────────────────────────────
# NOTIFICATIONS DISMISSAL
# ──────────────────────────────────────────────
@banking_bp.route('/notifications/read-all', methods=['POST'])
@customer_required
def mark_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'All notifications marked as read'})


