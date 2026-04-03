from rest_framework.routers import DefaultRouter
from .views import BankViewSet

router = DefaultRouter()
router.register('accounts', BankViewSet)
router.register('accounts', BankViewSet, basename='accounts')

urlpatterns = router.urls