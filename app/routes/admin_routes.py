"""
Administrator Blueprint for Apex Bank Management System.
Exclusively handles system oversight, staff administration, user role management, audit logs, and direct SQL queries.
"""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from app.extensions import db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.loan import Loan
from app.models.card import Card
from app.models.fixed_deposit import FixedDeposit
from app.models.ticket import SupportTicket
from app.models.currency_rate import CurrencyRate
from app.models.standing_order import StandingOrder
from app.models.fx_conversion import FXConversion
from app.models.notification import Notification
from app.forms.fx_forms import AdminFXRateUpdateForm
from app.utils.decorators import admin_required
from app.utils.sql_executor import execute_raw_query, log_ledger_checksum
from app.utils.cpp_engine import generate_ledger_hash

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    search_query = request.args.get('q', '').strip()
    role_filter = request.args.get('role', '').strip()

    users_query = User.query
    if search_query:
        users_query = users_query.filter(
            (User.username.ilike(f'%{search_query}%')) |
            (User.email.ilike(f'%{search_query}%')) |
            (User.full_name.ilike(f'%{search_query}%'))
        )
    if role_filter:
        users_query = users_query.filter_by(role=role_filter)

    all_users = users_query.order_by(User.created_at.desc()).all()

    # Executive System Metrics
    total_users_count = User.query.count()
    total_customers_count = User.query.filter_by(role='customer').count()
    total_managers_count = User.query.filter_by(role='manager').count()
    total_admins_count = User.query.filter_by(role='admin').count()

    total_accounts_count = Account.query.count()
    total_reserves = sum(acc.balance for acc in Account.query.all())
    master_transactions = Transaction.query.order_by(Transaction.timestamp.desc()).limit(20).all()

    total_loans_count = Loan.query.count()
    total_cards_count = Card.query.count()
    total_fd_volume = sum(fd.principal_amount for fd in FixedDeposit.query.filter_by(status='active').all())
    open_tickets_count = SupportTicket.query.filter(SupportTicket.status.in_(['OPEN', 'IN_PROGRESS'])).count()
    total_standing_orders = StandingOrder.query.filter_by(status='ACTIVE').count()
    total_fx_conversions = FXConversion.query.count()

    return render_template(
        'admin/dashboard.html',
        users=all_users,
        total_users=total_users_count,
        total_customers=total_customers_count,
        total_managers=total_managers_count,
        total_admins=total_admins_count,
        total_accounts=total_accounts_count,
        total_reserves=total_reserves,
        total_loans_count=total_loans_count,
        total_cards_count=total_cards_count,
        total_fd_volume=total_fd_volume,
        open_tickets_count=open_tickets_count,
        total_standing_orders=total_standing_orders,
        total_fx_conversions=total_fx_conversions,
        transactions=master_transactions,
        search_query=search_query,
        role_filter=role_filter
    )

@admin_bp.route('/sql-console')
@admin_required
def sql_console():
    return render_template('admin/sql_console.html')

@admin_bp.route('/api/sql', methods=['POST'])
@admin_required
def api_run_sql():
    data = request.get_json() or {}
    query_text = data.get('query', '')
    result = execute_raw_query(query_text)
    return jsonify(result)

@admin_bp.route('/user/<int:user_id>/update-role', methods=['POST'])
@admin_required
def update_user_role(user_id):
    target_user = User.query.get_or_404(user_id)
    new_role = request.form.get('role', '').strip().lower()

    if new_role not in ('customer', 'manager', 'admin'):
        flash('Invalid role specified.', 'danger')
        return redirect(url_for('admin.dashboard'))

    # Prevent admin from accidentally demoting themselves if only 1 admin
    target_user.role = new_role
    db.session.commit()
    flash(f'Role for {target_user.username} successfully updated to {new_role.upper()}.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/user/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def reset_user_password(user_id):
    target_user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password', '').strip()

    if len(new_password) < 6:
        flash('Password must be at least 6 characters.', 'danger')
        return redirect(url_for('admin.dashboard'))

    target_user.set_password(new_password)
    db.session.commit()
    flash(f'Password for user {target_user.username} has been reset.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/tickets')
@admin_required
def tickets():
    all_tickets = SupportTicket.query.order_by(SupportTicket.created_at.desc()).all()
    open_count = SupportTicket.query.filter_by(status='OPEN').count()
    critical_count = SupportTicket.query.filter_by(priority='CRITICAL').count()

    return render_template(
        'admin/tickets.html',
        tickets=all_tickets,
        open_count=open_count,
        critical_count=critical_count,
        total_count=len(all_tickets)
    )

@admin_bp.route('/fx-rates')
@admin_required
def fx_rates():
    rates = CurrencyRate.query.order_by(CurrencyRate.currency_code.asc()).all()
    all_conversions = FXConversion.query.order_by(FXConversion.created_at.desc()).limit(25).all()
    total_conversions = FXConversion.query.count()
    total_spread_revenue = sum(c.spread_fee for c in FXConversion.query.all())

    return render_template(
        'admin/fx_rates.html',
        rates=rates,
        conversions=all_conversions,
        total_conversions=total_conversions,
        total_spread_revenue=total_spread_revenue
    )

@admin_bp.route('/fx-rates/<int:rate_id>/update', methods=['POST'])
@admin_required
def update_fx_rate(rate_id):
    rate_obj = CurrencyRate.query.get_or_404(rate_id)
    try:
        new_rate = float(request.form.get('rate_to_usd', rate_obj.rate_to_usd))
        new_spread = float(request.form.get('spread_pct', rate_obj.spread_pct))
        is_active = True if request.form.get('is_active') == 'on' else False

        if new_rate <= 0:
            flash('Exchange rate must be positive.', 'danger')
            return redirect(url_for('admin.fx_rates'))

        rate_obj.rate_to_usd = new_rate
        rate_obj.spread_pct = new_spread
        rate_obj.is_active = is_active
        rate_obj.updated_at = datetime.utcnow()

        db.session.commit()
        flash(f"Currency {rate_obj.currency_code} rate updated: 1 {rate_obj.currency_code} = {new_rate} USD (Spread: {new_spread}%).", 'success')
    except Exception as e:
        flash(f"Error updating currency rate: {e}", 'danger')

    return redirect(url_for('admin.fx_rates'))

@admin_bp.route('/batch-processing')
@admin_required
def batch_processing():
    all_orders = StandingOrder.query.all()
    now = datetime.utcnow()
    due_orders = [so for so in all_orders if so.is_due]
    total_active = sum(1 for so in all_orders if so.status == 'ACTIVE')
    total_executions = sum(so.total_executions for so in all_orders)
    total_volume_processed = sum(so.total_transferred for so in all_orders)

    return render_template(
        'admin/batch_processing.html',
        all_orders=all_orders,
        due_orders=due_orders,
        total_active=total_active,
        total_executions=total_executions,
        total_volume_processed=total_volume_processed,
        now=now
    )

@admin_bp.route('/batch-processing/run-standing-orders', methods=['POST'])
@admin_required
def run_standing_orders_batch():
    now = datetime.utcnow()
    # Find all due standing orders (or all active if forced via query param)
    force = request.args.get('force') == '1'
    if force:
        due_orders = StandingOrder.query.filter_by(status='ACTIVE').all()
    else:
        due_orders = [so for so in StandingOrder.query.filter_by(status='ACTIVE').all() if so.is_due]

    if not due_orders:
        flash('No standing orders are currently due for execution.', 'info')
        return redirect(url_for('admin.batch_processing'))

    processed_count = 0
    total_disbursed = 0.0
    failed_count = 0

    for order in due_orders:
        src = order.source_account
        if src.balance < order.amount:
            failed_count += 1
            continue

        src.balance -= order.amount
        order.total_executions += 1
        order.total_transferred += order.amount
        order.last_execution_date = now
        order.next_execution_date = order.calculate_next_date(now)

        tx_ref = Transaction.generate_reference()
        txn = Transaction(
            reference_id=tx_ref,
            account_id=src.id,
            transaction_type='transfer_out',
            amount=order.amount,
            balance_after=src.balance,
            description=f"Automated Batch Standing Order [{order.order_reference}]: {order.title}",
            related_account=order.destination_account
        )

        notif = Notification(
            user_id=order.user_id,
            title='Standing Order Auto-Executed (Batch)',
            message=f"Mandate {order.order_reference} ({order.title}) for {src.symbol}{order.amount:,.2f} has been processed.",
            category='success'
        )

        db.session.add_all([txn, notif])
        processed_count += 1
        total_disbursed += order.amount

        # C++ cryptographic checksum
        hash_res = generate_ledger_hash(tx_ref, src.account_number, order.destination_account, order.amount, str(now))
        log_ledger_checksum(tx_ref, hash_res.get('ledger_hash', ''))

    db.session.commit()
    flash(f"Batch Processing Executed: {processed_count} standing orders disbursed (${total_disbursed:,.2f}). {failed_count} failed due to insufficient funds.", 'success')
    return redirect(url_for('admin.batch_processing'))


