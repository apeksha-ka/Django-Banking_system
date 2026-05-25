from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_views.login_page),
    path('login/', user_views.login_page),
    path('register/', user_views.register_page),
    path('dashboard/', views.dashboard),
    path('accounts/', views.accounts),
    path('accounts/<int:account_id>/', views.account_details),
    path('accounts/<int:account_id>/edit/', views.edit_account),
    path('accounts/<int:account_id>/transactions/', views.transactions_page),
    path('add-account/', views.add_account),
    path('edit-account/', views.edit_account),
    path('no-account/', views.no_account),
    path('summary/', views.summary_page),
    path('transfer/', views.transfer_page),
    path('transactions/<int:account_id>/', views.transactions_page),
    path('api/', include('banking.urls')),
    path('users/', include('users.urls')),
    path('debit/<int:account_id>/', views.debit_page),
]
