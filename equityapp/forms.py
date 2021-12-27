from django.forms import ModelForm
from django.forms import widgets

from equityapp.models import Equity, EquityTransaction


class EquityCreationForm(ModelForm):
    class Meta:
        model = Equity
        fields = []


class EquityTransactionCreationForm(ModelForm):
    class Meta:
        model = EquityTransaction
        fields = ['transaction_type', 'quantity', 'price', 'transaction_fee', 'transaction_tax', 'transaction_date', 'note']

        widgets = {
            'transaction_date': widgets.DateTimeInput(attrs={'type': 'date'}),
        }