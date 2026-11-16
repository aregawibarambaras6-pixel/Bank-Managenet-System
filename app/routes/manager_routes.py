from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from app.extensions import db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.loan import Loan
from app.models.card import Card
from app.models.fixed_deposit import FixedDeposit
from app.models.ticket import SupportTicket
from app.models.notification import Notification
from app.models.currency_rate import CurrencyRate
from app.models.standing_order import StandingOrder
from app.models.fx_conversion import FXConversion
from app.forms.support_forms import ManagerTicketReplyForm
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
    open_tickets_count = SupportTicket.query.filter(SupportTicket.status.in_(['OPEN', 'IN_PROGRESS'])).count()
    total_fd_volume = sum(fd.principal_amount for fd in FixedDeposit.query.filter_by(status='active').all())
    total_standing_orders = StandingOrder.query.filter_by(status='ACTIVE').count()
    total_fx_count = FXConversion.query.count()

    return render_template(
        'manager/dashboard.html',
        accounts=accounts,
        total_customers=total_customers,
        total_accounts=total_accounts,
        total_bank_reserves=total_bank_reserves,
        recent_transactions=recent_transactions,
        pending_loans_count=pending_loans_count,
        total_cards=total_cards,
        open_tickets_count=open_tickets_count,
        total_fd_volume=total_fd_volume,
        total_standing_orders=total_standing_orders,
        total_fx_count=total_fx_count,
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

# ──────────────────────────────────────────────
# FIXED DEPOSIT PORTFOLIO OVERSIGHT
# ──────────────────────────────────────────────
@manager_bp.route('/deposits')
@manager_required
def deposits():
    all_deposits = FixedDeposit.query.order_by(FixedDeposit.start_date.desc()).all()
    active_deposits = [d for d in all_deposits if d.status == 'active']
    total_locked_capital = sum(d.principal_amount for d in active_deposits)
    total_projected_liability = sum(d.maturity_amount for d in active_deposits)
    matured_count = sum(1 for d in active_deposits if d.is_matured)

    return render_template(
        'manager/deposits.html',
        deposits=all_deposits,
        total_locked_capital=total_locked_capital,
        total_projected_liability=total_projected_liability,
        active_count=len(active_deposits),
        matured_count=matured_count
    )

# ──────────────────────────────────────────────
# SUPPORT TICKETS & DISPUTE RESOLUTION
# ──────────────────────────────────────────────
@manager_bp.route('/tickets')
@manager_required
def tickets():
    status_filter = request.args.get('status', '').upper()
    priority_filter = request.args.get('priority', '').upper()

    query = SupportTicket.query
    if status_filter in ['OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED']:
        query = query.filter_by(status=status_filter)
    if priority_filter in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
        query = query.filter_by(priority=priority_filter)

    all_tickets = query.order_by(SupportTicket.created_at.desc()).all()

    open_count = SupportTicket.query.filter_by(status='OPEN').count()
    in_progress_count = SupportTicket.query.filter_by(status='IN_PROGRESS').count()
    resolved_count = SupportTicket.query.filter_by(status='RESOLVED').count()
    critical_count = SupportTicket.query.filter(SupportTicket.priority == 'CRITICAL', SupportTicket.status.in_(['OPEN', 'IN_PROGRESS'])).count()

    reply_form = ManagerTicketReplyForm()

    return render_template(
        'manager/tickets.html',
        tickets=all_tickets,
        open_count=open_count,
        in_progress_count=in_progress_count,
        resolved_count=resolved_count,
        critical_count=critical_count,
        status_filter=status_filter,
        priority_filter=priority_filter,
        reply_form=reply_form
    )

@manager_bp.route('/tickets/<int:ticket_id>/reply', methods=['POST'])
@manager_required
def reply_ticket(ticket_id):
    ticket = SupportTicket.query.get_or_404(ticket_id)
    form = ManagerTicketReplyForm()

    if form.validate_on_submit():
        ticket.manager_reply = form.reply.data.strip()
        ticket.status = form.status.data
        ticket.assigned_manager_id = current_user.id
        ticket.updated_at = datetime.utcnow()

        notif = Notification(
            user_id=ticket.user_id,
            title=f'Support Ticket Update ({ticket.ticket_number})',
            message=f'Branch Management replied to your inquiry: Status is now {ticket.status.replace("_", " ")}.',
            category='info'
        )

        db.session.add(notif)
        db.session.commit()

        flash(f'Response sent for Ticket #{ticket.ticket_number}. Status updated to {ticket.status}.', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Reply Error: {error}', 'danger')

    return redirect(url_for('manager.tickets'))


@manager_bp.route('/fx-treasury')
@manager_required
def fx_treasury():
    rates = CurrencyRate.query.filter_by(is_active=True).all()
    rate_dict = {r.currency_code: r for r in rates}

    all_accounts = Account.query.all()
    currency_holdings = {}
    for acc in all_accounts:
        c = acc.currency.upper()
        if c not in currency_holdings:
            r_obj = rate_dict.get(c)
            currency_holdings[c] = {
                'currency': c,
                'symbol': acc.symbol,
                'total_balance': 0.0,
                'account_count': 0,
                'rate_to_usd': r_obj.rate_to_usd if r_obj else 1.0,
                'spread_pct': r_obj.spread_pct if r_obj else 0.8
            }
        currency_holdings[c]['total_balance'] += acc.balance
        currency_holdings[c]['account_count'] += 1

    total_fx_reserve_usd = 0.0
    for c, data in currency_holdings.items():
        usd_equiv = data['total_balance'] * data['rate_to_usd']
        data['usd_equivalent'] = usd_equiv
        total_fx_reserve_usd += usd_equiv

    for c, data in currency_holdings.items():
        data['portfolio_weight'] = (data['usd_equivalent'] / total_fx_reserve_usd * 100.0) if total_fx_reserve_usd > 0 else 0.0

    recent_conversions = FXConversion.query.order_by(FXConversion.created_at.desc()).limit(30).all()
    total_conversions_volume_usd = sum(
        fx.from_amount * (rate_dict[fx.from_currency].rate_to_usd if fx.from_currency in rate_dict and rate_dict[fx.from_currency] else 1.0)
        for fx in FXConversion.query.all()
    )

    return render_template(
        'manager/fx_treasury.html',
        holdings=currency_holdings,
        total_fx_reserve_usd=total_fx_reserve_usd,
        total_conversions_volume_usd=total_conversions_volume_usd,
        conversions=recent_conversions,
        rates=rates
    )


@manager_bp.route('/standing-orders')
@manager_required
def standing_orders():
    status_filter = request.args.get('status', '').upper()
    query = StandingOrder.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    all_orders = query.order_by(StandingOrder.created_at.desc()).all()

    active_count = StandingOrder.query.filter_by(status='ACTIVE').count()
    paused_count = StandingOrder.query.filter_by(status='PAUSED').count()
    cancelled_count = StandingOrder.query.filter_by(status='CANCELLED').count()
    total_active_volume = sum(so.amount for so in StandingOrder.query.filter_by(status='ACTIVE').all())

    return render_template(
        'manager/standing_orders.html',
        orders=all_orders,
        active_count=active_count,
        paused_count=paused_count,
        cancelled_count=cancelled_count,
        total_active_volume=total_active_volume,
        status_filter=status_filter
    )




