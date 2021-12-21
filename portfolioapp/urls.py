from django.urls import path

from portfolioapp.views import PortfolioCreateView, PortfolioDetailView

app_name = 'portfolioapp'

urlpatterns = [

    path('create/',PortfolioCreateView.as_view(), name='create'),
    path('detail/<int:pk>',PortfolioDetailView.as_view(), name='detail'),

]