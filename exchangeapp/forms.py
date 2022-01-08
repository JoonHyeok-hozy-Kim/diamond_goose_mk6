from django.forms import ModelForm

from exchangeapp.models import MyExchange, ForeignCurrency


class MyExchangeCreationForm(ModelForm):
    class Meta:
        model = MyExchange
        fields = ['main_currency']


class ForeignCurrencyCreationForm(ModelForm):
    class Meta:
        model = ForeignCurrency
        fields = ['currency']

