from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from dashboardapp.models import Dashboard
from exchangeapp.models import MyExchange, ForeignCurrency


class Portfolio(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolio')
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='portfolio')

    current_value = models.FloatField(default=0, null=False)

    capital_gain = models.FloatField(default=0, null=False)
    rate_of_return = models.FloatField(default=0, null=False)

    capital_gain_foreign_exchange_adjusted = models.FloatField(default=0, null=False)
    rate_of_return_foreign_exchange_adjusted = models.FloatField(default=0, null=False)

    creation_date = models.DateTimeField(auto_now=True)
    last_update_date = models.DateTimeField(auto_now_add=True)

    def asset_current_value_exchanger(self, asset_instance, my_main_currency, foreign_currencies):
        asset_instance.asset.update_current_price()
        result = 0
        if asset_instance.asset.currency == my_main_currency:
            result += asset_instance.total_amount
        else:
            for foreign_currency in foreign_currencies:
                if asset_instance.asset.currency == foreign_currency.currency:
                    result += asset_instance.total_amount * foreign_currency.current_exchange_rate
        return result

    def asset_purchase_value_exchanger(self, asset_instance, my_main_currency, foreign_currencies, my_rate_flag=None):
        result = 0
        purchase_amount = asset_instance.quantity * asset_instance.average_purchase_price_mv
        if asset_instance.asset.currency == my_main_currency:
            result += purchase_amount
        else:
            for foreign_currency in foreign_currencies:
                if asset_instance.asset.currency == foreign_currency.currency:
                    if my_rate_flag:
                        result += purchase_amount * foreign_currency.accumulated_exchange_rate_mv
                    else:
                        result += purchase_amount * foreign_currency.current_exchange_rate
        return result

    def update_current_value(self):
        current_value = 0
        purchase_value = 0
        purchase_value_exchange_adjusted = 0
        asset_type_count_list = []

        queryset_my_exchange = MyExchange.objects.get(dashboard=self.dashboard.pk)
        my_main_currency = queryset_my_exchange.main_currency
        queryset_foreign_currencies = ForeignCurrency.objects.filter(exchange=queryset_my_exchange.pk)

        from equityapp.models import Equity
        queryset_equities = Equity.objects.filter(portfolio=self.pk)
        asset_type = None
        asset_count = 0
        for equity in queryset_equities:
            current_value += self.asset_current_value_exchanger(equity, my_main_currency, queryset_foreign_currencies)
            purchase_value += self.asset_purchase_value_exchanger(equity, my_main_currency, queryset_foreign_currencies)
            purchase_value_exchange_adjusted += self.asset_purchase_value_exchanger(equity, my_main_currency, queryset_foreign_currencies, 'Y')
            asset_type = equity.asset.asset_type
            asset_count += 1
        asset_type_count_list.append({'asset_type': asset_type, 'asset_count': asset_count})

        from cryptoapp.models import Crypto
        queryset_cryptoes = Crypto.objects.filter(portfolio=self.pk)
        asset_type = None
        asset_count = 0
        for crypto in queryset_cryptoes:
            current_value += self.asset_current_value_exchanger(crypto, my_main_currency, queryset_foreign_currencies)
            purchase_value += self.asset_purchase_value_exchanger(crypto, my_main_currency, queryset_foreign_currencies)
            purchase_value_exchange_adjusted += self.asset_purchase_value_exchanger(crypto, my_main_currency, queryset_foreign_currencies, 'Y')
            asset_type = crypto.asset.asset_type
            asset_count += 1
        asset_type_count_list.append({'asset_type': asset_type, 'asset_count': asset_count})

        from reitsapp.models import Reits
        queryset_reits = Reits.objects.filter(portfolio=self.pk)
        asset_type = None
        asset_count = 0
        for reits in queryset_reits:
            current_value += self.asset_current_value_exchanger(reits, my_main_currency, queryset_foreign_currencies)
            purchase_value += self.asset_purchase_value_exchanger(reits, my_main_currency, queryset_foreign_currencies)
            purchase_value_exchange_adjusted += self.asset_purchase_value_exchanger(reits, my_main_currency, queryset_foreign_currencies, 'Y')
            asset_type = reits.asset.asset_type
            asset_count += 1
        asset_type_count_list.append({'asset_type': asset_type, 'asset_count': asset_count})

        from guardianapp.models import Guardian
        queryset_guardians = Guardian.objects.filter(portfolio=self.pk)
        asset_type = None
        asset_count = 0
        for guardian in queryset_guardians:
            current_value += self.asset_current_value_exchanger(guardian, my_main_currency, queryset_foreign_currencies)
            purchase_value += self.asset_purchase_value_exchanger(guardian, my_main_currency, queryset_foreign_currencies)
            purchase_value_exchange_adjusted += self.asset_purchase_value_exchanger(guardian, my_main_currency, queryset_foreign_currencies, 'Y')
            asset_type = guardian.asset.asset_type
            asset_count += 1
        asset_type_count_list.append({'asset_type': asset_type, 'asset_count': asset_count})

        from pensionapp.models import PensionAsset
        queryset_pension_assets = PensionAsset.objects.filter(owner=self.owner.pk)
        asset_type = None
        asset_count = 0
        for pension_asset in queryset_pension_assets:
            current_value += self.asset_current_value_exchanger(pension_asset, my_main_currency, queryset_foreign_currencies)
            purchase_value += self.asset_purchase_value_exchanger(pension_asset, my_main_currency, queryset_foreign_currencies)
            purchase_value_exchange_adjusted += self.asset_purchase_value_exchanger(pension_asset, my_main_currency, queryset_foreign_currencies, 'Y')
            asset_type = pension_asset.asset.asset_type
            asset_count += 1
        asset_type_count_list.append({'asset_type': asset_type, 'asset_count': asset_count})

        portfolio = Portfolio.objects.filter(pk=self.pk)
        portfolio.update(current_value=current_value)

        if purchase_value > 0:
            capital_gain = current_value-purchase_value
            rate_of_return = capital_gain/purchase_value
            portfolio.update(capital_gain=capital_gain)
            portfolio.update(rate_of_return=rate_of_return)

            capital_gain_foreign_exchange_adjusted = current_value-purchase_value_exchange_adjusted
            rate_of_return_foreign_exchange_adjusted = capital_gain_foreign_exchange_adjusted/purchase_value_exchange_adjusted
            portfolio.update(capital_gain_foreign_exchange_adjusted=capital_gain_foreign_exchange_adjusted)
            portfolio.update(rate_of_return_foreign_exchange_adjusted=rate_of_return_foreign_exchange_adjusted)
        else:
            portfolio.update(capital_gain=0)
            portfolio.update(rate_of_return=0)
            portfolio.update(capital_gain_foreign_exchange_adjusted=0)
            portfolio.update(rate_of_return_foreign_exchange_adjusted=0)

        return asset_type_count_list
