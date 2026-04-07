from django.urls import path
from users.views import RegisterView
from users.views import ProfileView
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', TokenObtainPairView.as_view()),  
     path('profile', ProfileView.as_view()),
]