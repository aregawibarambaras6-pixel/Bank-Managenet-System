"""
Database Seeding Module for Apex Bank Management System.
Populates realistic demo accounts and sample transaction data for immediate testing.
"""
from datetime import datetime, timedelta
from app.extensions import db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction

def seed_demo_data():
    # Only seed if no users exist
    if User.query.first():
        return

    print("🌱 Seeding initial demo users and banking records...")

    # 1. Demo Customer: Alex Mercer
    customer = User(
        full_name='Alex Mercer',
        username='customer',
        email='customer@apexbank.com',
        role='customer'
    )
    customer.set_password('password123')
    db.session.add(customer)
    db.session.flush()

    # Checking Account
    checking = Account(
        account_number='4040100001',
        user_id=customer.id,
        account_type='checking',
        balance=5420.50,
        currency='USD',
        status='active'
    )
    # Savings Account
    savings = Account(
        account_number='4040200002',
        user_id=customer.id,
        account_type='savings',
        balance=14850.00,
        currency='USD',
        status='active'
    )
    db.session.add(checking)
    db.session.add(savings)
    db.session.flush()

    # Checking Transactions
    now = datetime.utcnow()
    txns = [
        Transaction(
            reference_id='TXN-INIT0001',
            account_id=checking.id,
            transaction_type='deposit',
            amount=4000.00,
            balance_after=4000.00,
            description='Payroll Direct Deposit - Tech Corp',
            related_account='ACH-TRANSFER',
            timestamp=now - timedelta(days=5)
        ),
        Transaction(
            reference_id='TXN-INIT0002',
            account_id=checking.id,
            transaction_type='deposit',
            amount=2000.00,
            balance_after=6000.00,
            description='Freelance Consulting Invoice #418',
            related_account='WIRE-IN',
            timestamp=now - timedelta(days=3)
        ),
        Transaction(
            reference_id='TXN-INIT0003',
            account_id=checking.id,
            transaction_type='withdrawal',
            amount=579.50,
            balance_after=5420.50,
            description='Utility & Cloud Server Hosting',
            related_account='DEBIT-CARD',
            timestamp=now - timedelta(days=1)
        ),
        # Savings Transactions
        Transaction(
            reference_id='TXN-INIT0004',
            account_id=savings.id,
            transaction_type='deposit',
            amount=14500.00,
            balance_after=14500.00,
            description='High-Yield Emergency Reserve',
            related_account='INTERNAL-TRANSFER',
            timestamp=now - timedelta(days=10)
        ),
        Transaction(
            reference_id='TXN-INIT0005',
            account_id=savings.id,
            transaction_type='deposit',
            amount=350.00,
            balance_after=14850.00,
            description='Monthly Compounded Interest (4.5% APY)',
            related_account='APEX-INTEREST',
            timestamp=now - timedelta(days=1)
        )
    ]
    for t in txns:
        db.session.add(t)

    # 2. Demo Customer: Jordan Lee (for testing wire transfers)
    customer2 = User(
        full_name='Jordan Lee',
        username='jordan',
        email='jordan@example.com',
        role='customer'
    )
    customer2.set_password('password123')
    db.session.add(customer2)
    db.session.flush()

    account2 = Account(
        account_number='4040300003',
        user_id=customer2.id,
        account_type='checking',
        balance=3200.00,
        currency='USD',
        status='active'
    )
    db.session.add(account2)
    db.session.flush()

    db.session.add(Transaction(
        reference_id='TXN-INIT0006',
        account_id=account2.id,
        transaction_type='deposit',
        amount=3200.00,
        balance_after=3200.00,
        description='Initial Deposit',
        related_account='OPENING-BALANCE',
        timestamp=now - timedelta(days=7)
    ))

    # 3. Demo Manager: Sarah Jenkins
    manager = User(
        full_name='Sarah Jenkins',
        username='manager',
        email='manager@apexbank.com',
        role='manager'
    )
    manager.set_password('password123')
    db.session.add(manager)

    # 4. Demo Administrator: Apex Admin
    admin = User(
        full_name='Apex System Admin',
        username='admin',
        email='admin@apexbank.com',
        role='admin'
    )
    admin.set_password('password123')
    db.session.add(admin)

    db.session.commit()
    print("✅ Demo banking records seeded successfully.")
