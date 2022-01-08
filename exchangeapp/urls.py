from django.urls import path

from exchangeapp.views import MyExchangeCreateView, MyExchangeDetailView, ForeignCurrencyCreateView
from portfolioapp.views import PortfolioCreateView, PortfolioDetailView

app_name = 'exchangeapp'

urlpatterns = [

    path('myexchange_create/', MyExchangeCreateView.as_view(), name='myexchange_create'),
    path('myexchange_detail/<int:pk>', MyExchangeDetailView.as_view(), name='myexchange_detail'),

    path('foreigncurrency_create/', ForeignCurrencyCreateView.as_view(), name='foreigncurrency_create'),
    # path('portfolio_refresh/<int:portfolio_pk>', portfolio_refresh, name='portfolio_refresh'),

]