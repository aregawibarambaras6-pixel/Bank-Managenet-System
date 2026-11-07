from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.extensions import db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.loan import Loan
from app.models.card import Card
from app.utils.decorators import manager_required
from app.utils.cpp_engine import generate_ledger_hash
from app.utils.sql_executor import log_ledger_checksum

manager_bp = Blueprint('manager', __name__, url_prefix='/manager')

@manager_bp.route('/dashboard')
@manager_required
def dashboard():
    search_query = request.args.get('q', '').strip()
    
    # Query accounts
    accounts_query = Account.query.join(User)
    if search_query:
        accounts_query = accounts_query.filter(
            (Account.account_number.contains(search_query)) |
            (User.username.contains(search_query)) |
            (User.email.contains(search_query)) |
            (User.full_name.contains(search_query))
        )
    accounts = accounts_query.order_by(Account.created_at.desc()).all()

    # System Statistics for Manager
    total_customers = User.query.filter_by(role='customer').count()
    total_accounts = Account.query.count()
    total_bank_reserves = sum(acc.balance for acc in Account.query.all())
    recent_transactions = Transaction.query.order_by(Transaction.timestamp.desc()).limit(15).all()
    pending_loans_count = Loan.query.filter_by(status='PENDING').count()
    total_cards = Card.query.count()

    return render_template(
        'manager/dashboard.html',
        accounts=accounts,
        total_customers=total_customers,
        total_accounts=total_accounts,
        total_bank_reserves=total_bank_reserves,
        recent_transactions=recent_transactions,
        pending_loans_count=pending_loans_count,
        total_cards=total_cards,
        search_query=search_query
    )

@manager_bp.route('/account/<int:account_id>/toggle-status', methods=['POST'])
@manager_required
def toggle_status(account_id):
    account = Account.query.get_or_404(account_id)

    if account.status == 'active':
        account.status = 'frozen'
        flash(f'Account #{account.account_number} has been FROZEN.', 'warning')
    else:
        account.status = 'active'
        flash(f'Account #{account.account_number} has been ACTIVATED.', 'success')

    db.session.commit()
    return redirect(url_for('manager.dashboard'))

@manager_bp.route('/loans')
@manager_required
def loans():
    status_filter = request.args.get('status', '').upper()
    query = Loan.query

    if status_filter in ['PENDING', 'APPROVED', 'REJECTED']:
        query = query.filter_by(status=status_filter)

    all_loans = query.order_by(Loan.created_at.desc()).all()

    pending_count = Loan.query.filter_by(status='PENDING').count()
    approved_count = Loan.query.filter_by(status='APPROVED').count()
    rejected_count = Loan.query.filter_by(status='REJECTED').count()
    total_disbursed = sum(l.amount for l in Loan.query.filter_by(status='APPROVED').all())
    pending_requested = sum(l.amount for l in Loan.query.filter_by(status='PENDING').all())

    return render_template(
        'manager/loans.html',
        loans=all_loans,
        status_filter=status_filter,
        pending_count=pending_count,
        approved_count=approved_count,
        rejected_count=rejected_count,
        total_disbursed=total_disbursed,
        pending_requested=pending_requested
    )

@manager_bp.route('/loans/<int:loan_id>/review', methods=['POST'])
@manager_required
def review_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    if loan.status != 'PENDING':
        flash(f'Loan #{loan.loan_reference} has already been reviewed ({loan.status}).', 'warning')
        return redirect(url_for('manager.loans'))

    decision = request.form.get('decision')
    notes = request.form.get('manager_notes', '').strip()

    if decision == 'APPROVE':
        loan.status = 'APPROVED'
        loan.reviewed_at = datetime.utcnow()
        loan.manager_notes = notes or 'Credit facility approved and disbursed by Branch Underwriter.'

        # Disburse credit funds into customer's selected account
        target_account = loan.account
        target_account.balance += loan.amount

        # Record ledger transaction
        ref_id = Transaction.generate_reference()
        txn = Transaction(
            reference_id=ref_id,
            account_id=target_account.id,
            transaction_type='deposit',
            amount=loan.amount,
            balance_after=target_account.balance,
            description=f"Loan Disbursal: {loan.loan_type} ({loan.loan_reference})",
            related_account='APEX-CREDIT-FACILITY'
        )
        db.session.add(txn)
        db.session.commit()

        # Compute cryptographic hash for ledger audit
        try:
            hash_res = generate_ledger_hash(
                ref_id, 'APEX-CREDIT-FACILITY', target_account.account_number, loan.amount, str(txn.timestamp)
            )
            log_ledger_checksum(ref_id, hash_res.get('ledger_hash', ''))
        except Exception:
            pass

        flash(f'✅ Loan #{loan.loan_reference} APPROVED! ${loan.amount:,.2f} disbursed to Account #{target_account.account_number}.', 'success')

    elif decision == 'REJECT':
        loan.status = 'REJECTED'
        loan.reviewed_at = datetime.utcnow()
        loan.manager_notes = notes or 'Declined by Branch Underwriting based on credit/income parameters.'
        db.session.commit()
        flash(f'❌ Loan application #{loan.loan_reference} for ${loan.amount:,.2f} has been REJECTED.', 'danger')

    else:
        flash('Invalid review decision.', 'danger')

    return redirect(url_for('manager.loans'))

@manager_bp.route('/cards')
@manager_required
def cards():
    search_query = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').lower()

    query = Card.query.join(User)
    if search_query:
        query = query.filter(
            (Card.card_number.contains(search_query)) |
            (Card.card_holder.contains(search_query)) |
            (User.username.contains(search_query)) |
            (User.email.contains(search_query))
        )
    if status_filter in ['active', 'frozen', 'blocked']:
        query = query.filter(Card.status == status_filter)

    all_cards = query.order_by(Card.created_at.desc()).all()
    active_cards = Card.query.filter_by(status='active').count()
    frozen_cards = Card.query.filter_by(status='frozen').count()
    total_cards = Card.query.count()

    return render_template(
        'manager/cards.html',
        cards=all_cards,
        search_query=search_query,
        status_filter=status_filter,
        active_cards=active_cards,
        frozen_cards=frozen_cards,
        total_cards=total_cards
    )

@manager_bp.route('/cards/<int:card_id>/toggle-freeze', methods=['POST'])
@manager_required
def toggle_card_freeze(card_id):
    card = Card.query.get_or_404(card_id)
    if card.status == 'active':
        card.status = 'frozen'
        flash(f'Card #{card.masked_number} belonging to {card.card_holder} has been FROZEN by Management.', 'warning')
    else:
        card.status = 'active'
        flash(f'Card #{card.masked_number} belonging to {card.card_holder} has been ACTIVATED by Management.', 'success')
    db.session.commit()
    return redirect(url_for('manager.cards'))


