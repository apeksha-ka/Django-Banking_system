from decimal import Decimal, InvalidOperation

from django.core.paginator import Paginator
from django.db import transaction as db_transaction
from django.shortcuts import get_object_or_404, redirect, render

from banking.models import BankAccount, Transaction


def login_page(request):
    if request.method == 'POST':
        return redirect('/dashboard/')

    return render(request, 'login.html')


def register_page(request):
    return render(request, 'register.html')


def dashboard(request):
    return redirect('/accounts/')


def accounts(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    bank_accounts = BankAccount.objects.filter(user=request.user)
    return render(request, 'accounts.html', {'accounts': bank_accounts})


def _get_user_account(request, account_id):
    return get_object_or_404(
        BankAccount,
        id=account_id,
        user=request.user,
    )


def _parse_amount(value):
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError):
        return None

    if amount <= 0:
        return None

    return amount


def _render_with_error(request, template_name, context, error):
    return render(request, template_name, {**context, 'error': error})


def _transactions_with_running_balance(account):
    transactions = list(
        Transaction.objects.filter(account=account).order_by('-id')
    )

    running_balance = account.balance
    for transaction in transactions:
        transaction.display_balance = running_balance

        if transaction.transaction_type == 'Credit':
            running_balance -= transaction.amount
        elif transaction.transaction_type == 'Debit':
            running_balance += transaction.amount

    return transactions


def account_details(request, account_id):
    if not request.user.is_authenticated:
        return redirect('/login/')

    account = _get_user_account(request, account_id)
    transactions_list = _transactions_with_running_balance(account)
    paginator = Paginator(transactions_list, 3)
    page_number = request.GET.get('page')
    transactions = paginator.get_page(page_number)

    return render(request, 'account_details.html', {
        'account': account,
        'transactions': transactions,
    })


def add_account(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    if request.method == 'POST':
        account_holder = (request.POST.get('account_holder') or '').strip()
        account_number = (request.POST.get('account_number') or '').strip()
        account_type = request.POST.get('account_type') or 'Savings'
        ifsc_code = (request.POST.get('ifsc_code') or '').strip().upper()
        balance = _parse_amount(request.POST.get('balance'))

        if not account_number:
            return _render_with_error(request, 'add_account.html', {}, 'Enter an account number')

        if BankAccount.objects.filter(account_number=account_number).exists():
            return _render_with_error(request, 'add_account.html', {}, 'Account number already exists')

        BankAccount.objects.create(
            user=request.user,
            account_holder=account_holder,
            account_number=account_number,
            account_type=account_type.capitalize(),
            ifsc_code=ifsc_code,
            balance=balance or Decimal('0'),
        )

        return redirect('/accounts/')

    return render(request, 'add_account.html')


def edit_account(request, account_id=None):
    if not request.user.is_authenticated:
        return redirect('/login/')

    if account_id is None:
        return redirect('/accounts/')

    account = _get_user_account(request, account_id)

    if request.method == 'POST':
        account.account_holder = request.POST.get(
            'account_holder'
        ) or account.account_holder
        account.account_type = request.POST.get(
            'account_type'
        ) or account.account_type
        account.ifsc_code = (
            request.POST.get('ifsc_code') or account.ifsc_code
        ).upper()
        account.save()

        return redirect(f'/accounts/{account.id}/')

    return render(request, 'edit_account.html', {
        'account': account,
    })


def no_account(request):
    return render(request, 'no_account.html')


def summary_page(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    user_accounts = BankAccount.objects.filter(user=request.user)
    total_balance = sum(account.balance for account in user_accounts)

    return render(request, 'summary.html', {
        'accounts': user_accounts,
        'total_balance': total_balance,
        'total_accounts': user_accounts.count(),
    })


def transfer_page(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    accounts = BankAccount.objects.filter(user=request.user)

    if request.method == 'POST':
        from_account_id = request.POST.get('from_account')
        to_account_number = (request.POST.get('to_account') or '').strip()
        amount = _parse_amount(request.POST.get('amount'))

        if amount is None:
            return _render_with_error(request, 'transfer.html', {
                'accounts': accounts,
            }, 'Enter a valid amount')

        with db_transaction.atomic():
            from_account = get_object_or_404(
                BankAccount,
                id=from_account_id,
                user=request.user,
            )
            to_account = BankAccount.objects.filter(
                account_number=to_account_number
            ).first()

            if not to_account:
                return _render_with_error(request, 'transfer.html', {
                    'accounts': accounts,
                }, 'Account number not found')

            if to_account.id == from_account.id:
                return _render_with_error(request, 'transfer.html', {
                    'accounts': accounts,
                }, 'Choose a different account to transfer money')

            if from_account.balance < amount:
                return _render_with_error(request, 'transfer.html', {
                    'accounts': accounts,
                }, 'Insufficient balance')

            from_account.balance -= amount
            to_account.balance += amount
            from_account.save()
            to_account.save()

            Transaction.objects.create(
                account=from_account,
                transaction_type='Debit',
                amount=amount,
                balance=from_account.balance,
            )
            Transaction.objects.create(
                account=to_account,
                transaction_type='Credit',
                amount=amount,
                balance=to_account.balance,
            )

        return redirect(f'/accounts/{from_account.id}/')

    return render(request, 'transfer.html', {
        'accounts': accounts,
    })


def debit_page(request, account_id):
    if not request.user.is_authenticated:
        return redirect('/login/')

    account = _get_user_account(request, account_id)

    if request.method == 'POST':
        amount = _parse_amount(request.POST.get('amount'))

        if amount is None:
            return _render_with_error(request, 'debit_account.html', {
                'account': account,
            }, 'Enter a valid amount')

        if account.balance < amount:
            return _render_with_error(request, 'debit_account.html', {
                'account': account,
            }, 'Insufficient balance')

        with db_transaction.atomic():
            account.balance -= amount
            account.save()

            Transaction.objects.create(
                account=account,
                transaction_type='Debit',
                amount=amount,
                balance=account.balance,
            )

        return redirect(f'/accounts/{account.id}/')

    return render(request, 'debit_account.html', {'account': account})


def transactions_page(request, account_id):
    if not request.user.is_authenticated:
        return redirect('/login/')

    account = _get_user_account(request, account_id)

    if request.method == 'POST':
        amount = _parse_amount(request.POST.get('amount'))
        transaction_type = request.POST.get('transaction_type')

        if amount is None:
            return _render_with_error(request, 'transactions.html', {
                'account': account,
            }, 'Enter a valid amount')

        if transaction_type not in ('credit', 'debit'):
            return _render_with_error(request, 'transactions.html', {
                'account': account,
            }, 'Select a transaction type')

        if transaction_type == 'debit' and account.balance < amount:
            return _render_with_error(request, 'transactions.html', {
                'account': account,
            }, 'Insufficient balance')

        with db_transaction.atomic():
            if transaction_type == 'credit':
                account.balance += amount
            else:
                account.balance -= amount

            account.save()

            Transaction.objects.create(
                account=account,
                transaction_type=transaction_type.capitalize(),
                amount=amount,
                balance=account.balance,
            )

        return redirect(f'/accounts/{account.id}/')

    return render(request, 'transactions.html', {
        'account': account,
    })
