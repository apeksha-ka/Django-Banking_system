from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import BankAccount, Transaction
from .Serializer import BankSerializer
from decimal import Decimal


class BankViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # ✅ ADD HERE (inside class)
    @action(detail=True, methods=['post'])
    def deposit(self, request, pk=None):
        account = self.get_object()
        amount = request.data.get('amount')

        if not amount:
            return Response({"error": "Amount is required"})
        
        
        if not amount:
         return Response({"error": "Amount is required"})

        amount = Decimal(amount)   # ✅ FIX

        account.balance += amount

        

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
        amount = float(request.data.get('amount', 0))

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