from django.urls import path
from reitsapp.views import ReitsCreateView, ReitsDetailView, ReitsDeleteView, ReitsTransactionCreateView, \
    ReitsTransactionDeleteView, reits_transaction_delete_all

app_name = 'reitsapp'

urlpatterns = [

    path('reits_create/', ReitsCreateView.as_view(), name='reits_create'),
    path('reits_detail/<int:pk>', ReitsDetailView.as_view(), name='reits_detail'),
    path('reits_delete/<int:pk>', ReitsDeleteView.as_view(), name='reits_delete'),

    path('reitstransaction_create', ReitsTransactionCreateView.as_view(), name='reitstransaction_create'),
    path('reitstransaction_delete/<int:pk>', ReitsTransactionDeleteView.as_view(), name='reitstransaction_delete'),
    path('reits_transaction_delete_all/', reits_transaction_delete_all, name='reits_transaction_delete_all'),
    # path('reitstransaction_export_csv_template/', reitstransaction_export_csv_template, name='reitstransaction_export_csv_template'),
    # path('reitstransaction_import_csv/', reitstransaction_import_csv, name='reitstransaction_import_csv'),

]