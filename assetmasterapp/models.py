import requests
import json

from django.db import models
import yfinance as yf

# Create your models here.

ASSET_TYPES = (
    ('EQUITY', 'Equity'),
    ('GUARDIAN', 'Guardian'),
    ('REITS', 'Reits'),
    ('PENSION', 'Pension'),
    ('CRYPTO', 'Crypto Asset'),
)

MARKET_CHOICES = (
    ('KSE', 'Korean Stock Exchange(KSE)'),
    ('NASDAQ', 'NASDAQ'),
    ('NYSE', 'NewYork Stock Exchange(NYSE)'),
    ('NA', 'Not Applicable')
)

CURRENCY_CHOICES = (
    ('KRW', 'KRW(￦)'),
    ('USD', 'USD($)'),
)

class Asset(models.Model):
    asset_type = models.CharField(max_length=100, choices=ASSET_TYPES, null=False)
    market = models.CharField(max_length=100, choices=MARKET_CHOICES, null=False)
    ticker = models.CharField(max_length=20, null=False)
    name = models.CharField(max_length=200, null=True)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, null=False)
    image = models.ImageField(upload_to='assetmaster/', null=True)

    current_price = models.FloatField(default=0, null=False)

    pension_non_risk_asset_flag = models.BooleanField(default=False, null=False)

    def update_current_price(self):
        yfinance_markets = ['NASDAQ', 'NYSE', 'KSE']
        result_current_price = 0

        if self.market in yfinance_markets:
            ticker = self.ticker

            if self.market == 'KSE': ticker += '.KS'

            try:
                ticker_data = yf.Ticker(ticker)
                today_ticker_data = ticker_data.history(period='1d')

                if self.market == 'KSE':
                    result_current_price = round(today_ticker_data['Close'][0])
                else:
                    result_current_price = round(today_ticker_data['Close'][0], 2)
            except Exception as identifier:
                print('[Exception] Asset Model, update_current_price : ', identifier)

        else:
            if self.asset_type == 'CRYPTO':

                url_list = ['https://api.upbit.com/v1/candles/minutes/1?market=']
                url_list.append(self.currency)
                url_list.append('-')
                url_list.append(self.ticker)
                url_list.append('&count=1')

                url = ''.join(url_list)
                headers = {"Accept": "application/json"}
                response = requests.request("GET", url, headers=headers)
                dict_result = json.loads(response.text[1:-1])

                result_current_price = round(float(dict_result['opening_price']),2)

        asset = Asset.objects.filter(pk=self.pk)
        asset.update(current_price=result_current_price)

        return result_current_price


