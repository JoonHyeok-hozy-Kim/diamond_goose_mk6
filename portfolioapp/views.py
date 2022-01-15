from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, ListView

from cryptoapp.models import Crypto
from dashboardapp.models import Dashboard
from equityapp.models import Equity
from exchangeapp.models import ForeignCurrency
from guardianapp.models import Guardian
from pensionapp.models import PensionAsset, Pension
from portfolioapp.decorators import portfolio_ownership_required
from portfolioapp.forms import PortfolioCreationForm
from portfolioapp.models import Portfolio
from reitsapp.models import Reits

has_ownership = [login_required, portfolio_ownership_required]


class PortfolioCreateView(CreateView):
    model = Portfolio
    form_class = PortfolioCreationForm
    context_object_name = 'target_portfolio'
    template_name = 'portfolioapp/create.html'

    def form_valid(self, form):
        temp_portfolio = form.save(commit=False)
        temp_portfolio.owner = self.request.user
        temp_portfolio.dashboard = Dashboard.objects.get(pk=self.request.POST['dashboard_pk'])
        temp_portfolio.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboardapp:detail', kwargs={'pk':self.request.POST['dashboard_pk']})


@method_decorator(has_ownership,'get')
class PortfolioDetailView(DetailView):
    model = Portfolio
    context_object_name = 'target_portfolio'
    template_name = 'portfolioapp/detail.html'

    def get_context_data(self, **kwargs):
        context = super(PortfolioDetailView, self).get_context_data(**kwargs)

        asset_type_count_list = self.object.count_by_asset()

        for element in asset_type_count_list:
            if element['asset_type'] == 'EQUITY':
                queryset_my_equities = Equity.objects.filter(owner=self.request.user,
                                                             portfolio=self.object.pk).order_by("asset")
                context.update({'queryset_my_equities': queryset_my_equities})
                context.update({'asset_count_equity': element['asset_count']+1})

            elif element['asset_type'] == 'CRYPTO':
                queryset_my_cryptoes = Crypto.objects.filter(owner=self.request.user).order_by("asset")
                context.update({'queryset_my_cryptoes': queryset_my_cryptoes})
                context.update({'asset_count_cryptoes': element['asset_count'] + 1})

            elif element['asset_type'] == 'REITS':
                queryset_my_reits = Reits.objects.filter(owner=self.request.user).order_by("asset")
                context.update({'queryset_my_reits': queryset_my_reits})
                context.update({'asset_count_reits': element['asset_count'] + 1})

            elif element['asset_type'] == 'GUARDIAN':
                queryset_my_guardians = Guardian.objects.filter(owner=self.request.user,
                                                                portfolio=self.object.pk).order_by("asset")
                context.update({'queryset_my_guardians': queryset_my_guardians})
                context.update({'asset_count_guardian': element['asset_count']+1})

            elif element['asset_type'] == 'PENSION':
                queryset_my_pension_assets = PensionAsset.objects.filter(owner=self.request.user).order_by('pension')
                context.update({'queryset_my_pension_assets': queryset_my_pension_assets})
                context.update({'asset_count_pension_asset': element['asset_count'] + 1})
                
        return context


def portfolio_refresh(request):

    try:
        queryset_my_portfolio = Portfolio.objects.get(owner=request.user)
        queryset_my_portfolio.update_current_value()
        queryset_my_portfolio.refresh_from_db()

    except Exception as identifier:
        print('portfolio_refresh:', identifier)

    return redirect('portfolioapp:detail', pk=queryset_my_portfolio.pk)