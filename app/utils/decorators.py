"""
Role-based access control (RBAC) decorators for Apex Bank Management System.
Enforces strict segregation of duties across Customer, Manager, and Admin roles.
"""
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role != 'customer':
            flash(f'Access restricted: Customer services are for retail accounts only. Redirected to your {current_user.role.title()} portal.', 'warning')
            if current_user.role == 'manager':
                return redirect(url_for('manager.dashboard'))
            elif current_user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role != 'manager':
            flash(f'Access denied: The Manager Portal is restricted exclusively to Branch Managers.', 'danger')
            if current_user.role == 'customer':
                return redirect(url_for('banking.dashboard'))
            elif current_user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role != 'admin':
            flash(f'Access denied: The Administrator Portal is restricted exclusively to System Administrators.', 'danger')
            if current_user.role == 'customer':
                return redirect(url_for('banking.dashboard'))
            elif current_user.role == 'manager':
                return redirect(url_for('manager.dashboard'))
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function
