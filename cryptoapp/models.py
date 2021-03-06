from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models import Q

from assetmasterapp.models import Asset
from portfolioapp.models import Portfolio


class Crypto(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='crypto', null=False)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='crypto', null=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crypto', null=False)

    quantity = models.FloatField(default=0, null=False)
    total_amount = models.FloatField(default=0, null=False)
    average_purchase_price_mv = models.FloatField(default=0, null=False)
    average_purchase_price_fifo = models.FloatField(default=0, null=False)

    rate_of_return_mv = models.FloatField(default=0, null=False)
    rate_of_return_fifo = models.FloatField(default=0, null=False)

    creation_date = models.DateTimeField(auto_now=True)
    last_update_date = models.DateTimeField(auto_now_add=True)

    def update_crypto_data(self):
        self.update_quantity_amount_prices()
        self.refresh_from_db()
        self.update_rate_of_returns()
        self.refresh_from_db()

    # def update_quantity_amount_prices(self):
    #     query = Q(transaction_type='BUY')
    #     query.add(Q(transaction_type='SELL'),Q.OR)
    #     query.add(Q(quantity__gt=0),Q.AND)
    #
    #     transaction_data_set = self.transaction.filter(query).values()
    #     crypto = Crypto.objects.filter(pk=self.pk)
    #
    #     # quantity
    #     final_quantity = 0
    #     for transaction_data in transaction_data_set:
    #         if transaction_data['transaction_type'] == 'BUY':
    #             final_quantity += transaction_data['quantity']
    #         elif transaction_data['transaction_type'] == 'SELL':
    #             final_quantity -= transaction_data['quantity']
    #
    #     crypto.update(quantity=final_quantity)
    #
    #     # amount
    #     current_price = self.asset.current_price
    #     crypto.update(total_amount=final_quantity*current_price)
    #
    #     # average_purchase_price_mv
    #     temp_qty = 0
    #     temp_amt = 0
    #     average_purchase_price_mv = 0
    #     max_qty_digit_for_fifo = 0
    #     for transaction_data in transaction_data_set:
    #
    #         # Calculate max digit of quantity for FIFO calculation
    #         qty_str_split_list = str(transaction_data['quantity']).split('.')
    #         if len(qty_str_split_list) > 1:
    #             qty_digit = len(qty_str_split_list[1])
    #             if qty_digit > max_qty_digit_for_fifo:
    #                 max_qty_digit_for_fifo = qty_digit
    #
    #         if transaction_data['transaction_type'] == 'BUY':
    #             temp_qty += transaction_data['quantity']
    #             temp_amt += transaction_data['quantity'] * transaction_data['price']
    #         elif transaction_data['transaction_type'] == 'SELL':
    #             temp_price = temp_amt/temp_qty
    #             temp_qty -= transaction_data['quantity']
    #             temp_amt = temp_qty * temp_price
    #
    #     if temp_qty < 0:
    #         average_purchase_price_mv = -999
    #     elif temp_qty > 0:
    #         average_purchase_price_mv = temp_amt/temp_qty
    #     crypto.update(average_purchase_price_mv=average_purchase_price_mv)
    #
    #     # average_purchase_price_fifo
    #     transaction_amount_list = []
    #     temp_qty = 0
    #     temp_amt = 0
    #
    #     if max_qty_digit_for_fifo > 0:
    #         qty_digit_unit = pow(10, max_qty_digit_for_fifo)
    #     else:
    #         qty_digit_unit = 1
    #
    #     for transaction_data in transaction_data_set:
    #         if transaction_data['transaction_type'] == 'BUY':
    #             for i in range(int(transaction_data['quantity']*qty_digit_unit)):
    #                 transaction_amount_list.append(transaction_data['price'])
    #         elif transaction_data['transaction_type'] == 'SELL':
    #             for i in range(int(transaction_data['quantity']*qty_digit_unit)):
    #                 transaction_amount_list.pop(0)
    #
    #     for transaction_amount in transaction_amount_list:
    #         temp_qty += 1
    #         temp_amt += transaction_amount
    #
    #     if temp_qty > 0: average_purchase_price_fifo = temp_amt/temp_qty
    #     else: average_purchase_price_fifo = 0
    #     crypto.update(average_purchase_price_fifo=average_purchase_price_fifo)
    #
    #     return {
    #         'quantity': final_quantity,
    #         'total_amount': final_quantity*current_price,
    #         'average_purchase_price_mv': average_purchase_price_mv,
    #         'average_purchase_price_fifo': average_purchase_price_fifo,
    #     }
    #
    # def update_rate_of_returns(self):
    #     crypto = Crypto.objects.filter(pk=self.pk)
    #
    #     rate_of_return_mv = 0
    #     if self.average_purchase_price_mv > 0:
    #         rate_of_return_mv = (self.asset.current_price - self.average_purchase_price_mv)/self.average_purchase_price_mv
    #     crypto.update(rate_of_return_mv=rate_of_return_mv)
    #
    #     rate_of_return_fifo = 0
    #     if self.average_purchase_price_fifo > 0:
    #         rate_of_return_fifo = (self.asset.current_price - self.average_purchase_price_fifo)/self.average_purchase_price_fifo
    #     crypto.update(rate_of_return_fifo=rate_of_return_fifo)
    #
    #     return{
    #         'rate_of_return_mv': rate_of_return_mv,
    #         'rate_of_return_fifo': rate_of_return_fifo,
    #     }

    def update_from_upbit(self):
        import jwt
        import uuid
        import hashlib
        from urllib.parse import urlencode

        import requests

        try:
            from diamond_goose_mk6.settings.local import UPBIT_ACCESS_KEY as access_key_local, UPBIT_SECRET_KEY as secret_key_local
            if access_key_local:
                access_key = access_key_local
                secret_key = secret_key_local
        except:
            from diamond_goose_mk6.settings.deploy import UPBIT_ACCESS_KEY as access_key_deploy, UPBIT_SECRET_KEY as secret_key_deploy
            access_key = access_key_deploy
            secret_key = secret_key_deploy

        server_url = "https://api.upbit.com"

        market = 'KRW-'
        market += self.asset.ticker
        query = {
            'market': market,
        }
        query_string = urlencode(query).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, secret_key)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.get(server_url + "/v1/orders/chance", params=query, headers=headers)

        # My Account Data in Json
        my_account = res.json()['ask_account']
        my_balance = float(my_account['balance'])
        my_avg_buy_price = float(my_account['avg_buy_price'])

        crypto = Crypto.objects.filter(pk=self.pk)
        crypto.update(quantity=my_balance)
        total_amount = my_balance * self.asset.current_price
        crypto.update(total_amount=total_amount)
        crypto.update(average_purchase_price_mv=my_avg_buy_price)
        crypto.update(average_purchase_price_fifo=my_avg_buy_price)
        rate_of_return = 0
        if my_avg_buy_price > 0:
            rate_of_return = (self.asset.current_price-my_avg_buy_price)/my_avg_buy_price
        crypto.update(rate_of_return_mv=rate_of_return)
        crypto.update(rate_of_return_fifo=rate_of_return)


TRANSACTION_TYPE_CHOICES = (
    ('BUY', '??????'),
    ('SELL', '??????'),
    ('DIVIDEND', '?????????'),
    ('SPLIT', '????????????'),
)


class MinValueFloat(models.FloatField):
    def __init__(self, min_value=None, *args, **kwargs):
        self.min_value = min_value
        super(MinValueFloat, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value}
        defaults.update(kwargs)
        return super(MinValueFloat, self).formfield(**defaults)



class CryptoTransaction(models.Model):
    from django import utils

    crypto = models.ForeignKey(Crypto, on_delete=models.CASCADE, related_name='transaction', null=False)

    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, null=False)
    quantity = MinValueFloat(min_value=0.0, null=False)

    price = MinValueFloat(min_value=0.0, default=0, null=False)
    transaction_fee = models.FloatField(default=0)
    transaction_tax = models.FloatField(default=0)
    transaction_date = models.DateTimeField(default=utils.timezone.now, null=False)
    note = models.CharField(max_length=40, default=' - ', null=True)

    split_cnt = models.IntegerField(default=0, null=False)

    creation_date = models.DateTimeField(auto_now=True)
    last_update_date = models.DateTimeField(auto_now_add=True)


