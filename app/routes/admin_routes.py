"""
Administrator Blueprint for Apex Bank Management System.
Exclusively handles system oversight, staff administration, user role management, and audit logs.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from app.extensions import db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.utils.decorators import admin_required

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

    return render_template(
        'admin/dashboard.html',
        users=all_users,
        total_users=total_users_count,
        total_customers=total_customers_count,
        total_managers=total_managers_count,
        total_admins=total_admins_count,
        total_accounts=total_accounts_count,
        total_reserves=total_reserves,
        transactions=master_transactions,
        search_query=search_query,
        role_filter=role_filter
    )

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
