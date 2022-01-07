from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelChoiceField

# Create your models here.
from django.db.models import Q

from assetmasterapp.models import Asset
from dashboardapp.models import Dashboard
from portfolioapp.models import Portfolio

PENSION_TYPES = (
    ('퇴직연금', '퇴직연금'),
    ('연금저축', '연금저축'),
    ('IRP', 'IRP'),
)


class Pension(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pension')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='pension')

    pension_type = models.CharField(max_length=30, choices=PENSION_TYPES, null=False)
    total_paid_amount = models.FloatField(default=0, null=False)
    total_current_value = models.FloatField(default=0, null=False)
    total_cash_amount = models.FloatField(default=0, null=False)
    total_profit_amount = models.FloatField(default=0, null=False)
    rate_of_return = models.FloatField(default=0, null=False)

    risk_ratio_force_flag = models.BooleanField(default=False, null=False)
    risk_ratio = models.FloatField(default=0.7, null=True)
    current_risk_asset_ratio = models.FloatField(default=0, null=True)

    def __str__(self):
        return f'{self.pension_type}'

    def update_parameters(self):
        self.calculate_total_paid_amount()
        self.refresh_from_db()
        self.calculate_total_current_value_total_cash_amount_current_risk_asset_ratio()
        self.refresh_from_db()
        self.calculate_total_profit_amount_rate_of_return()
        self.refresh_from_db()

    def calculate_total_paid_amount(self):
        pension_transaction_query = self.pension_transaction.all()
        new_total_paid_amount = 0
        for transaction in pension_transaction_query:
            if transaction.transaction_type == 'PAY':
                new_total_paid_amount += transaction.amount
            else:
                new_total_paid_amount -= transaction.amount

        pension = Pension.objects.filter(pk=self.pk)
        pension.update(total_paid_amount=new_total_paid_amount)
        return new_total_paid_amount

    def calculate_total_current_value_total_cash_amount_current_risk_asset_ratio(self):
        queryset_pension_asset = self.pension_asset.all()
        total_asset_purchase_amount = 0
        total_asset_dividend_amount = 0
        total_current_value = 0
        current_risk_asset_ratio = 0
        current_risk_asset_amount = 0

        for pension_asset in queryset_pension_asset:
            total_asset_purchase_amount += pension_asset.average_purchase_price_mv * pension_asset.quantity
            total_asset_dividend_amount += pension_asset.total_dividend_amount
            total_current_value += pension_asset.total_amount
            if not pension_asset.asset.pension_non_risk_asset_flag:
                current_risk_asset_amount += pension_asset.total_amount

        total_cash_amount = self.total_paid_amount + total_asset_dividend_amount - total_asset_purchase_amount
        total_current_value += total_cash_amount
        if current_risk_asset_amount > 0:
            current_risk_asset_ratio = current_risk_asset_amount / total_current_value

        pension = Pension.objects.filter(pk=self.pk)
        pension.update(total_cash_amount=total_cash_amount)
        pension.update(total_current_value=total_current_value)
        pension.update(current_risk_asset_ratio=current_risk_asset_ratio)

        return {'total_current_value': total_current_value, 'total_cash_amount': total_cash_amount}

    def calculate_total_profit_amount_rate_of_return(self):
        total_profit_amount = 0
        if self.total_paid_amount > 0:
            total_profit_amount += self.total_current_value - self.total_paid_amount
        rate_of_return = 0
        if self.total_paid_amount > 0:
            rate_of_return += total_profit_amount/self.total_paid_amount

        pension = Pension.objects.filter(pk=self.pk)
        pension.update(total_profit_amount=total_profit_amount)
        pension.update(rate_of_return=rate_of_return)

        return {'total_profit_amount': total_profit_amount, 'rate_of_return': rate_of_return}


PENSION_TRANSACTION_TYPES = (
    ('PAY', '납입'),
    ('RECEIVE', '수령'),
)


class PensionTransaction(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pension_transaction')
    pension = models.ForeignKey(Pension, on_delete=models.CASCADE, related_name='pension_transaction')

    transaction_type = models.CharField(max_length=20, choices=PENSION_TRANSACTION_TYPES, null=False)
    amount = models.FloatField(default=0, null=False)

    transaction_date = models.DateTimeField(null=False)
    creation_date = models.DateTimeField(auto_now=True)
    last_update_date = models.DateTimeField(auto_now_add=True)


class PensionAsset(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='pension_asset', null=False)
    pension = models.ForeignKey(Pension, on_delete=models.CASCADE, related_name='pension_asset', null=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pension_asset', null=False)

    quantity = models.FloatField(default=0, null=False)
    total_amount = models.FloatField(default=0, null=False)
    total_dividend_amount = models.FloatField(default=0, null=False)
    average_purchase_price_mv = models.FloatField(default=0, null=False)
    average_purchase_price_fifo = models.FloatField(default=0, null=False)

    rate_of_return_mv = models.FloatField(default=0, null=False)
    rate_of_return_fifo = models.FloatField(default=0, null=False)

    creation_date = models.DateTimeField(auto_now=True)
    last_update_date = models.DateTimeField(auto_now_add=True)

    def update_pension_asset_data(self):
        self.update_quantity_amount_prices()
        self.refresh_from_db()
        self.update_rate_of_returns()
        self.refresh_from_db()

    def update_quantity_amount_prices(self):
        query = Q(transaction_type='BUY')
        query.add(Q(transaction_type='SELL'),Q.OR)
        query.add(Q(transaction_type='DIVIDEND'),Q.OR)
        query.add(Q(quantity__gt=0),Q.AND)

        transaction_data_set = self.transaction.filter(query).values()
        pension_asset = PensionAsset.objects.filter(pk=self.pk)

        # quantity and amount
        final_quantity = 0
        total_dividend_amount = 0
        for transaction_data in transaction_data_set:
            if transaction_data['transaction_type'] == 'BUY':
                final_quantity += transaction_data['quantity']
            elif transaction_data['transaction_type'] == 'SELL':
                final_quantity -= transaction_data['quantity']
            elif transaction_data['transaction_type'] == 'DIVIDEND':
                total_dividend_amount += transaction_data['price'] * transaction_data['quantity']

        current_price = self.asset.current_price
        total_amount = final_quantity*current_price
        pension_asset.update(quantity=final_quantity)
        pension_asset.update(total_dividend_amount=total_dividend_amount)
        pension_asset.update(total_amount=total_amount)

        # average_purchase_price_mv
        temp_qty = 0
        temp_amt = 0
        average_purchase_price_mv = 0
        for transaction_data in transaction_data_set:
            if transaction_data['transaction_type'] == 'BUY':
                temp_qty += transaction_data['quantity']
                temp_amt += transaction_data['quantity'] * transaction_data['price']
            else:
                temp_price = temp_amt/temp_qty
                temp_qty -= transaction_data['quantity']
                temp_amt = temp_qty * temp_price

        if temp_qty < 0: average_purchase_price_mv = -999
        elif temp_qty > 0: average_purchase_price_mv = temp_amt/temp_qty
        pension_asset.update(average_purchase_price_mv=average_purchase_price_mv)

        # average_purchase_price_fifo
        transaction_amount_list = []
        temp_qty = 0
        temp_amt = 0
        for transaction_data in transaction_data_set:
            if transaction_data['transaction_type'] == 'BUY':
                for i in range(int(transaction_data['quantity'])):
                    transaction_amount_list.append(transaction_data['price'])
            elif transaction_data['transaction_type'] == 'SELL':
                for i in range(int(transaction_data['quantity'])):
                    transaction_amount_list.pop(0)

        for transaction_amount in transaction_amount_list:
            temp_qty += 1
            temp_amt += transaction_amount

        if temp_qty > 0: average_purchase_price_fifo = temp_amt/temp_qty
        else: average_purchase_price_fifo = 0
        pension_asset.update(average_purchase_price_fifo=average_purchase_price_fifo)

        return {
            'quantity': final_quantity,
            'total_amount': final_quantity*current_price,
            'average_purchase_price_mv': average_purchase_price_mv,
            'average_purchase_price_fifo': average_purchase_price_fifo,
        }

    def update_rate_of_returns(self):
        pension_asset = PensionAsset.objects.filter(pk=self.pk)

        rate_of_return_mv = 0
        if self.average_purchase_price_mv > 0:
            rate_of_return_mv = (self.asset.current_price - self.average_purchase_price_mv)/self.average_purchase_price_mv
        pension_asset.update(rate_of_return_mv=rate_of_return_mv)

        rate_of_return_fifo = 0
        if self.average_purchase_price_fifo > 0:
            rate_of_return_fifo = (self.asset.current_price - self.average_purchase_price_fifo)/self.average_purchase_price_fifo
        pension_asset.update(rate_of_return_fifo=rate_of_return_fifo)

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


class PensionAssetTransaction(models.Model):
    from django import utils
    pension_asset = models.ForeignKey(PensionAsset, on_delete=models.CASCADE, related_name='transaction', null=False)

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