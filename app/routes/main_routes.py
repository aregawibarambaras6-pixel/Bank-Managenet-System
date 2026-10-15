from flask import Blueprint, render_template, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Render the Bank Management System home page."""
    return render_template('index.html')

# Direct convenience redirects for common URLs
@main_bp.route('/login')
def login_redirect():
    return redirect(url_for('auth.login'))

@main_bp.route('/register')
@main_bp.route('/signup')
def register_redirect():
    return redirect(url_for('auth.register'))

@main_bp.route('/logout')
@main_bp.route('/signout')
def logout_redirect():
    return redirect(url_for('auth.logout'))

@main_bp.route('/manager')
def manager_redirect():
    return redirect(url_for('manager.dashboard'))

@main_bp.route('/admin')
def admin_redirect():
    return redirect(url_for('admin.dashboard'))

@main_bp.route('/account')
@main_bp.route('/accounts')
def account_redirect():
    return redirect(url_for('banking.dashboard'))

@main_bp.route('/history')
@main_bp.route('/ledger')
def history_redirect():
    return redirect(url_for('banking.transactions'))
