from django.forms import ModelForm
from django.forms import widgets
from guardianapp.models import Guardian, GuardianTransaction


class GuardianCreationForm(ModelForm):
    class Meta:
        model = Guardian
        fields = []


class GuardianTransactionCreationForm(ModelForm):
    class Meta:
        model = GuardianTransaction
        fields = ['transaction_type', 'quantity', 'price', 'transaction_fee', 'transaction_tax', 'transaction_date', 'note']

        widgets = {
            'transaction_date': widgets.DateTimeInput(attrs={'type': 'date'}),
        }