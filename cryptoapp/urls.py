from django.urls import path

from cryptoapp.views import CryptoCreateView, CryptoDetailView, CryptoDeleteView, CryptoTransactionCreateView, \
    CryptoTransactionDeleteView

app_name = 'cryptoapp'

urlpatterns = [

    path('crypto_create/', CryptoCreateView.as_view(), name='crypto_create'),
    path('crypto_detail/<int:pk>', CryptoDetailView.as_view(), name='crypto_detail'),
    path('crypto_delete/<int:pk>', CryptoDeleteView.as_view(), name='crypto_delete'),

    path('cryptotransaction_create', CryptoTransactionCreateView.as_view(), name='cryptotransaction_create'),
    path('cryptotransaction_delete/<int:pk>', CryptoTransactionDeleteView.as_view(), name='cryptotransaction_delete'),
    # path('equitytransaction_export_csv_template/', equitytransaction_export_csv_template, name='equitytransaction_export_csv_template'),
    # path('equitytransaction_import_csv/', equitytransaction_import_csv, name='equitytransaction_import_csv'),

]