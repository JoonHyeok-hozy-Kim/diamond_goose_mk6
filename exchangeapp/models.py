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
