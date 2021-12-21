from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Dashboard(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='dashboard')

    creation_date = models.DateTimeField(auto_now=True)
    last_update_date = models.DateTimeField(auto_now_add=True)