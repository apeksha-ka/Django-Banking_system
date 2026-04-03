from django.urls import path
from .views import register

from users.views import RegisterView, EmailTokenView
from users.views import ProfileView


urlpatterns = [
    path('api/register/', RegisterView.as_view()),
    path('api/login/', EmailTokenView.as_view()),  
     path('api/profile/', ProfileView.as_view()),
]