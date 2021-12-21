from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, ListView

from assetmasterapp.models import Asset
from equityapp.decorators import equity_ownership_required
from equityapp.forms import EquityCreationForm
from equityapp.models import Equity
from portfolioapp.models import Portfolio

has_equity_ownership = [login_required, equity_ownership_required]


class EquityCreateView(CreateView):
    model = Equity
    form_class = EquityCreationForm
    context_object_name = 'target_equity'
    template_name = 'equityapp/equity_create.html'

    def form_valid(self, form):
        temp_equity = form.save(commit=False)
        temp_equity.owner = self.request.user
        temp_equity.asset = Asset.objects.get(pk=self.request.POST['asset_pk'])
        temp_equity.portfolio = Portfolio.objects.get(owner=self.request.user)
        temp_equity.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('equityapp:equity_detail', kwargs={'pk':self.object.asset.pk})


@method_decorator(has_equity_ownership,'get')
class EquityDetailView(DetailView):
    model = Equity
    context_object_name = 'target_equity'
    template_name = 'equityapp/equity_detail.html'

    def get_context_data(self, **kwargs):
        # Update Asset's current price
        self.object.asset.update_current_price()
        self.object.asset.refresh_from_db()

        context = super(EquityDetailView, self).get_context_data(**kwargs)

        my_portfolio_scalar_query = Portfolio.objects.filter(owner=self.request.user).values()
        if my_portfolio_scalar_query:
            for my_portfolio in my_portfolio_scalar_query:
                my_portfolio_pk = my_portfolio['id']
                target_user_id = my_portfolio['owner_id']
            context.update({'my_portfolio_pk': my_portfolio_pk})
            context.update({'target_user_id': target_user_id})

            my_equity_scalar_query = Equity.objects.filter(asset=self.object.pk,
                                                           portfolio=my_portfolio_pk,
                                                           owner=self.request.user).values()
            if my_equity_scalar_query:
                for my_equity in my_equity_scalar_query:
                    my_equity_pk = my_equity['id']
                context.update({'my_equity_pk': my_equity_pk})

        return context


@method_decorator(has_equity_ownership, 'get')
class EquityListView(ListView):
    model = Equity
    context_object_name = 'target_equity_list'
    template_name = 'equityapp/equity_list.html'