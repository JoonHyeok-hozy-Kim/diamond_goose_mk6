from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, DeleteView
from django.views.generic.edit import FormMixin

from assetmasterapp.models import Asset
from guardianapp.decorators import guardian_ownership_required
from guardianapp.forms import GuardianCreationForm, GuardianTransactionCreationForm
from guardianapp.models import Guardian, GuardianTransaction
from portfolioapp.models import Portfolio

has_guardian_ownership = [login_required, guardian_ownership_required]


class GuardianCreateView(CreateView):
    model = Guardian
    form_class = GuardianCreationForm
    template_name = 'guardianapp/guardian_create.html'

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


@method_decorator(has_guardian_ownership, 'get')
class GuardianDetailView(DetailView, FormMixin):
    model = Guardian
    form_class = GuardianTransactionCreationForm
    context_object_name = 'target_guardian'
    template_name = 'guardianapp/guardian_detail.html'

    def get_context_data(self, **kwargs):
        # Update Asset's current price
        self.object.asset.update_current_price()
        self.object.asset.refresh_from_db()

        # Update guardian's stats
        self.object.update_guardian_data()
        self.object.refresh_from_db()

        context = super(GuardianDetailView, self).get_context_data(**kwargs)

        my_portfolio_pk = self.object.portfolio.pk
        context.update({'my_portfolio_pk': my_portfolio_pk})

        my_guardian_transactions = GuardianTransaction.objects.filter(guardian=self.object.pk).order_by('-transaction_date')
        context.update({'my_guardian_transactions': my_guardian_transactions})

        return context


class GuardianDeleteView(DeleteView):
    model = Guardian
    context_object_name = 'target_guardian'
    template_name = 'guardianapp/guardian_delete.html'

    def get_success_url(self):
        return reverse('portfolioapp:detail', kwargs={'pk': self.object.portfolio.pk})


class GuardianTransactionCreateView(CreateView):
    model = GuardianTransaction
    form_class = GuardianTransactionCreationForm
    template_name = 'guardianapp/guardiantransaction_create.html'

    def form_valid(self, form):
        temp_transaction = form.save(commit=False)
        temp_transaction.guardian = Guardian.objects.get(pk=self.request.POST['guardian_pk'])

        if temp_transaction.transaction_type == 'SELL' and temp_transaction.quantity > temp_transaction.guardian.quantity:
            return HttpResponseNotFound('Cannot SELL more than you hold.')

        temp_transaction.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('guardianapp:guardian_detail', kwargs={'pk': self.object.guardian.pk})


class GuardianTransactionDeleteView(DeleteView):
    model = GuardianTransaction
    context_object_name = 'target_guardian_transaction'
    template_name = 'guardianapp/guardiantransaction_delete.html'

    def get_success_url(self):
        return reverse('guardianapp:guardian_detail', kwargs={'pk': self.object.guardian.pk})


def guardian_transaction_delete_all(request):

    guardian_pk = request.GET['guardian_pk']
    queryset_guardian_transactions = GuardianTransaction.objects.filter(guardian=guardian_pk)
    delete_count = 0
    asset_name = None
    for transaction in queryset_guardian_transactions:
        delete_count += 1
        asset_name = transaction.guardian.asset.name
        transaction.delete()
    print('Delete transaction of {}. {} row(s) deleted.'.format(asset_name, delete_count))

    target_guardian = Guardian.objects.get(pk=guardian_pk)
    target_guardian.update_guardian_data()
    target_guardian.refresh_from_db()

    return HttpResponseRedirect(reverse('guardianapp:guardian_detail', kwargs={'pk': guardian_pk}))