from django.urls import path

from exchangeapp.views import MyExchangeCreateView, MyExchangeDetailView
from portfolioapp.views import PortfolioCreateView, PortfolioDetailView

app_name = 'exchangeapp'

urlpatterns = [

    path('create/', MyExchangeCreateView.as_view(), name='create'),
    path('detail/<int:pk>', MyExchangeDetailView.as_view(), name='detail'),

    # path('portfolio_refresh/<int:portfolio_pk>', portfolio_refresh, name='portfolio_refresh'),

]