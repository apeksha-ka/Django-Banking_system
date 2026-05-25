from rest_framework import generics
from .models import User
from .serializers import RegisterSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from banking.models import BankAccount
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import User   
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import authenticate, login




class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer



from django.shortcuts import render, redirect
from .models import User

from django.shortcuts import render, redirect
from users.models import User
@csrf_exempt
def register_page(request):
  
    if request.method == 'POST':

        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        print(name)
        print(email)
        print(phone)
        print(password)

        # check existing email
        if User.objects.filter(email=email).exists():

            return render(request, 'register.html', {
                'error': 'Email already registered'
            })

        User.objects.create_user(
            name=name,
            email=email,
            phone=phone,
            password=password
        )

        return redirect('/login/')

    return render(request, 'register.html')


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
@csrf_exempt
def login_page(request):

    if request.method == 'POST':

        phone = request.POST.get('phone')
        password = request.POST.get('password')

        user = User.objects.filter(phone_number=phone).first()

        if user and user.check_password(password):

            login(request, user)
            return redirect('/dashboard/')

        else:
            return render(request, 'login.html', {
                'error': 'Invalid credentials'
            })

    return render(request, 'login.html')

def home(request):
    return HttpResponse("Users working")

class EmailTokenSerializer(TokenObtainPairSerializer):
    username_field = 'email'

class EmailTokenView(TokenObtainPairView):
    serializer_class = EmailTokenSerializer

from rest_framework.permissions import AllowAny

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


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
