"""
Database Seeding Module for Apex Bank Management System.
Populates realistic demo accounts and sample transaction data for immediate testing.
"""
from datetime import datetime, timedelta
from app.extensions import db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.loan import Loan
from app.models.card import Card
from app.models.notification import Notification

def seed_demo_data():
    """Seed initial demo users, accounts, transactions, loans, cards, and alerts."""
    if not User.query.first():
        _seed_users_and_accounts()

    _seed_loans()
    _seed_cards()
    _seed_notifications()

def _seed_users_and_accounts():
    print("[*] Seeding initial demo users and banking records...")

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
        account_number='1000100001000',
        user_id=customer.id,
        account_type='checking',
        balance=5420.50,
        currency='USD',
        status='active'
    )
    # Savings Account
    savings = Account(
        account_number='1000200002000',
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
        account_number='1000300003000',
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
    print("[OK] Demo banking records seeded successfully.")

def _seed_loans():
    """Seed demo loan applications if none exist."""
    if Loan.query.first() is not None:
        return

    customer_user = User.query.filter_by(username='customer').first()
    if customer_user and customer_user.accounts:
        checking_acc = customer_user.accounts[0]
        now = datetime.utcnow()
        demo_loan1 = Loan(
            loan_reference='LN-83921045',
            user_id=customer_user.id,
            account_id=checking_acc.id,
            loan_type='Auto Loan',
            amount=18000.00,
            annual_rate=7.0,
            term_months=36,
            monthly_payment=555.74,
            total_payable=20006.64,
            total_interest=2006.64,
            purpose='Electric vehicle purchase',
            monthly_income=6500.00,
            status='APPROVED',
            manager_notes='Approved by Branch Underwriting following income verification.',
            created_at=now - timedelta(days=20),
            reviewed_at=now - timedelta(days=19)
        )
        demo_loan2 = Loan(
            loan_reference='LN-91402831',
            user_id=customer_user.id,
            account_id=checking_acc.id,
            loan_type='Personal Loan',
            amount=5000.00,
            annual_rate=8.5,
            term_months=12,
            monthly_payment=436.09,
            total_payable=5233.08,
            total_interest=233.08,
            purpose='Home office renovation and equipment',
            monthly_income=6500.00,
            status='PENDING',
            created_at=now - timedelta(hours=5)
        )
        db.session.add(demo_loan1)
        db.session.add(demo_loan2)
        db.session.commit()
        print("[OK] Demo loan applications seeded successfully.")

def _seed_cards():
    """Seed demo debit and virtual cards if none exist."""
    if Card.query.first() is not None:
        return

    customer_user = User.query.filter_by(username='customer').first()
    if customer_user and customer_user.accounts:
        checking_acc = customer_user.accounts[0]
        
        card1 = Card(
            card_number='4532 8910 2345 6789',
            card_holder='ALEX MERCER',
            user_id=customer_user.id,
            account_id=checking_acc.id,
            card_type='virtual',
            card_network='Visa',
            card_design='emerald',
            cvv='482',
            expiry_date='08/29',
            status='active',
            daily_limit=2500.00,
            daily_spent=0.00
        )
        card1.set_pin('1234')

        card2 = Card(
            card_number='5421 9876 5432 1098',
            card_holder='ALEX MERCER',
            user_id=customer_user.id,
            account_id=checking_acc.id,
            card_type='physical',
            card_network='Mastercard',
            card_design='platinum',
            cvv='719',
            expiry_date='11/28',
            status='active',
            daily_limit=5000.00,
            daily_spent=0.00
        )
        card2.set_pin('5678')

        db.session.add(card1)
        db.session.add(card2)
        db.session.commit()
        print("[OK] Demo payment cards seeded successfully.")

def _seed_notifications():
    """Seed demo activity notifications if none exist."""
    if Notification.query.first() is not None:
        return

    customer_user = User.query.filter_by(username='customer').first()
    if customer_user:
        now = datetime.utcnow()
        n1 = Notification(
            user_id=customer_user.id,
            title='Direct Deposit Received',
            message='Payroll Direct Deposit of $4,000.00 from Tech Corp was credited to your Checking account.',
            category='success',
            created_at=now - timedelta(days=5)
        )
        n2 = Notification(
            user_id=customer_user.id,
            title='Auto Loan Approved',
            message='Your Auto Loan facility (LN-83921045) for $18,000.00 has been approved and funded.',
            category='info',
            created_at=now - timedelta(days=2)
        )
        n3 = Notification(
            user_id=customer_user.id,
            title='Virtual Visa Card Activated',
            message='Your Emerald Virtual Card ending in 6789 is active and ready for online spending.',
            category='success',
            created_at=now - timedelta(hours=3)
        )
        db.session.add_all([n1, n2, n3])
        db.session.commit()
        print("[OK] Demo notification alerts seeded successfully.")

