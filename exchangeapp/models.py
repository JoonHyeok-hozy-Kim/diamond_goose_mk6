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