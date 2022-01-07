from django.forms import ModelForm

from exchangeapp.models import MyExchange


class MyExchangeCreationForm(ModelForm):
    class Meta:
        model = MyExchange
        fields = ['main_currency']

