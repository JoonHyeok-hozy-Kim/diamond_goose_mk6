from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, DeleteView
from django.views.generic.edit import FormMixin

from dashboardapp.models import Dashboard
from exchangeapp.decorators import exchange_ownership_required
from exchangeapp.forms import MyExchangeCreationForm, ForeignCurrencyCreationForm, \
    ForeignCurrencyTransactionCreationForm
from exchangeapp.models import MyExchange, ForeignCurrency, ForeignCurrencyTransaction

has_ownership = [login_required, exchange_ownership_required]


class MyExchangeCreateView(CreateView):
    model = MyExchange
    form_class = MyExchangeCreationForm
    template_name = 'exchangeapp/myexchange_create.html'
    _dashboard_pk = None

    def form_valid(self, form):
        temp_exchange = form.save(commit=False)
        temp_exchange.owner = self.request.user
        temp_exchange.dashboard = Dashboard.objects.get(owner=self.request.user)
        self._dashboard_pk = temp_exchange.dashboard.pk
        temp_exchange.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboardapp:detail', kwargs={'pk': self._dashboard_pk})


@method_decorator(has_ownership,'get')
class MyExchangeDetailView(DetailView):
    model = MyExchange
    context_object_name = 'my_exchange'
    template_name = 'exchangeapp/myexchange_detail.html'

    def get_context_data(self, **kwargs):
        context = super(MyExchangeDetailView, self).get_context_data(**kwargs)

        queryset_foreigncurrencies = ForeignCurrency.objects.filter(owner=self.request.user,
                                                                    exchange=self.object.pk)
        context.update({'queryset_foreigncurrencies': queryset_foreigncurrencies})

        return context


class ForeignCurrencyCreateView(CreateView):
    model = ForeignCurrency
    form_class = ForeignCurrencyCreationForm
    template_name = 'exchangeapp/foreigncurrency_create.html'
    _my_exchange_pk = None

    def form_valid(self, form):
        temp_currency = form.save(commit=False)
        temp_currency.owner = self.request.user
        temp_currency.exchange = MyExchange.objects.get(owner=self.request.user)
        self._my_exchange_pk = temp_currency.exchange.pk
        temp_currency.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('exchangeapp:myexchange_detail', kwargs={'pk': self._my_exchange_pk})


class ForeignCurrencyDeleteView(DeleteView):
    model = ForeignCurrency
    context_object_name = 'target_foreigncurrency'
    template_name = 'exchangeapp/foreigncurrency_delete.html'

    def get_success_url(self):
        return reverse('exchangeapp:myexchange_detail', kwargs={'pk': self.request.POST['myexchange_pk']})


class ForeignCurrencyDetailView(DetailView, FormMixin):
    model = ForeignCurrency
    context_object_name = 'target_foreign_currency'
    form_class = ForeignCurrencyTransactionCreationForm
    template_name = 'exchangeapp/foreigncurrency_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ForeignCurrencyDetailView, self).get_context_data(**kwargs)

        queryset_transaction_list = ForeignCurrencyTransaction.objects.filter(foreign_currency=self.object.pk).order_by("-transaction_date")
        context.update({'queryset_transaction_list': queryset_transaction_list})

        # Update Exchange Rate up-to-date.
        self.object.update_current_rate()
        self.object.refresh_from_db()

        return context


class ForeignCurrencyTransactionCreateView(CreateView):
    model = ForeignCurrencyTransaction
    form_class = ForeignCurrencyTransactionCreationForm
    template_name = 'exchangeapp/foreigncurrencytransaction_create.html'

    def form_valid(self, form):
        temp_transaction = form.save(commit=False)
        temp_transaction.foreign_currency = ForeignCurrency.objects.get(pk=self.request.POST['foreign_currency_pk'])

        if temp_transaction.transaction_type == 'SELL' and temp_transaction.quantity > temp_transaction.foreign_currency.quantity:
            return HttpResponseNotFound('Cannot SELL more than you hold.')

        temp_transaction.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('exchangeapp:foreigncurrency_detail', kwargs={'pk': self.object.foreign_currency.pk})


class ForeignCurrencyTransactionDeleteView(DeleteView):
    model = ForeignCurrencyTransaction
    context_object_name = 'target_foreign_currency_transaction'
    template_name = 'exchangeapp/foreigncurrencytransaction_delete.html'

    def get_success_url(self):
        return reverse('exchangeapp:foreigncurrency_detail', kwargs={'pk': self.object.foreign_currency.pk})