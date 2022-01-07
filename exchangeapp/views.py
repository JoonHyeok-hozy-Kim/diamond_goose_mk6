from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView

from dashboardapp.models import Dashboard
from exchangeapp.decorators import exchange_ownership_required
from exchangeapp.forms import MyExchangeCreationForm
from exchangeapp.models import MyExchange

has_ownership = [login_required, exchange_ownership_required]


class MyExchangeCreateView(CreateView):
    model = MyExchange
    form_class = MyExchangeCreationForm
    template_name = 'exchangeapp/create.html'
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
    template_name = 'exchangeapp/detail.html'

    def get_context_data(self, **kwargs):
        context = super(MyExchangeDetailView, self).get_context_data(**kwargs)


        return context