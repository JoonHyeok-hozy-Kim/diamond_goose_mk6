from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from hozylabapp.views import lab_home_view, TempTransactionListView, upload_excel_daeshin

app_name = "hozylabapp"

urlpatterns = [

    path('lab_home/', lab_home_view, name='lab_home'),
    path('upload_excel_daeshin/', upload_excel_daeshin, name='upload_excel_daeshin'),

    path('temptransaction_list/', TempTransactionListView.as_view(), name='temptransaction_list'),
    # path('temptransaction_detail/', TempTransactionDetailView.as_view(), name='temptransaction_detail'),

]