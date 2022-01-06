from django.urls import path

from guardianapp.views import GuardianCreateView, GuardianDetailView, GuardianDeleteView, GuardianTransactionCreateView, \
    GuardianTransactionDeleteView

app_name = 'guardianapp'

urlpatterns = [

    path('guardian_create/', GuardianCreateView.as_view(), name='guardian_create'),
    path('guardian_detail/<int:pk>', GuardianDetailView.as_view(), name='guardian_detail'),
    # path('equity_list/', EquityListView.as_view(), name='equity_list'),
    path('guardian_delete/<int:pk>', GuardianDeleteView.as_view(), name='guardian_delete'),

    path('guardiantransaction_create', GuardianTransactionCreateView.as_view(), name='guardiantransaction_create'),
    # path('equitytransaction_list/', EquityTransactionListView.as_view(), name='equitytransaction_list'),
    path('guardiantransaction_delete/<int:pk>', GuardianTransactionDeleteView.as_view(), name='guardiantransaction_delete'),
    # path('equitytransaction_export_csv_template/', equitytransaction_export_csv_template, name='equitytransaction_export_csv_template'),
    # path('equitytransaction_import_csv/', equitytransaction_import_csv, name='equitytransaction_import_csv'),

]