from django.forms import ModelForm
from django.forms import widgets
from guardianapp.models import Guardian, GuardianTransaction
from reitsapp.models import Reits, ReitsTransaction


class ReitsCreationForm(ModelForm):
    class Meta:
        model = Reits
        fields = []


class ReitsTransactionCreationForm(ModelForm):
    class Meta:
        model = ReitsTransaction
        fields = ['transaction_type', 'quantity', 'price', 'transaction_fee', 'transaction_tax', 'transaction_date', 'note']

        widgets = {
            'transaction_date': widgets.DateTimeInput(attrs={'type': 'date'}),
        }