from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, ListView

from cryptoapp.models import Crypto
from dashboardapp.models import Dashboard
from equityapp.models import Equity
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

        queryset_my_equities = Equity.objects.filter(owner=self.request.user, portfolio=self.object.pk)
        asset_count_equity = 1
        for equity in queryset_my_equities:
            equity.asset.update_current_price()
            # equity.update_equity_data()
            asset_count_equity += 1
        context.update({'queryset_my_equities': queryset_my_equities})
        context.update({'asset_count_equity': asset_count_equity})

        queryset_my_guardians = Guardian.objects.filter(owner=self.request.user, portfolio=self.object.pk)
        asset_count_guardian = 1
        for guardian in queryset_my_guardians:
            guardian.asset.update_current_price()
            # guardian.update_guardian_data()
            asset_count_guardian += 1
        context.update({'queryset_my_guardians': queryset_my_guardians})
        context.update({'asset_count_guardian': asset_count_guardian})

        queryset_my_pension_assets = PensionAsset.objects.filter(owner=self.request.user).order_by('pension')
        asset_count_pension_asset = 1
        for pension_asset in queryset_my_pension_assets:
            pension_asset.asset.update_current_price()
            # pension_asset.update_pension_asset_data()
            asset_count_pension_asset += 1
        context.update({'queryset_my_pension_assets': queryset_my_pension_assets})
        context.update({'asset_count_pension_asset': asset_count_pension_asset})

        queryset_my_cryptoes = Crypto.objects.filter(owner=self.request.user)
        asset_count_cryptoes = 1
        for crypto in queryset_my_cryptoes:
            crypto.asset.update_current_price()
            # crypto.update_crypto_data()
            asset_count_cryptoes += 1
        context.update({'queryset_my_cryptoes': queryset_my_cryptoes})
        context.update({'asset_count_cryptoes': asset_count_cryptoes})

        queryset_my_reits = Reits.objects.filter(owner=self.request.user)
        asset_count_reits = 1
        for reits in queryset_my_reits:
            reits.asset.update_current_price()
            # reits.update_reits_data()
            asset_count_reits += 1
        context.update({'queryset_my_reits': queryset_my_reits})
        context.update({'asset_count_reits': asset_count_reits})

        return context


# def portfolio_refresh(request):
#
#     print('request.path : ', request.path)
#     my_portfolio_pk = request.POST['portfolio_pk']
#     print('In portfolio_refresh, my_portfolio_pk :', my_portfolio_pk)
#
#     queryset_my_equities = Equity.objects.filter(owner=request.user, portfolio=my_portfolio_pk)
#     for equity in queryset_my_equities:
#         equity.asset.update_current_price()
#         equity.update_equity_data()
#
#     queryset_my_guardians = Guardian.objects.filter(owner=request.user, portfolio=my_portfolio_pk)
#     for guardian in queryset_my_guardians:
#         guardian.asset.update_current_price()
#         guardian.update_guardian_data()
#
#     queryset_my_pension_assets = PensionAsset.objects.filter(owner=request.user).order_by('pension')
#     for pension_asset in queryset_my_pension_assets:
#         pension_asset.asset.update_current_price()
#         pension_asset.update_pension_asset_data()
#
#     queryset_my_cryptoes = Crypto.objects.filter(owner=request.user)
#     for crypto in queryset_my_cryptoes:
#         crypto.asset.update_current_price()
#         crypto.update_crypto_data()
#
#     queryset_my_reits = Reits.objects.filter(owner=request.user)
#     for reits in queryset_my_reits:
#         reits.asset.update_current_price()
#         reits.update_reits_data()
#
#     return render(request, 'portfolioapp/detail.html', context={'pk': my_portfolio_pk})