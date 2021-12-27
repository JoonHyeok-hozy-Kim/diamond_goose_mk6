# Generated by Django 4.0 on 2021-12-20 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_type', models.CharField(choices=[('EQUITY', 'Equity'), ('GUARDIAN', 'Guardian'), ('REITS', 'Reits'), ('PENSION', 'Pension'), ('CRYPTO', 'Crypto Asset')], max_length=100)),
                ('market', models.CharField(choices=[('KSE', 'Korean Stock Exchange(KSE)'), ('NASDAQ', 'NASDAQ'), ('NYSE', 'NewYork Stock Exchange(NYSE)'), ('NA', 'Not Applicable')], max_length=100)),
                ('ticker', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=200, null=True)),
                ('currency', models.CharField(choices=[('KRW', 'KRW(￦)'), ('USD', 'USD($)')], max_length=10)),
                ('image', models.ImageField(null=True, upload_to='assetmaster/')),
                ('current_price', models.FloatField(default=0)),
            ],
        ),
    ]