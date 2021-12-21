from django.http import HttpResponseForbidden

from equityapp.models import Equity


def equity_ownership_required(func):
    def decorated(request, *args, **kwargs):
        equity = Equity.objects.get(pk=kwargs['pk'])
        if request.user != equity.owner:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)

    return decorated