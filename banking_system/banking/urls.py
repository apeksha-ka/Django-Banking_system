from rest_framework.routers import DefaultRouter
from .views import BankViewSet, BankAPIView
from django.urls import path

router = DefaultRouter()
router.register('accounts', BankViewSet)

urlpatterns = router.urls + [path('bank_accounts', BankAPIView.as_view())]