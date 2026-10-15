from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.extensions import db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.utils.decorators import manager_required

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

    return render_template(
        'manager/dashboard.html',
        accounts=accounts,
        total_customers=total_customers,
        total_accounts=total_accounts,
        total_bank_reserves=total_bank_reserves,
        recent_transactions=recent_transactions,
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
