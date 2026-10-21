import random
import string
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from app.extensions import db
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.beneficiary import Beneficiary
from app.forms.services_forms import (
    CBCTransferForm, BeneficiaryForm, OwnAccountTransferForm,
    CBCCashOutForm, ATMCashOutForm, OtherBankTransferForm, AirtimeForm,
    BillsUtilitiesForm, TravelForm, ShoppingForm, GovernmentServicesForm,
    SubscriptionsForm, PayForForm, DonationForm, TaxPaymentForm, MyServiceForm
)
from app.utils.decorators import customer_required

services_bp = Blueprint('services', __name__, url_prefix='/services')


def _generate_code(length=8):
    """Generate a random alphanumeric code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


# ──────────────────────────────────────────────
# 1. My Account  (view account details)
# ──────────────────────────────────────────────
@services_bp.route('/my-account')
@customer_required
def my_account():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    total_balance = sum(a.balance for a in accounts)
    return render_template(
        'services/my_account.html',
        accounts=accounts,
        total_balance=total_balance
    )


# ──────────────────────────────────────────────
# 2. Transfer to CBC Account
# ──────────────────────────────────────────────
@services_bp.route('/cbc-transfer', methods=['GET', 'POST'])
@customer_required
def cbc_transfer():
    form = CBCTransferForm()
    accounts = Account.query.filter_by(user_id=current_user.id, status='active').all()

    if form.validate_on_submit():
        account_id = request.form.get('account_id', type=int)
        sender = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not sender:
            flash('Source account not found.', 'danger')
            return redirect(url_for('services.cbc_transfer'))

        recipient_number = form.recipient_account.data.strip()
        amount = float(form.amount.data)

        if recipient_number == sender.account_number:
            flash('Cannot transfer to the same account. Use Own Account Transfer.', 'danger')
            return redirect(url_for('services.cbc_transfer'))

        recipient = Account.query.filter_by(account_number=recipient_number).first()
        if not recipient:
            flash(f'CBC account #{recipient_number} not found.', 'danger')
            return redirect(url_for('services.cbc_transfer'))
        if recipient.status != 'active':
            flash('Recipient account is not active.', 'danger')
            return redirect(url_for('services.cbc_transfer'))
        if sender.balance < amount:
            flash(f'Insufficient funds. Available: ${sender.balance:,.2f}', 'danger')
            return redirect(url_for('services.cbc_transfer'))

        try:
            sender.balance -= amount
            recipient.balance += amount
            tx_ref = Transaction.generate_reference()

            db.session.add(Transaction(
                reference_id=tx_ref,
                account_id=sender.id,
                transaction_type='cbc_transfer_out',
                amount=amount,
                balance_after=sender.balance,
                description=f'CBC Transfer to {recipient.account_number}: {form.description.data}',
                related_account=recipient.account_number
            ))
            db.session.add(Transaction(
                reference_id=f"{tx_ref}-REC",
                account_id=recipient.id,
                transaction_type='cbc_transfer_in',
                amount=amount,
                balance_after=recipient.balance,
                description=f'CBC Transfer from {sender.account_number}: {form.description.data}',
                related_account=sender.account_number
            ))
            db.session.commit()
            flash(f'Successfully transferred {amount:,.2f} Birr to CBC account #{recipient_number}. Ref: {tx_ref}', 'success')
            return redirect(url_for('banking.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Transfer failed: {str(e)}', 'danger')

    return render_template('services/cbc_transfer.html', form=form, accounts=accounts)


# ──────────────────────────────────────────────
# 3. Beneficiary Management
# ──────────────────────────────────────────────
@services_bp.route('/beneficiaries')
@customer_required
def beneficiaries():
    user_beneficiaries = Beneficiary.query.filter_by(user_id=current_user.id).all()
    form = BeneficiaryForm()
    return render_template('services/beneficiaries.html', beneficiaries=user_beneficiaries, form=form)


@services_bp.route('/beneficiaries/add', methods=['POST'])
@customer_required
def add_beneficiary():
    form = BeneficiaryForm()
    if form.validate_on_submit():
        b = Beneficiary(
            user_id=current_user.id,
            name=form.name.data.strip(),
            account_number=form.account_number.data.strip(),
            bank_name=form.bank_name.data
        )
        db.session.add(b)
        db.session.commit()
        flash(f'Beneficiary "{b.name}" saved successfully!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{error}', 'danger')
    return redirect(url_for('services.beneficiaries'))


@services_bp.route('/beneficiaries/delete/<int:beneficiary_id>', methods=['POST'])
@customer_required
def delete_beneficiary(beneficiary_id):
    b = Beneficiary.query.filter_by(id=beneficiary_id, user_id=current_user.id).first()
    if b:
        db.session.delete(b)
        db.session.commit()
        flash(f'Beneficiary "{b.name}" removed.', 'info')
    else:
        flash('Beneficiary not found.', 'danger')
    return redirect(url_for('services.beneficiaries'))


# ──────────────────────────────────────────────
# 4. Own Account Transfer
# ──────────────────────────────────────────────
@services_bp.route('/own-transfer', methods=['GET', 'POST'])
@customer_required
def own_transfer():
    accounts = Account.query.filter_by(user_id=current_user.id, status='active').all()
    form = OwnAccountTransferForm()
    choices = [(a.id, f'{a.account_number} ({a.account_type.title()}) - ${a.balance:,.2f}') for a in accounts]
    form.from_account.choices = choices
    form.to_account.choices = choices

    if form.validate_on_submit():
        from_id = form.from_account.data
        to_id = form.to_account.data
        amount = float(form.amount.data)

        if from_id == to_id:
            flash('Source and destination must be different accounts.', 'danger')
            return redirect(url_for('services.own_transfer'))

        src = Account.query.filter_by(id=from_id, user_id=current_user.id).first()
        dst = Account.query.filter_by(id=to_id, user_id=current_user.id).first()
        if not src or not dst:
            flash('Account not found.', 'danger')
            return redirect(url_for('services.own_transfer'))
        if src.balance < amount:
            flash(f'Insufficient funds in {src.account_number}. Available: ${src.balance:,.2f}', 'danger')
            return redirect(url_for('services.own_transfer'))

        try:
            src.balance -= amount
            dst.balance += amount
            tx_ref = Transaction.generate_reference()
            db.session.add(Transaction(
                reference_id=tx_ref,
                account_id=src.id,
                transaction_type='own_transfer_out',
                amount=amount,
                balance_after=src.balance,
                description=f'Own transfer to {dst.account_number}: {form.description.data}',
                related_account=dst.account_number
            ))
            db.session.add(Transaction(
                reference_id=f"{tx_ref}-REC",
                account_id=dst.id,
                transaction_type='own_transfer_in',
                amount=amount,
                balance_after=dst.balance,
                description=f'Own transfer from {src.account_number}: {form.description.data}',
                related_account=src.account_number
            ))
            db.session.commit()
            flash(f'Transferred {amount:,.2f} Birr from {src.account_number} to {dst.account_number}.', 'success')
            return redirect(url_for('banking.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Transfer failed: {str(e)}', 'danger')

    return render_template('services/own_transfer.html', form=form, accounts=accounts)


# ──────────────────────────────────────────────
# 5. CBC Cash Out
# ──────────────────────────────────────────────
@services_bp.route('/cbc-cashout', methods=['GET', 'POST'])
@customer_required
def cbc_cashout():
    form = CBCCashOutForm()
    accounts = Account.query.filter_by(user_id=current_user.id, status='active').all()

    if form.validate_on_submit():
        account_id = request.form.get('account_id', type=int)
        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not account:
            flash('Account not found.', 'danger')
            return redirect(url_for('services.cbc_cashout'))

        amount = float(form.amount.data)
        if account.balance < amount:
            flash(f'Insufficient funds. Available: ${account.balance:,.2f}', 'danger')
            return redirect(url_for('services.cbc_cashout'))

        try:
            account.balance -= amount
            cashout_code = _generate_code(8)
            txn = Transaction(
                reference_id=Transaction.generate_reference(),
                account_id=account.id,
                transaction_type='cbc_cashout',
                amount=amount,
                balance_after=account.balance,
                description=f'CBC Cash-Out to {form.phone_number.data} | Code: {cashout_code}',
                related_account=f'PHONE:{form.phone_number.data}'
            )
            db.session.add(txn)
            db.session.commit()
            flash(f'Cash-Out code generated: {cashout_code} for {amount:,.2f} Birr. Share with receiver.', 'success')
            return redirect(url_for('banking.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Cash-Out failed: {str(e)}', 'danger')

    return render_template('services/cbc_cashout.html', form=form, accounts=accounts)


# ──────────────────────────────────────────────
# 6. ATM Cash Out (Cardless)
# ──────────────────────────────────────────────
@services_bp.route('/atm-cashout', methods=['GET', 'POST'])
@customer_required
def atm_cashout():
    form = ATMCashOutForm()
    accounts = Account.query.filter_by(user_id=current_user.id, status='active').all()

    if form.validate_on_submit():
        account_id = request.form.get('account_id', type=int)
        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not account:
            flash('Account not found.', 'danger')
            return redirect(url_for('services.atm_cashout'))

        amount = float(form.amount.data)
        if account.balance < amount:
            flash(f'Insufficient funds. Available: ${account.balance:,.2f}', 'danger')
            return redirect(url_for('services.atm_cashout'))

        try:
            account.balance -= amount
            atm_code = _generate_code(6)
            txn = Transaction(
                reference_id=Transaction.generate_reference(),
                account_id=account.id,
                transaction_type='atm_cashout',
                amount=amount,
                balance_after=account.balance,
                description=f'Cardless ATM Cash-Out | Code: {atm_code}',
                related_account='ATM-CARDLESS'
            )
            db.session.add(txn)
            db.session.commit()
            flash(f'ATM Code: {atm_code} — Use at any CBC ATM within 30 minutes. Amount: {amount:,.2f} Birr.', 'success')
            return redirect(url_for('banking.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'ATM Cash-Out failed: {str(e)}', 'danger')

    return render_template('services/atm_cashout.html', form=form, accounts=accounts)


# ──────────────────────────────────────────────
# 7. Other Bank Transfer
# ──────────────────────────────────────────────
@services_bp.route('/other-transfer', methods=['GET', 'POST'])
@customer_required
def other_transfer():
    form = OtherBankTransferForm()
    accounts = Account.query.filter_by(user_id=current_user.id, status='active').all()

    if form.validate_on_submit():
        account_id = request.form.get('account_id', type=int)
        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not account:
            flash('Account not found.', 'danger')
            return redirect(url_for('services.other_transfer'))

        amount = float(form.amount.data)
        if account.balance < amount:
            flash(f'Insufficient funds. Available: ${account.balance:,.2f}', 'danger')
            return redirect(url_for('services.other_transfer'))

        try:
            account.balance -= amount
            tx_ref = Transaction.generate_reference()
            txn = Transaction(
                reference_id=tx_ref,
                account_id=account.id,
                transaction_type='other_bank_transfer',
                amount=amount,
                balance_after=account.balance,
                description=f'Transfer to {form.recipient_name.data} at {form.bank_name.data}: {form.description.data}',
                related_account=f'{form.bank_name.data}:{form.recipient_account.data}'
            )
            db.session.add(txn)
            db.session.commit()
            flash(f'Transferred {amount:,.2f} Birr to {form.recipient_name.data} ({form.bank_name.data}). Ref: {tx_ref}', 'success')
            return redirect(url_for('banking.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Transfer failed: {str(e)}', 'danger')

    return render_template('services/other_transfer.html', form=form, accounts=accounts)


# ──────────────────────────────────────────────
# 8. Airtime Top-Up
# ──────────────────────────────────────────────
@services_bp.route('/airtime', methods=['GET', 'POST'])
@customer_required
def airtime():
    form = AirtimeForm()
    accounts = Account.query.filter_by(user_id=current_user.id, status='active').all()

    if form.validate_on_submit():
        account_id = request.form.get('account_id', type=int)
        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not account:
            flash('Account not found.', 'danger')
            return redirect(url_for('services.airtime'))

        amount = float(form.amount.data)
        if account.balance < amount:
            flash(f'Insufficient funds. Available: ${account.balance:,.2f}', 'danger')
            return redirect(url_for('services.airtime'))

        try:
            account.balance -= amount
            txn = Transaction(
                reference_id=Transaction.generate_reference(),
                account_id=account.id,
                transaction_type='airtime',
                amount=amount,
                balance_after=account.balance,
                description=f'Airtime top-up ({form.provider.data}) to {form.phone_number.data}',
                related_account=f'{form.provider.data}:{form.phone_number.data}'
            )
            db.session.add(txn)
            db.session.commit()
            flash(f'Airtime of {amount:,.2f} Birr sent to {form.phone_number.data} ({form.provider.data}).', 'success')
            return redirect(url_for('banking.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Airtime purchase failed: {str(e)}', 'danger')

    return render_template('services/airtime.html', form=form, accounts=accounts)


# ──────────────────────────────────────────────
# 9. Next (Services Page 2 Hub)
# ──────────────────────────────────────────────
@services_bp.route('/next')
@customer_required
def next_services():
    """Banking Services - Page 2 hub displaying extended services."""
    return render_template('services/next_services.html')


# ──────────────────────────────────────────────
# 9.1 Bills & Utilities
# ──────────────────────────────────────────────
@services_bp.route('/bills-utilities', methods=['GET', 'POST'])
@customer_required
def bills_utilities():
    form = BillsUtilitiesForm()
    accounts = Account.query.filter_by(user_id=current_user.id, status='active').all()

    if form.validate_on_submit():
        account_id = request.form.get('account_id', type=int)
        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not account:
            flash('Source account not found.', 'danger')
            return redirect(url_for('services.bills_utilities'))

        amount = float(form.amount.data)
        if account.balance < amount:
            flash(f'Insufficient funds. Available: ${account.balance:,.2f}', 'danger')
            return redirect(url_for('services.bills_utilities'))

        try:
            account.balance -= amount
            ref_id = Transaction.generate_reference()
            txn = Transaction(
                reference_id=ref_id,
                account_id=account.id,
                transaction_type='bill_payment',
                amount=amount,
                balance_after=account.balance,
                description=f'Bill: {form.biller_category.data} (Ref: {form.bill_reference.data}) - {form.description.data}',
                related_account=f'{form.biller_category.data}:{form.bill_reference.data}'
            )
            db.session.add(txn)
            db.session.commit()
            flash(f'Successfully paid {amount:,.2f} Birr for {form.biller_category.data}. Ref: {ref_id}', 'success')
            return redirect(url_for('banking.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Bill payment failed: {str(e)}', 'danger')

    return render_template('services/bills_utilities.html', form=form, accounts=accounts)


# ──────────────────────────────────────────────
# 9.2 Travel
# ──────────────────────────────────────────────
@services_bp.route('/travel', methods=['GET', 'POST'])
@customer_required
def travel():
    form = TravelForm()
    accounts = Account.query.filter_by(user_id=current_user.id, status='active').all()

    if form.validate_on_submit():
        account_id = request.form.get('account_id', type=int)
        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not account:
            flash('Source account not found.', 'danger')
            return redirect(url_for('services.travel'))

        amount = float(form.amount.data)
        if account.balance < amount:
            flash(f'Insufficient funds. Available: ${account.balance:,.2f}', 'danger')
            return redirect(url_for('services.travel'))

        try:
            account.balance -= amount
            ref_id = Transaction.generate_reference()
            txn = Transaction(
                reference_id=ref_id,
                account_id=account.id,
                transaction_type='travel',
                amount=amount,
                balance_after=account.balance,
                description=f'Travel: {form.travel_type.data} ({form.booking_reference.data}) - {form.passenger_name.data}',
                related_account=f'{form.travel_type.data}:{form.booking_reference.data}'
            )
            db.session.add(txn)
            db.session.commit()
            flash(f'Travel payment of {amount:,.2f} Birr confirmed for {form.passenger_name.data} ({form.travel_type.data}). Ref: {ref_id}', 'success')
            return redirect(url_for('banking.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Travel payment failed: {str(e)}', 'danger')

    return render_template('services/travel.html', form=form, accounts=accounts)


# ──────────────────────────────────────────────
# 9.3 Shopping
# ──────────────────────────────────────────────
@services_bp.route('/shopping', methods=['GET', 'POST'])
@customer_required
def shopping():
    form = ShoppingForm()
    accounts = Account.query.filter_by(user_id=current_user.id, status='active').all()

    if form.validate_on_submit():
        account_id = request.form.get('account_id', type=int)
        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not account:
            flash('Source account not found.', 'danger')
            return redirect(url_for('services.shopping'))

        amount = float(form.amount.data)
        if account.balance < amount:
            flash(f'Insufficient funds. Available: ${account.balance:,.2f}', 'danger')
            return redirect(url_for('services.shopping'))

        try:
            account.balance -= amount
            ref_id = Transaction.generate_reference()
            txn = Transaction(
                reference_id=ref_id,
                account_id=account.id,
                transaction_type='shopping',
                amount=amount,
                balance_after=account.balance,
                description=f'Shopping: {form.merchant_type.data} (Till: {form.merchant_code.data}, Inv: {form.invoice_number.data})',
                related_account=f'Till:{form.merchant_code.data}'
            )
            db.session.add(txn)
            db.session.commit()
            flash(f'Shopping payment of {amount:,.2f} Birr completed to Till #{form.merchant_code.data}. Ref: {ref_id}', 'success')
            return redirect(url_for('banking.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Shopping payment failed: {str(e)}', 'danger')

    return render_template('services/shopping.html', form=form, accounts=accounts)


# ──────────────────────────────────────────────
# 9.4 Government Services
# ──────────────────────────────────────────────
@services_bp.route('/government-services', methods=['GET', 'POST'])
@customer_required
def government_services():
    form = GovernmentServicesForm()
    accounts = Account.query.filter_by(user_id=current_user.id, status='active').all()

    if form.validate_on_submit():
        account_id = request.form.get('account_id', type=int)
        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not account:
            flash('Source account not found.', 'danger')
            return redirect(url_for('services.government_services'))

        amount = float(form.amount.data)
        if account.balance < amount:
            flash(f'Insufficient funds. Available: ${account.balance:,.2f}', 'danger')
            return redirect(url_for('services.government_services'))

        try:
            account.balance -= amount
            ref_id = Transaction.generate_reference()
            txn = Transaction(
                reference_id=ref_id,
                account_id=account.id,
                transaction_type='gov_service',
                amount=amount,
                balance_after=account.balance,
                description=f'Govt Fee: {form.agency.data} (App #{form.application_number.data}) for {form.applicant_name.data}',
                related_account=f'{form.agency.data}:{form.application_number.data}'
            )
            db.session.add(txn)
            db.session.commit()
            flash(f'Government fee of {amount:,.2f} Birr paid to {form.agency.data}. Official Ref: {ref_id}', 'success')
            return redirect(url_for('banking.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Government fee payment failed: {str(e)}', 'danger')

    return render_template('services/government_services.html', form=form, accounts=accounts)


# ──────────────────────────────────────────────
# 9.5 Subscriptions
# ──────────────────────────────────────────────
@services_bp.route('/subscriptions', methods=['GET', 'POST'])
@customer_required
def subscriptions():
    form = SubscriptionsForm()
    accounts = Account.query.filter_by(user_id=current_user.id, status='active').all()

    if form.validate_on_submit():
        account_id = request.form.get('account_id', type=int)
        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not account:
            flash('Source account not found.', 'danger')
            return redirect(url_for('services.subscriptions'))

        amount = float(form.amount.data)
        if account.balance < amount:
            flash(f'Insufficient funds. Available: ${account.balance:,.2f}', 'danger')
            return redirect(url_for('services.subscriptions'))

        try:
            account.balance -= amount
            ref_id = Transaction.generate_reference()
            txn = Transaction(
                reference_id=ref_id,
                account_id=account.id,
                transaction_type='subscription',
                amount=amount,
                balance_after=account.balance,
                description=f'Subscription: {form.subscription_service.data} - {form.package.data} (Acc: {form.account_number.data})',
                related_account=f'{form.subscription_service.data}:{form.account_number.data}'
            )
            db.session.add(txn)
            db.session.commit()
            flash(f'Subscription {form.subscription_service.data} ({form.package.data}) renewed for {amount:,.2f} Birr. Ref: {ref_id}', 'success')
            return redirect(url_for('banking.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Subscription renewal failed: {str(e)}', 'danger')

    return render_template('services/subscriptions.html', form=form, accounts=accounts)


# ──────────────────────────────────────────────
# 9.6 Pay For
# ──────────────────────────────────────────────
@services_bp.route('/pay-for', methods=['GET', 'POST'])
@customer_required
def pay_for():
    form = PayForForm()
    accounts = Account.query.filter_by(user_id=current_user.id, status='active').all()

    if form.validate_on_submit():
        account_id = request.form.get('account_id', type=int)
        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not account:
            flash('Source account not found.', 'danger')
            return redirect(url_for('services.pay_for'))

        amount = float(form.amount.data)
        if account.balance < amount:
            flash(f'Insufficient funds. Available: ${account.balance:,.2f}', 'danger')
            return redirect(url_for('services.pay_for'))

        try:
            account.balance -= amount
            ref_id = Transaction.generate_reference()
            txn = Transaction(
                reference_id=ref_id,
                account_id=account.id,
                transaction_type='pay_for',
                amount=amount,
                balance_after=account.balance,
                description=f'Pay For: {form.category.data} (Paybill: {form.paybill_number.data}, Ref: {form.reference_number.data})',
                related_account=f'{form.paybill_number.data}:{form.reference_number.data}'
            )
            db.session.add(txn)
            db.session.commit()
            flash(f'Payment of {amount:,.2f} Birr sent successfully to {form.paybill_number.data}. Ref: {ref_id}', 'success')
            return redirect(url_for('banking.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Payment failed: {str(e)}', 'danger')

    return render_template('services/pay_for.html', form=form, accounts=accounts)


# ──────────────────────────────────────────────
# 9.7 Donation
# ──────────────────────────────────────────────
@services_bp.route('/donation', methods=['GET', 'POST'])
@customer_required
def donation():
    form = DonationForm()
    accounts = Account.query.filter_by(user_id=current_user.id, status='active').all()

    if form.validate_on_submit():
        account_id = request.form.get('account_id', type=int)
        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not account:
            flash('Source account not found.', 'danger')
            return redirect(url_for('services.donation'))

        amount = float(form.amount.data)
        if account.balance < amount:
            flash(f'Insufficient funds. Available: ${account.balance:,.2f}', 'danger')
            return redirect(url_for('services.donation'))

        try:
            account.balance -= amount
            ref_id = Transaction.generate_reference()
            txn = Transaction(
                reference_id=ref_id,
                account_id=account.id,
                transaction_type='donation',
                amount=amount,
                balance_after=account.balance,
                description=f'Donation: {form.charity_name.data} - {form.cause.data} (Donor: {form.donor_name.data})',
                related_account=f'Charity:{form.charity_name.data}'
            )
            db.session.add(txn)
            db.session.commit()
            flash(f'Thank you! Your donation of {amount:,.2f} Birr to {form.charity_name.data} was successful. Ref: {ref_id}', 'success')
            return redirect(url_for('banking.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Donation failed: {str(e)}', 'danger')

    return render_template('services/donation.html', form=form, accounts=accounts)


# ──────────────────────────────────────────────
# 9.8 Tax Payment
# ──────────────────────────────────────────────
@services_bp.route('/tax-payment', methods=['GET', 'POST'])
@customer_required
def tax_payment():
    form = TaxPaymentForm()
    accounts = Account.query.filter_by(user_id=current_user.id, status='active').all()

    if form.validate_on_submit():
        account_id = request.form.get('account_id', type=int)
        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not account:
            flash('Source account not found.', 'danger')
            return redirect(url_for('services.tax_payment'))

        amount = float(form.amount.data)
        if account.balance < amount:
            flash(f'Insufficient funds. Available: ${account.balance:,.2f}', 'danger')
            return redirect(url_for('services.tax_payment'))

        try:
            account.balance -= amount
            ref_id = Transaction.generate_reference()
            txn = Transaction(
                reference_id=ref_id,
                account_id=account.id,
                transaction_type='tax_payment',
                amount=amount,
                balance_after=account.balance,
                description=f'Tax: {form.tax_type.data} (TIN: {form.tin_number.data}, Doc: {form.assessment_number.data})',
                related_account=f'TIN:{form.tin_number.data}'
            )
            db.session.add(txn)
            db.session.commit()
            flash(f'Tax payment of {amount:,.2f} Birr processed for TIN {form.tin_number.data}. Official Ref: {ref_id}', 'success')
            return redirect(url_for('banking.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Tax payment failed: {str(e)}', 'danger')

    return render_template('services/tax_payment.html', form=form, accounts=accounts)


# ──────────────────────────────────────────────
# 9.9 My Service
# ──────────────────────────────────────────────
@services_bp.route('/my-service', methods=['GET', 'POST'])
@customer_required
def my_service():
    form = MyServiceForm()
    accounts = Account.query.filter_by(user_id=current_user.id, status='active').all()

    if form.validate_on_submit():
        account_id = request.form.get('account_id', type=int)
        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        if not account:
            flash('Source account not found.', 'danger')
            return redirect(url_for('services.my_service'))

        amount = float(form.amount.data)
        if account.balance < amount:
            flash(f'Insufficient funds. Available: ${account.balance:,.2f}', 'danger')
            return redirect(url_for('services.my_service'))

        try:
            account.balance -= amount
            ref_id = Transaction.generate_reference()
            txn = Transaction(
                reference_id=ref_id,
                account_id=account.id,
                transaction_type='my_service',
                amount=amount,
                balance_after=account.balance,
                description=f'My Service: {form.service_name.data} ({form.service_provider.data} - {form.account_reference.data})',
                related_account=f'{form.service_provider.data}:{form.account_reference.data}'
            )
            db.session.add(txn)
            db.session.commit()
            flash(f'Payment of {amount:,.2f} Birr for "{form.service_name.data}" processed successfully. Ref: {ref_id}', 'success')
            return redirect(url_for('banking.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Custom service payment failed: {str(e)}', 'danger')

    return render_template('services/my_service.html', form=form, accounts=accounts)

