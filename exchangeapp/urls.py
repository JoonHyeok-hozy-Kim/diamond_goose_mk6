from django.urls import path

from exchangeapp.views import MyExchangeCreateView, MyExchangeDetailView, ForeignCurrencyCreateView, \
    ForeignCurrencyDeleteView, ForeignCurrencyDetailView, ForeignCurrencyTransactionCreateView, \
    ForeignCurrencyTransactionDeleteView, foreign_currency_transaction_delete_all
from portfolioapp.views import PortfolioCreateView, PortfolioDetailView

app_name = 'exchangeapp'

urlpatterns = [

    path('myexchange_create/', MyExchangeCreateView.as_view(), name='myexchange_create'),
    path('myexchange_detail/<int:pk>', MyExchangeDetailView.as_view(), name='myexchange_detail'),

    path('foreigncurrency_create/', ForeignCurrencyCreateView.as_view(), name='foreigncurrency_create'),
    path('foreigncurrency_delete/<int:pk>', ForeignCurrencyDeleteView.as_view(), name='foreigncurrency_delete'),
    path('foreigncurrency_detail/<int:pk>', ForeignCurrencyDetailView.as_view(), name='foreigncurrency_detail'),
    # path('portfolio_refresh/<int:portfolio_pk>', portfolio_refresh, name='portfolio_refresh'),

    path('foreigncurrencytransaction_create/', ForeignCurrencyTransactionCreateView.as_view(), name='foreigncurrencytransaction_create'),
    path('foreigncurrencytransaction_delete/<int:pk>', ForeignCurrencyTransactionDeleteView.as_view(), name='foreigncurrencytransaction_delete'),
    path('foreigncurrencytransaction_delete_all/', foreign_currency_transaction_delete_all, name='foreigncurrencytransaction_delete_all'),

]