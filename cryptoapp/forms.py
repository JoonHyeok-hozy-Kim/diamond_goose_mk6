from django.contrib.auth.models import User
from django.forms import ModelForm
from django.forms import widgets

from cryptoapp.models import Crypto, CryptoTransaction


class CryptoCreationForm(ModelForm):
    class Meta:
        model = Crypto
        fields = []


class CryptoTransactionCreationForm(ModelForm):

    class Meta:
        model = CryptoTransaction
        fields = ['transaction_type', 'quantity', 'price', 'transaction_fee', 'transaction_tax', 'transaction_date', 'note']

        widgets = {
            'transaction_date': widgets.DateTimeInput(attrs={'type': 'date'}),
        }