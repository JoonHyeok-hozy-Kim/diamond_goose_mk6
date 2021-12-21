from django.urls import path

from equityapp.views import EquityCreateView, EquityDetailView, EquityListView

app_name = 'equityapp'

urlpatterns = [

    path('equity_create/',EquityCreateView.as_view(), name='equity_create'),
    path('equity_detail/<int:pk>',EquityDetailView.as_view(), name='equity_detail'),
    path('equity_list/',EquityListView.as_view(), name='equity_list'),

]