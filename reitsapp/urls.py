from django.urls import path
from reitsapp.views import ReitsCreateView, ReitsDetailView, ReitsDeleteView, ReitsTransactionCreateView, \
    ReitsTransactionDeleteView

app_name = 'reitsapp'

urlpatterns = [

    path('reits_create/', ReitsCreateView.as_view(), name='reits_create'),
    path('reits_detail/<int:pk>', ReitsDetailView.as_view(), name='reits_detail'),
    path('reits_delete/<int:pk>', ReitsDeleteView.as_view(), name='reits_delete'),

    path('reitstransaction_create', ReitsTransactionCreateView.as_view(), name='reitstransaction_create'),
    path('reitstransaction_delete/<int:pk>', ReitsTransactionDeleteView.as_view(), name='reitstransaction_delete'),
    # path('equitytransaction_export_csv_template/', equitytransaction_export_csv_template, name='equitytransaction_export_csv_template'),
    # path('equitytransaction_import_csv/', equitytransaction_import_csv, name='equitytransaction_import_csv'),

]