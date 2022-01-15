from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.db.models import Q

from assetmasterapp.models import Asset
from portfolioapp.models import Portfolio


class Guardian(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='guardian', null=False)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='guardian', null=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guardian', null=False)

    quantity = models.FloatField(default=0, null=False)
    total_amount = models.FloatField(default=0, null=False)
    total_dividend_amount = models.FloatField(default=0, null=False)

    average_purchase_price_mv = models.FloatField(default=0, null=False)
    average_purchase_price_fifo = models.FloatField(default=0, null=False)

    rate_of_return_mv = models.FloatField(default=0, null=False)
    rate_of_return_fifo = models.FloatField(default=0, null=False)

    creation_date = models.DateTimeField(auto_now=True)
    last_update_date = models.DateTimeField(auto_now_add=True)

    def update_guardian_data(self):
        self.update_quantity_amount_prices()
        self.refresh_from_db()
        self.update_rate_of_returns()
        self.refresh_from_db()

    def update_quantity_amount_prices(self):
        query = Q(transaction_type='BUY')
        query.add(Q(transaction_type='SELL'),Q.OR)
        query.add(Q(transaction_type='DIVIDEND'),Q.OR)
        query.add(Q(transaction_type='SPLIT'),Q.OR)

        transaction_data_set = self.transaction.filter(query)
        guardian = Guardian.objects.filter(pk=self.pk)

        # quantity and amount
        final_quantity = 0
        total_dividend_amount = 0
        for transaction_data in transaction_data_set:
            if transaction_data.transaction_type == 'BUY':
                final_quantity += transaction_data.quantity
            elif transaction_data.transaction_type == 'SELL':
                final_quantity -= transaction_data.quantity
            elif transaction_data.transaction_type == 'DIVIDEND':
                total_dividend_amount += transaction_data.price
            elif transaction_data.transaction_type == 'SPLIT':
                final_quantity *= transaction_data.split_ratio_one_to_N

        guardian.update(quantity=final_quantity)
        current_price = self.asset.current_price
        guardian.update(total_amount=final_quantity*current_price)
        guardian.update(total_dividend_amount=total_dividend_amount)

        # average_purchase_price_mv
        temp_qty = 0
        temp_amt = 0
        average_purchase_price_mv = 0
        for transaction_data in transaction_data_set:
            if transaction_data.transaction_type == 'BUY':
                temp_qty += transaction_data.quantity
                temp_amt += transaction_data.quantity * transaction_data.price
            elif transaction_data.transaction_type == 'SELL':
                temp_price = temp_amt/temp_qty
                temp_qty -= transaction_data.quantity
                temp_amt = temp_qty * temp_price
            elif transaction_data.transaction_type == 'SPLIT':
                temp_qty *= transaction_data.split_ratio_one_to_N

        if temp_qty > 0: average_purchase_price_mv = temp_amt/temp_qty
        guardian.update(average_purchase_price_mv=average_purchase_price_mv)

        # average_purchase_price_fifo
        transaction_amount_list = []
        temp_qty = 0
        temp_amt = 0
        average_purchase_price_fifo = 0
        for transaction_data in transaction_data_set:
            if transaction_data.transaction_type == 'BUY':
                for i in range(int(transaction_data.quantity)):
                    transaction_amount_list.append(transaction_data.price)
            elif transaction_data.transaction_type == 'SELL':
                for i in range(int(transaction_data.quantity)):
                    transaction_amount_list.pop(0)
            elif transaction_data.transaction_type == 'SPLIT':
                if transaction_data.split_ratio_one_to_N > 1:
                    new_transaction_amount_list = []
                    for i in transaction_amount_list:
                        for j in range(transaction_data.split_ratio_one_to_N):
                            new_transaction_amount_list.append(i/transaction_data.split_ratio_one_to_N)
                    transaction_amount_list = new_transaction_amount_list

        for transaction_amount in transaction_amount_list:
            temp_qty += 1
            temp_amt += transaction_amount

        if temp_qty > 0: average_purchase_price_fifo = temp_amt/temp_qty
        guardian.update(average_purchase_price_fifo=average_purchase_price_fifo)

        return {
            'quantity': final_quantity,
            'total_amount': final_quantity*current_price,
            'average_purchase_price_mv': average_purchase_price_mv,
            'average_purchase_price_fifo': average_purchase_price_fifo,
        }

    def update_rate_of_returns(self):
        guardian = Guardian.objects.filter(pk=self.pk)

        rate_of_return_mv = 0
        if self.average_purchase_price_mv > 0:
            rate_of_return_mv = (self.asset.current_price - self.average_purchase_price_mv)/self.average_purchase_price_mv
        guardian.update(rate_of_return_mv=rate_of_return_mv)

        rate_of_return_fifo = 0
        if self.average_purchase_price_fifo > 0:
            rate_of_return_fifo = (self.asset.current_price - self.average_purchase_price_fifo)/self.average_purchase_price_fifo
        guardian.update(rate_of_return_fifo=rate_of_return_fifo)

        return{
            'rate_of_return_mv': rate_of_return_mv,
            'rate_of_return_fifo': rate_of_return_fifo,
        }

TRANSACTION_TYPE_CHOICES = (
    ('BUY', '매수'),
    ('SELL', '매도'),
    ('DIVIDEND', '배당금'),
    ('SPLIT', '액면분할'),
)


class MinValueFloat(models.FloatField):
    def __init__(self, min_value=None, *args, **kwargs):
        self.min_value = min_value
        super(MinValueFloat, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value}
        defaults.update(kwargs)
        return super(MinValueFloat, self).formfield(**defaults)


class GuardianTransaction(models.Model):
    from django import utils

    guardian = models.ForeignKey(Guardian, on_delete=models.CASCADE, related_name='transaction', null=False)

    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, null=False)
    quantity = MinValueFloat(min_value=0.0, null=False)

    price = MinValueFloat(min_value=0.0, default=0, null=False)
    transaction_fee = models.FloatField(default=0)
    transaction_tax = models.FloatField(default=0)
    transaction_date = models.DateTimeField(default=utils.timezone.now, null=False)
    note = models.CharField(max_length=40, default=' - ', null=True)

    split_ratio_one_to_N = models.IntegerField(default=0, null=True)

    creation_date = models.DateTimeField(auto_now=True)
    last_update_date = models.DateTimeField(auto_now_add=True)