from django.urls import path

from assetmasterapp.views import AssetListView, AssetCreateView, AssetDetailView, AssetUpdateView, AssetDeleteView
from pensionapp.views import PensionAssetCreateView

app_name = 'assetmasterapp'

urlpatterns = [

    path('list/', AssetListView.as_view(), name='list'),
    path('create/', AssetCreateView.as_view(), name='create'),
    path('detail/<int:pk>', AssetDetailView.as_view(), name='detail'),
    path('update/<int:pk>', AssetUpdateView.as_view(), name='update'),
    path('delete/<int:pk>', AssetDeleteView.as_view(), name='delete'),

]