import json
import requests

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from dashboardapp.models import Dashboard

EXCHANGE_LOOKUP = (
    ('KRW', 'Korean Won(￦)'),
    ('USD', 'US Dollar($)'),
)

class MyExchange(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_exchange', null=False)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='my_exchange', null=False)

    main_currency = models.CharField(max_length=10, choices=EXCHANGE_LOOKUP, null=False)

    creation_date = models.DateTimeField(auto_now=True)
    last_update_date = models.DateTimeField(auto_now_add=True)


class ForeignCurrency(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='foreign_currency', null=False)
    exchange = models.ForeignKey(MyExchange, on_delete=models.CASCADE, related_name='foreign_currency', null=False)

    currency = models.CharField(max_length=10, choices=EXCHANGE_LOOKUP, null=False)
    current_exchange_rate = models.FloatField(default=0, null=False)

    current_amount = models.FloatField(default=0, null=False)

    accumulated_exchange_rate_mv = models.FloatField(default=0, null=False)
    accumulated_exchange_rate_fifo = models.FloatField(default=0, null=False)

    exchange_rate_of_return_mv = models.FloatField(default=0, null=False)
    exchange_rate_of_return_fifo = models.FloatField(default=0, null=False)

    def update_current_rate(self):
        from datetime import datetime

        url_list = ['https://www.koreaexim.go.kr/site/program/financial/exchangeJSON?']
        url_list.append('authkey=')
        try:
            from diamond_goose_mk6.settings.local import EXIM_BANK_API_KEY as key_local
            if key_local:
                url_list.append(key_local)
        except:
            from diamond_goose_mk6.settings.deploy import EXIM_BANK_API_KEY as key_deploy
            url_list.append(key_deploy)
        url_list.append('&searchdate=')
        url_list.append(datetime.today().strftime("%Y%m%d"))
        url_list.append('&data=AP01')

        url = ''.join(url_list)
        headers = {"Accept": "application/json"}
        response = requests.request("GET", url, headers=headers)
        dict_result = json.loads(response.text)

        for result in dict_result:
            if result['cur_unit'] == self.currency:
                exchange_rate_char_list = []
                for char in result['deal_bas_r']:
                    if char != ',':
                        exchange_rate_char_list.append(char)
                new_exchange_rate = round(float(''.join(exchange_rate_char_list)), 2)

                foreign_currency = ForeignCurrency.objects.filter(pk=self.pk)
                foreign_currency.update(current_exchange_rate=new_exchange_rate)
                break

        return new_exchange_rate

    def update_quantity_amount_rates(self):
        from django.db.models import Q
        query = Q(transaction_type='BUY')
        query.add(Q(transaction_type='SELL'),Q.OR)
        query.add(Q(quantity__gt=0),Q.AND)

        transaction_data_set = self.transaction.filter(query).values()
        foreign_currency = ForeignCurrency.objects.filter(pk=self.pk)

        # quantity and amount
        final_amount = 0
        max_qty_digit_for_fifo = 0
        for transaction_data in transaction_data_set:

            # Calculate max digit of quantity for FIFO calculation
            qty_str_split_list = str(transaction_data['quantity']).split('.')
            if len(qty_str_split_list) > 1:
                qty_digit = len(qty_str_split_list[1])
                if qty_digit > max_qty_digit_for_fifo:
                    max_qty_digit_for_fifo = qty_digit

            if transaction_data['transaction_type'] == 'BUY':
                final_amount += transaction_data['quantity']
            elif transaction_data['transaction_type'] == 'SELL':
                final_amount -= transaction_data['quantity']

        current_exchange_rate = self.current_exchange_rate
        foreign_currency.update(current_amount=final_amount)

        # accumulated_exchange_rate_mv
        temp_val_in_foreign_currency = 0
        temp_val_in_main_currency = 0
        accumulated_exchange_rate_mv = 0
        for transaction_data in transaction_data_set:
            if transaction_data['transaction_type'] == 'BUY':
                temp_val_in_foreign_currency += transaction_data['quantity']
                temp_val_in_main_currency += transaction_data['quantity'] * transaction_data['exchange_rate']
            elif transaction_data['transaction_type'] == 'SELL':
                temp_exchange_rate = temp_val_in_main_currency/temp_val_in_foreign_currency
                temp_val_in_foreign_currency -= transaction_data['quantity']
                temp_val_in_main_currency = temp_val_in_foreign_currency * temp_exchange_rate

        if temp_val_in_foreign_currency < 0:
            accumulated_exchange_rate_mv = -999
        elif temp_val_in_foreign_currency > 0:
            accumulated_exchange_rate_mv = round(temp_val_in_main_currency/temp_val_in_foreign_currency, 2)
        foreign_currency.update(accumulated_exchange_rate_mv=accumulated_exchange_rate_mv)

        # accumulated_exchange_rate_fifo
        transaction_amount_list = []
        temp_val_in_foreign_currency = 0
        temp_val_in_main_currency = 0
        if max_qty_digit_for_fifo > 0:
            qty_digit_unit = pow(10, max_qty_digit_for_fifo)
        else:
            qty_digit_unit = 1

        for transaction_data in transaction_data_set:
            if transaction_data['transaction_type'] == 'BUY':
                for i in range(int(transaction_data['quantity']*qty_digit_unit)):
                    transaction_amount_list.append(transaction_data['exchange_rate'])
            elif transaction_data['transaction_type'] == 'SELL':
                for i in range(int(transaction_data['quantity']*qty_digit_unit)):
                    transaction_amount_list.pop(0)

        for transaction_amount in transaction_amount_list:
            temp_val_in_foreign_currency += 1
            temp_val_in_main_currency += transaction_amount

        if temp_val_in_foreign_currency > 0:
            accumulated_exchange_rate_fifo = round(temp_val_in_main_currency/temp_val_in_foreign_currency, 2)
        else:
            accumulated_exchange_rate_fifo = 0
        foreign_currency.update(accumulated_exchange_rate_fifo=accumulated_exchange_rate_fifo)

        # exchange_rate_of_return_mv
        new_exchange_rate_of_return_mv = 0
        if accumulated_exchange_rate_mv > 0:
            new_exchange_rate_of_return_mv = (current_exchange_rate-accumulated_exchange_rate_mv)/accumulated_exchange_rate_mv
        foreign_currency.update(exchange_rate_of_return_mv=new_exchange_rate_of_return_mv)

        # exchange_rate_of_return_fifo
        new_exchange_rate_of_return_fifo = 0
        if accumulated_exchange_rate_fifo > 0:
            new_exchange_rate_of_return_fifo = (current_exchange_rate-accumulated_exchange_rate_fifo)/accumulated_exchange_rate_fifo
        foreign_currency.update(exchange_rate_of_return_fifo=new_exchange_rate_of_return_fifo)

        return {
            'current_amount': final_amount,
            'accumulated_exchange_rate_mv': accumulated_exchange_rate_mv,
            'accumulated_exchange_rate_fifo': accumulated_exchange_rate_fifo,
            'exchange_rate_of_return_mv': new_exchange_rate_of_return_mv,
            'exchange_rate_of_return_fifo': new_exchange_rate_of_return_fifo,
        }


TRANSACTION_TYPE_CHOICES = (
    ('BUY', '매수'),
    ('SELL', '매도'),
)


class MinValueFloat(models.FloatField):
    def __init__(self, min_value=None, *args, **kwargs):
        self.min_value = min_value
        super(MinValueFloat, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value}
        defaults.update(kwargs)
        return super(MinValueFloat, self).formfield(**defaults)


class ForeignCurrencyTransaction(models.Model):
    from django import utils
    foreign_currency = models.ForeignKey(ForeignCurrency, on_delete=models.CASCADE, related_name='transaction', null=False)

    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, null=False)
    quantity = MinValueFloat(min_value=0.0, null=False)
    exchange_rate = MinValueFloat(min_value=0.0, default=0, null=False)
    transaction_date = models.DateTimeField(default=utils.timezone.now, null=False)
    note = models.CharField(max_length=40, default=' - ', null=True)

    creation_date = models.DateTimeField(auto_now=True)
    last_update_date = models.DateTimeField(auto_now_add=True)