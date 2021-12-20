import json
import os
import yfinance as yf
from django.contrib.sites import requests
from django.http import HttpResponseRedirect

from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.edit import FormMixin, UpdateView, DeleteView
from django.utils.text import Truncator

from assetmasterapp.forms import AssetCreationForm
from assetmasterapp.models import Asset
from diamond_goose_mk6.settings import MEDIA_ROOT

class AssetListView(ListView):
    model = Asset
    context_object_name = 'target_asset_list'
    template_name = 'assetmasterapp/list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AssetListView, self).get_context_data(**kwargs)

        query_asset_list = Asset.objects.all().order_by('asset_type','ticker').values()
        for query_asset in query_asset_list:
            query_asset['name'] = Truncator(query_asset['name']).chars(29)
            query_asset['image'] = 'media/'+query_asset['image']

        context.update({'query_asset_list': query_asset_list})

        return context


class AssetCreateView(CreateView):
    model = Asset
    form_class = AssetCreationForm
    template_name = 'assetmasterapp/create.html'

    def get_success_url(self):
        return reverse('assetmasterapp:list')


class AssetDetailView(DetailView):
    model = Asset
    context_object_name = 'target_asset'
    template_name = 'assetmasterapp/detail.html'


class AssetUpdateView(UpdateView):
    model = Asset
    form_class = AssetCreationForm
    context_object_name = 'target_asset'
    template_name = 'assetmasterapp/update.html'

    def get_success_url(self):
        return reverse('assetmasterapp:detail',kwargs={'pk':self.object.pk})


class AssetDeleteView(DeleteView):
    model = Asset
    context_object_name = 'target_asset'
    template_name = 'assetmasterapp/delete.html'

    def get_success_url(self):
        return reverse('assetmasterapp:list')