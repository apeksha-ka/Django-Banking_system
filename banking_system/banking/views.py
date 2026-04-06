from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal

from .models import BankAccount, Transaction
from .Serializer import BankSerializer
from decimal import Decimal
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Transaction


class BankViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # ✅ DEPOSIT
    @action(detail=True, methods=['post'])
    def deposit(self, request, pk=None):
        account = self.get_object()
        amount = request.data.get('amount')

        if not amount:
            return Response({"error": "Amount is required"})

        amount = Decimal(amount)

        account.balance += amount
        account.save()

        Transaction.objects.create(
            account=account,
            transaction_type='deposit',
            amount=amount
        )

        return Response({"balance": account.balance})

    # ✅ WITHDRAW
    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        account = self.get_object()
        amount = request.data.get('amount')

        if not amount:
            return Response({"error": "Amount is required"})

        amount = Decimal(amount)

        if account.balance >= amount:
            account.balance -= amount
            account.save()

            Transaction.objects.create(
                account=account,
                transaction_type='withdraw',
                amount=amount
            )

            return Response({"balance": account.balance})

        return Response({"error": "Insufficient balance"})
    
    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        from decimal import Decimal
        from .models import BankAccount, Transaction

        from_account = self.get_object()
        to_account_number = request.data.get('to_account')
        amount = request.data.get('amount')

        if not to_account_number or not amount:
            return Response({"error": "to_account and amount required"})

        amount = Decimal(amount)

        try:
            to_account = BankAccount.objects.get(account_number=to_account_number)
        except BankAccount.DoesNotExist:
            return Response({"error": "Receiver not found"})

        if from_account.balance < amount:
            return Response({"error": "Insufficient balance"})

        from_account.balance -= amount
        to_account.balance += amount

        from_account.save()
        to_account.save()

        Transaction.objects.create(account=from_account, transaction_type='transfer_debit', amount=amount)
        Transaction.objects.create(account=to_account, transaction_type='transfer_credit', amount=amount)

        return Response({"message": "Transfer successful"})
    @action(detail=False, methods=['get'])
    def transaction_history(self, request):
       user = request.user

       transactions = Transaction.objects.filter(account__user=user).order_by('-id')

       data = []
       for t in transactions:
        data.append({
            "type": t.transaction_type,
            "amount": str(t.amount),
            "date": t.created_at
        })
       return Response(data)