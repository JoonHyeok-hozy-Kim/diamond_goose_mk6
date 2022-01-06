from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, ListView

from dashboardapp.models import Dashboard
from equityapp.models import Equity
from guardianapp.models import Guardian
from pensionapp.models import PensionAsset, Pension
from portfolioapp.decorators import portfolio_ownership_required
from portfolioapp.forms import PortfolioCreationForm
from portfolioapp.models import Portfolio

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
        context.update({'queryset_my_equities': queryset_my_equities})
        context.update({'asset_count_equity': queryset_my_equities.count()+1})

        queryset_my_guardians = Guardian.objects.filter(owner=self.request.user, portfolio=self.object.pk)
        context.update({'queryset_my_guardians': queryset_my_guardians})
        context.update({'asset_count_guardian': queryset_my_guardians.count()+1})

        queryset_my_pension_assets = PensionAsset.objects.filter(owner=self.request.user).order_by('pension')
        context.update({'queryset_my_pension_assets': queryset_my_pension_assets})
        context.update({'asset_count_pension_asset': queryset_my_pension_assets.count()+1})

        return context


