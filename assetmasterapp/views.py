import json
import os
import yfinance as yf
from django.contrib.sites import requests
from django.http import HttpResponseRedirect

from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.edit import  UpdateView, DeleteView
from django.utils.text import Truncator

from assetmasterapp.forms import AssetCreationForm
from assetmasterapp.models import Asset
from cryptoapp.models import Crypto
from equityapp.models import Equity
from guardianapp.models import Guardian
from portfolioapp.models import Portfolio


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

    def get_context_data(self, **kwargs):
        # Update Asset's current price
        self.object.update_current_price()
        self.object.refresh_from_db()

        context = super(AssetDetailView, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            my_portfolio_scalar_query = Portfolio.objects.filter(owner=self.request.user).values()
            if my_portfolio_scalar_query:
                for my_portfolio in my_portfolio_scalar_query:
                    my_portfolio_pk = my_portfolio['id']
                    target_user_id = my_portfolio['owner_id']
                context.update({'my_portfolio_pk': my_portfolio_pk})
                context.update({'target_user_id': target_user_id})

                my_asset_pk = None
                if self.object.asset_type == 'EQUITY':
                    my_equity_scalar_query = Equity.objects.filter(asset=self.object.pk,
                                                                   portfolio=my_portfolio_pk,
                                                                   owner=self.request.user).values()
                    if my_equity_scalar_query:
                        for my_equity in my_equity_scalar_query:
                            my_asset_pk = my_equity['asset_id']

                elif self.object.asset_type == 'GUARDIAN':
                    queryset_my_guardian = Guardian.objects.filter(asset=self.object.pk,
                                                                   portfolio=my_portfolio_pk,
                                                                   owner=self.request.user)
                    if queryset_my_guardian:
                        for my_guardian in queryset_my_guardian:
                            my_asset_pk = my_guardian.asset.pk

                elif self.object.asset_type == 'REITS':
                    None
                elif self.object.asset_type == 'PENSION':
                    None
                elif self.object.asset_type == 'CRYPTO':
                    queryset_my_crypto = Crypto.objects.filter(asset=self.object.pk,
                                                               portfolio=my_portfolio_pk,
                                                               owner=self.request.user)
                    if queryset_my_crypto:
                        for my_crypto in queryset_my_crypto:
                            my_asset_pk = my_crypto.asset.pk

                if my_asset_pk:
                    context.update({'my_asset_pk': my_asset_pk})
        return context


class AssetUpdateView(UpdateView):
    model = Asset
    form_class = AssetCreationForm
    context_object_name = 'target_asset'
    template_name = 'assetmasterapp/update.html'

    def get_success_url(self):
        return reverse('assetmasterapp:detail', kwargs={'pk':self.object.pk})


class AssetDeleteView(DeleteView):
    model = Asset
    context_object_name = 'target_asset'
    template_name = 'assetmasterapp/delete.html'

    def get_success_url(self):
        return reverse('assetmasterapp:list')