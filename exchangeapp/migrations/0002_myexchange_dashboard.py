# Generated by Django 4.0 on 2022-01-07 17:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboardapp', '0001_initial'),
        ('exchangeapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='myexchange',
            name='dashboard',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='my_exchange', to='dashboardapp.dashboard'),
            preserve_default=False,
        ),
    ]
