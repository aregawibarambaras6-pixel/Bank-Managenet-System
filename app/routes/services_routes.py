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
    CBCCashOutForm, ATMCashOutForm, OtherBankTransferForm, AirtimeForm
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
