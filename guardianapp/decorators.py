from django.http import HttpResponseForbidden

from guardianapp.models import Guardian


def guardian_ownership_required(func):
    def decorated(request, *args, **kwargs):
        guardian = Guardian.objects.get(pk=kwargs['pk'])
        if request.user != guardian.owner:
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)

    return decorated