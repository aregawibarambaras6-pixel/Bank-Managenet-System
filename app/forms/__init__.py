from app.forms.auth_forms import LoginForm, RegisterForm
from app.forms.banking_forms import DepositForm, WithdrawForm, TransferForm, CreateAccountForm
from app.forms.loan_forms import LoanApplicationForm, LoanReviewForm
from app.forms.card_forms import IssueCardForm, UpdateCardLimitForm, ChangeCardPinForm
from app.forms.investment_forms import OpenDepositForm, DEPOSIT_PLANS
from app.forms.support_forms import SupportTicketForm, ManagerTicketReplyForm

__all__ = [
    'LoginForm', 'RegisterForm', 'DepositForm', 'WithdrawForm', 'TransferForm',
    'CreateAccountForm', 'LoanApplicationForm', 'LoanReviewForm',
    'IssueCardForm', 'UpdateCardLimitForm', 'ChangeCardPinForm',
    'OpenDepositForm', 'DEPOSIT_PLANS', 'SupportTicketForm', 'ManagerTicketReplyForm'
]
