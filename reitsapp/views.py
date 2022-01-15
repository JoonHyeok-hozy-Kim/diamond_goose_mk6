from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, DeleteView
from django.views.generic.edit import FormMixin

from assetmasterapp.models import Asset
from portfolioapp.models import Portfolio
from reitsapp.decorators import reits_ownership_required
from reitsapp.forms import ReitsCreationForm, ReitsTransactionCreationForm
from reitsapp.models import Reits, ReitsTransaction

has_reits_ownership = [login_required, reits_ownership_required]


class ReitsCreateView(CreateView):
    model = Reits
    form_class = ReitsCreationForm
    template_name = 'reitsapp/reits_create.html'

    def form_valid(self, form):
        temp_guardian = form.save(commit=False)
        temp_guardian.owner = self.request.user
        temp_guardian.asset = Asset.objects.get(pk=self.request.POST['asset_pk'])
        temp_guardian.portfolio = Portfolio.objects.get(owner=self.request.user)
        temp_guardian.save()

        return super().form_valid(form)

    def get_success_url(self):
        # return reverse('guardianapp:guardian_detail', kwargs={'pk': self.object.pk})
        return reverse('portfolioapp:detail', kwargs={'pk': self.object.portfolio.pk})


@method_decorator(has_reits_ownership, 'get')
class ReitsDetailView(DetailView, FormMixin):
    model = Reits
    form_class = ReitsTransactionCreationForm
    context_object_name = 'target_reits'
    template_name = 'reitsapp/reits_detail.html'

    def get_context_data(self, **kwargs):
        # Update Asset's current price
        self.object.asset.update_current_price()
        self.object.asset.refresh_from_db()

        # Update reits's stats
        self.object.update_reits_data()
        self.object.refresh_from_db()

        context = super(ReitsDetailView, self).get_context_data(**kwargs)

        my_portfolio_pk = self.object.portfolio.pk
        context.update({'my_portfolio_pk': my_portfolio_pk})

        my_reits_transactions = ReitsTransaction.objects.filter(reits=self.object.pk).order_by('-transaction_date')
        context.update({'my_reits_transactions': my_reits_transactions})

        return context


class ReitsDeleteView(DeleteView):
    model = Reits
    context_object_name = 'target_reits'
    template_name = 'reitsapp/reits_delete.html'

    def get_success_url(self):
        return reverse('portfolioapp:detail', kwargs={'pk': self.object.portfolio.pk})


class ReitsTransactionCreateView(CreateView):
    model = ReitsTransaction
    form_class = ReitsTransactionCreationForm
    template_name = 'reitsapp/reitstransaction_create.html'

    def form_valid(self, form):
        temp_transaction = form.save(commit=False)
        temp_transaction.reits = Reits.objects.get(pk=self.request.POST['reits_pk'])

        if temp_transaction.transaction_type == 'SELL' and temp_transaction.quantity > temp_transaction.reits.quantity:
            return HttpResponseNotFound('Cannot SELL more than you hold.')

        temp_transaction.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('reitsapp:reits_detail', kwargs={'pk': self.object.reits.pk})


class ReitsTransactionDeleteView(DeleteView):
    model = ReitsTransaction
    context_object_name = 'target_reits_transaction'
    template_name = 'reitsapp/reitstransaction_delete.html'

    def get_success_url(self):
        return reverse('reitsapp:reits_detail', kwargs={'pk': self.object.reits.pk})


def reits_transaction_delete_all(request):

    reits_pk = request.GET['reits_pk']
    queryset_reits_transactions = ReitsTransaction.objects.filter(reits=reits_pk)
    delete_count = 0
    asset_name = None
    for transaction in queryset_reits_transactions:
        delete_count += 1
        asset_name = transaction.reits.asset.name
        transaction.delete()
    print('Delete transaction of {}. {} row(s) deleted.'.format(asset_name, delete_count))

    target_reits = Reits.objects.get(pk=reits_pk)
    target_reits.update_reits_data()
    target_reits.refresh_from_db()

    return HttpResponseRedirect(reverse('reitsapp:reits_detail', kwargs={'pk': reits_pk}))