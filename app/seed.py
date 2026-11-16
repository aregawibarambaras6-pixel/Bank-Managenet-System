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
from app.models.fixed_deposit import FixedDeposit
from app.models.ticket import SupportTicket
from app.models.currency_rate import CurrencyRate
from app.models.standing_order import StandingOrder
from app.models.fx_conversion import FXConversion

def seed_demo_data():
    """Seed initial demo users, accounts, transactions, loans, cards, deposits, tickets, FX and orders."""
    if not User.query.first():
        _seed_users_and_accounts()

    _seed_loans()
    _seed_cards()
    _seed_notifications()
    _seed_fixed_deposits()
    _seed_support_tickets()
    _seed_currency_rates()
    _seed_multi_currency_accounts()
    _seed_standing_orders()
    _seed_fx_conversions()

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

def _seed_fixed_deposits():
    """Seed demo fixed deposits if none exist."""
    if FixedDeposit.query.first() is not None:
        return

    customer_user = User.query.filter_by(username='customer').first()
    if customer_user and customer_user.accounts:
        savings_acc = next((a for a in customer_user.accounts if a.account_type == 'savings'), customer_user.accounts[0])
        now = datetime.utcnow()

        fd1 = FixedDeposit(
            deposit_reference='FD-84920173',
            user_id=customer_user.id,
            account_id=savings_acc.id,
            plan_name='12-Month High Yield Certificate',
            principal_amount=5000.00,
            annual_rate=5.75,
            term_months=12,
            projected_interest=287.50,
            maturity_amount=5287.50,
            status='active',
            start_date=now - timedelta(days=60),
            maturity_date=now + timedelta(days=305)
        )

        fd2 = FixedDeposit(
            deposit_reference='FD-39108426',
            user_id=customer_user.id,
            account_id=savings_acc.id,
            plan_name='6-Month Growth Builder',
            principal_amount=2500.00,
            annual_rate=5.10,
            term_months=6,
            projected_interest=63.75,
            maturity_amount=2563.75,
            status='active',
            start_date=now - timedelta(days=30),
            maturity_date=now + timedelta(days=150)
        )

        db.session.add_all([fd1, fd2])
        db.session.commit()
        print("[OK] Demo fixed deposits seeded successfully.")

def _seed_support_tickets():
    """Seed demo customer support cases and dispute inquiries if none exist."""
    if SupportTicket.query.first() is not None:
        return

    customer_user = User.query.filter_by(username='customer').first()
    manager_user = User.query.filter_by(role='manager').first()
    first_txn = Transaction.query.first()

    if customer_user:
        now = datetime.utcnow()
        t1 = SupportTicket(
            ticket_number='TCK-84291',
            user_id=customer_user.id,
            transaction_id=first_txn.id if first_txn else None,
            subject='Inquiry regarding pending merchant hold',
            category='TRANSACTION_DISPUTE',
            priority='HIGH',
            status='IN_PROGRESS',
            message='I noticed a pending authorization hold on my debit card that was already completed via direct invoice. Could you please confirm if this hold will release automatically?',
            manager_reply='Hello Alex, we have contacted card merchant settlements. The temporary pre-authorization hold will auto-expire within 24 business hours without impacting your cleared balance.',
            assigned_manager_id=manager_user.id if manager_user else None,
            created_at=now - timedelta(days=2),
            updated_at=now - timedelta(hours=6)
        )

        t2 = SupportTicket(
            ticket_number='TCK-39104',
            user_id=customer_user.id,
            transaction_id=None,
            subject='Fixed deposit compound rate locks',
            category='GENERAL',
            priority='MEDIUM',
            status='RESOLVED',
            message='Are the fixed deposit yields guaranteed for the entire multi-year duration regardless of central bank interest rate changes?',
            manager_reply='Yes, all Apex Term Certificates lock in your fixed APY interest rate at inception. Your returns are completely protected against market fluctuations.',
            assigned_manager_id=manager_user.id if manager_user else None,
            created_at=now - timedelta(days=5),
            updated_at=now - timedelta(days=3)
        )

        db.session.add_all([t1, t2])
        db.session.commit()
        print("[OK] Demo support tickets seeded successfully.")

def _seed_currency_rates():
    """Seed baseline institutional currency exchange rates and spreads."""
    if CurrencyRate.query.first() is not None:
        return

    rates = [
        CurrencyRate(currency_code='USD', currency_name='US Dollar', symbol='$', rate_to_usd=1.0000, spread_pct=0.0, is_active=True),
        CurrencyRate(currency_code='EUR', currency_name='Euro', symbol='€', rate_to_usd=1.0850, spread_pct=0.8, is_active=True),
        CurrencyRate(currency_code='GBP', currency_name='British Pound', symbol='£', rate_to_usd=1.2820, spread_pct=0.8, is_active=True),
        CurrencyRate(currency_code='JPY', currency_name='Japanese Yen', symbol='¥', rate_to_usd=0.0065, spread_pct=0.9, is_active=True),
        CurrencyRate(currency_code='CAD', currency_name='Canadian Dollar', symbol='CA$', rate_to_usd=0.7350, spread_pct=0.8, is_active=True),
        CurrencyRate(currency_code='AUD', currency_name='Australian Dollar', symbol='A$', rate_to_usd=0.6550, spread_pct=0.8, is_active=True),
        CurrencyRate(currency_code='CHF', currency_name='Swiss Franc', symbol='CHF', rate_to_usd=1.1200, spread_pct=0.8, is_active=True)
    ]
    db.session.add_all(rates)
    db.session.commit()
    print("[OK] Demo institutional FX currency rates seeded successfully.")

def _seed_multi_currency_accounts():
    """Seed demo customer EUR and GBP multi-currency accounts if they don't already exist."""
    customer_user = User.query.filter_by(username='customer').first()
    if not customer_user:
        return

    existing_currencies = [a.currency for a in customer_user.accounts]
    now = datetime.utcnow()

    if 'EUR' not in existing_currencies:
        eur_acc = Account(
            account_number='1000800008001',
            user_id=customer_user.id,
            account_type='savings',
            balance=2400.00,
            currency='EUR',
            status='active',
            created_at=now - timedelta(days=20)
        )
        db.session.add(eur_acc)

    if 'GBP' not in existing_currencies:
        gbp_acc = Account(
            account_number='1000800008002',
            user_id=customer_user.id,
            account_type='checking',
            balance=1650.00,
            currency='GBP',
            status='active',
            created_at=now - timedelta(days=15)
        )
        db.session.add(gbp_acc)

    db.session.commit()
    print("[OK] Demo multi-currency accounts seeded successfully.")

def _seed_standing_orders():
    """Seed demo recurring standing orders and auto-pay mandates."""
    if StandingOrder.query.first() is not None:
        return

    customer_user = User.query.filter_by(username='customer').first()
    if customer_user and customer_user.accounts:
        primary_acc = customer_user.accounts[0]
        now = datetime.utcnow()

        so1 = StandingOrder(
            order_reference='SO-849201',
            user_id=customer_user.id,
            source_account_id=primary_acc.id,
            title='Apartment Residential Lease Rent',
            destination_type='EXTERNAL_BENEFICIARY',
            destination_account='METRO-PROPERTIES-LLC',
            amount=1200.00,
            frequency='MONTHLY',
            status='ACTIVE',
            next_execution_date=now + timedelta(days=5),
            last_execution_date=now - timedelta(days=25),
            total_executions=3,
            total_transferred=3600.00,
            created_at=now - timedelta(days=90)
        )

        so2 = StandingOrder(
            order_reference='SO-391084',
            user_id=customer_user.id,
            source_account_id=primary_acc.id,
            title='High-Yield Emergency Reserve Allocation',
            destination_type='INTERNAL_TRANSFER',
            destination_account='1000200002000',
            amount=250.00,
            frequency='BI_WEEKLY',
            status='ACTIVE',
            next_execution_date=now + timedelta(days=2),
            last_execution_date=now - timedelta(days=12),
            total_executions=6,
            total_transferred=1500.00,
            created_at=now - timedelta(days=85)
        )

        so3 = StandingOrder(
            order_reference='SO-719402',
            user_id=customer_user.id,
            source_account_id=primary_acc.id,
            title='Cloud Infrastructure & Web Hosting',
            destination_type='BILL_PAY',
            destination_account='APEX-CLOUD-HOSTING',
            amount=85.00,
            frequency='MONTHLY',
            status='PAUSED',
            next_execution_date=now + timedelta(days=14),
            last_execution_date=now - timedelta(days=45),
            total_executions=2,
            total_transferred=170.00,
            created_at=now - timedelta(days=75)
        )

        db.session.add_all([so1, so2, so3])
        db.session.commit()
        print("[OK] Demo standing orders seeded successfully.")

def _seed_fx_conversions():
    """Seed demo foreign currency conversion audit history."""
    if FXConversion.query.first() is not None:
        return

    customer_user = User.query.filter_by(username='customer').first()
    if customer_user and len(customer_user.accounts) >= 2:
        usd_acc = customer_user.accounts[0]
        other_acc = customer_user.accounts[1]
        now = datetime.utcnow()

        fx1 = FXConversion(
            reference_id='FX-92817402',
            user_id=customer_user.id,
            from_account_id=usd_acc.id,
            to_account_id=other_acc.id,
            from_currency='USD',
            to_currency='EUR',
            from_amount=1000.00,
            to_amount=914.29,
            exchange_rate=0.91429,
            spread_fee=7.37,
            created_at=now - timedelta(days=8)
        )

        fx2 = FXConversion(
            reference_id='FX-41098234',
            user_id=customer_user.id,
            from_account_id=usd_acc.id,
            to_account_id=other_acc.id,
            from_currency='USD',
            to_currency='GBP',
            from_amount=500.00,
            to_amount=387.16,
            exchange_rate=0.77432,
            spread_fee=3.12,
            created_at=now - timedelta(days=3)
        )

        db.session.add_all([fx1, fx2])
        db.session.commit()
        print("[OK] Demo FX conversion history seeded successfully.")

