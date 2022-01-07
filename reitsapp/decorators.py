from django.http import HttpResponseForbidden
from reitsapp.models import Reits


def reits_ownership_required(func):
    def decorated(request, *args, **kwargs):
        reits = Reits.objects.get(pk=kwargs['pk'])
        if request.user != reits.owner:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)

    return decorated