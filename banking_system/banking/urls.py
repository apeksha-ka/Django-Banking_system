from rest_framework.routers import DefaultRouter
from .views import BankViewSet, BankAPIView, account_details
from django.urls import path

router = DefaultRouter()
router.register('accounts', BankViewSet, basename='accounts')

urlpatterns = router.urls + [
    path('bank_accounts/', BankAPIView.as_view()),
    path('account-details/', account_details), 
]