from django.contrib.auth.models import User
from django.db import models

# Create your models here.
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