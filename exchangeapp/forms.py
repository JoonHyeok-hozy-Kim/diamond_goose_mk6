from django.forms import widgets, ModelForm

from exchangeapp.models import MyExchange, ForeignCurrency, ForeignCurrencyTransaction


class MyExchangeCreationForm(ModelForm):
    class Meta:
        model = MyExchange
        fields = ['main_currency']


class ForeignCurrencyCreationForm(ModelForm):
    class Meta:
        model = ForeignCurrency
        fields = ['currency']


class ForeignCurrencyTransactionCreationForm(ModelForm):
    class Meta:
        model = ForeignCurrencyTransaction
        fields = ['transaction_type', 'quantity', 'exchange_rate', 'transaction_date', 'note']

        widgets = {
            'transaction_date': widgets.DateTimeInput(attrs={'type': 'date'}),
        }

