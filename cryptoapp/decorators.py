from django.http import HttpResponseForbidden

from cryptoapp.models import Crypto


def crypto_ownership_required(func):
    def decorated(request, *args, **kwargs):
        crypto = Crypto.objects.get(pk=kwargs['pk'])
        if request.user != crypto.owner:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)

    return decorated