from django.forms import ModelForm

from equityapp.models import Equity


class EquityCreationForm(ModelForm):
    class Meta:
        model = Equity
        fields = []

