from rest_framework import generics
from .models import User
from .serializers import RegisterSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from banking.models import BankAccount



class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer



from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class EmailTokenSerializer(TokenObtainPairSerializer):
    username_field = 'email'

class EmailTokenView(TokenObtainPairView):
    serializer_class = EmailTokenSerializer


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            account = BankAccount.objects.filter(user=user)
            total_balance = sum([acc.balance for acc in account]) if account else 0

            account_list = []
        
        except BankAccount.DoesNotExist:
            balance = 0

        for acc in account:
          account_list.append({
            "account_number": acc.account_number,
            "account_type": acc.account_type,
            "balance": acc.balance
        })

        return Response({
            "email": user.email,
            "name": user.name,
            "phone": user.phone,
            "balance": total_balance,
            "total_balance": total_balance,
           "total_accounts": account.count(),   
            "accounts": account_list  
        })