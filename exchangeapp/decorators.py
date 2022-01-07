from django.http import HttpResponseForbidden

from exchangeapp.models import MyExchange
from portfolioapp.models import Portfolio


def exchange_ownership_required(func):
    def decorated(request, *args, **kwargs):
        exchange = MyExchange.objects.get(pk=kwargs['pk'])
        if request.user != exchange.owner:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)

    return decorated