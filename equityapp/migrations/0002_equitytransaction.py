# Generated by Django 4.0 on 2021-12-21 11:46

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import equityapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('equityapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EquityTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('BUY', '매수'), ('SELL', '매도'), ('DIVIDEND', '배당금'), ('SPLIT', '액면분할')], max_length=20)),
                ('quantity', equityapp.models.MinValueFloat()),
                ('price', equityapp.models.MinValueFloat(default=0)),
                ('transaction_fee', models.FloatField(default=0)),
                ('transaction_tax', models.FloatField(default=0)),
                ('transaction_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('note', models.CharField(default=' - ', max_length=40, null=True)),
                ('split_cnt', models.IntegerField(default=0)),
                ('creation_date', models.DateTimeField(auto_now=True)),
                ('last_update_date', models.DateTimeField(auto_now_add=True)),
                ('equity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transaction', to='equityapp.equity')),
            ],
        ),
    ]
