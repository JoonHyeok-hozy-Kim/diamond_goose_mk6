from django.urls import path

from equityapp.views import EquityCreateView, EquityDetailView, EquityListView, EquityTransactionCreateView, \
    EquityTransactionListView, EquityTransactionDeleteView, equitytransaction_export_csv_template, \
    equitytransaction_import_csv, EquityDeleteView

app_name = 'equityapp'

urlpatterns = [

    path('equity_create/', EquityCreateView.as_view(), name='equity_create'),
    path('equity_detail/<int:pk>', EquityDetailView.as_view(), name='equity_detail'),
    path('equity_list/', EquityListView.as_view(), name='equity_list'),
    path('equity_delete/<int:pk>', EquityDeleteView.as_view(), name='equity_delete'),

    path('equitytransaction_create', EquityTransactionCreateView.as_view(), name='equitytransaction_create'),
    path('equitytransaction_list/', EquityTransactionListView.as_view(), name='equitytransaction_list'),
    path('equitytransaction_delete/<int:pk>', EquityTransactionDeleteView.as_view(), name='equitytransaction_delete'),
    path('equitytransaction_export_csv_template/', equitytransaction_export_csv_template, name='equitytransaction_export_csv_template'),
    path('equitytransaction_import_csv/', equitytransaction_import_csv, name='equitytransaction_import_csv'),

]