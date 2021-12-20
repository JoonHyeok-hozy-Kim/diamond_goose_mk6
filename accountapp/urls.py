from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from accountapp.views import AccountCreateView, temp_welcome_view, AccountUpdateView, AccountDeleteView, \
    AccountDetailView

app_name = "accountapp"

urlpatterns = [

    path('temp_welcome/',temp_welcome_view,name='temp_welcome'),

    path('account_create/',AccountCreateView.as_view(),name='account_create'),
    path('account_update/<int:pk>',AccountUpdateView.as_view(),name='account_update'),
    path('account_delete/<int:pk>',AccountDeleteView.as_view(),name='account_delete'),
    path('account_detail/<int:pk>',AccountDetailView.as_view(),name='account_detail'),

    path('login/', LoginView.as_view(template_name='accountapp/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

]