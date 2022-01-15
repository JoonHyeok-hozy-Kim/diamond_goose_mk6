from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, DeleteView
from django.views.generic.edit import FormMixin

from assetmasterapp.models import Asset
from cryptoapp.decorators import crypto_ownership_required
from cryptoapp.forms import CryptoCreationForm, CryptoTransactionCreationForm
from cryptoapp.models import Crypto, CryptoTransaction
from portfolioapp.models import Portfolio

has_crypto_ownership = [login_required, crypto_ownership_required]


class CryptoCreateView(CreateView):
    model = Crypto
    form_class = CryptoCreationForm
    template_name = 'cryptoapp/crypto_create.html'

    def form_valid(self, form):
        temp_crypto = form.save(commit=False)
        temp_crypto.owner = self.request.user
        temp_crypto.asset = Asset.objects.get(pk=self.request.POST['asset_pk'])
        temp_crypto.portfolio = Portfolio.objects.get(owner=self.request.user)
        temp_crypto.save()

        return super().form_valid(form)

    def get_success_url(self):
        # return reverse('cryptoapp:crypto_detail', kwargs={'pk': self.object.pk})
        return reverse('portfolioapp:detail', kwargs={'pk': self.object.portfolio.pk})


@method_decorator(has_crypto_ownership, 'get')
class CryptoDetailView(DetailView, FormMixin):
    model = Crypto
    form_class = CryptoTransactionCreationForm
    context_object_name = 'target_crypto'
    template_name = 'cryptoapp/crypto_detail.html'

    def get_context_data(self, **kwargs):
        # Update Asset's current price
        self.object.asset.update_current_price()
        self.object.asset.refresh_from_db()

        # Update Crypto's stats
        self.object.update_from_upbit()
        self.object.refresh_from_db()


        context = super(CryptoDetailView, self).get_context_data(**kwargs)

        my_portfolio_pk = self.object.portfolio.pk
        context.update({'my_portfolio_pk': my_portfolio_pk})

        my_crypto_transactions = CryptoTransaction.objects.filter(crypto=self.object.pk).order_by('-transaction_date')
        context.update({'my_crypto_transactions': my_crypto_transactions})

        return context


class CryptoDeleteView(DeleteView):
    model = Crypto
    context_object_name = 'target_crypto'
    template_name = 'cryptoapp/crypto_delete.html'

    def get_success_url(self):
        return reverse('portfolioapp:detail', kwargs={'pk': self.object.portfolio.pk})


class CryptoTransactionCreateView(CreateView):
    model = CryptoTransaction
    form_class = CryptoTransactionCreationForm
    template_name = 'cryptoapp/cryptotransaction_create.html'

    def form_valid(self, form):
        temp_transaction = form.save(commit=False)
        temp_transaction.crypto = Crypto.objects.get(pk=self.request.POST['crypto_pk'])

        if temp_transaction.transaction_type == 'SELL' and temp_transaction.quantity > temp_transaction.crypto.quantity:
            return HttpResponseNotFound('Cannot SELL more than you hold.')

        temp_transaction.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('cryptoapp:crypto_detail', kwargs={'pk': self.object.crypto.pk})


class CryptoTransactionDeleteView(DeleteView):
    model = CryptoTransaction
    context_object_name = 'target_crypto_transaction'
    template_name = 'cryptoapp/cryptotransaction_delete.html'

    def get_success_url(self):
        return reverse('cryptoapp:crypto_detail', kwargs={'pk': self.object.crypto.pk})