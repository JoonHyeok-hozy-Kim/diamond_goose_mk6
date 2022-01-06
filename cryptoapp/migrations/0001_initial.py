# Generated by Django 4.0 on 2022-01-06 15:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('portfolioapp', '0001_initial'),
        ('assetmasterapp', '0002_asset_pension_non_risk_asset_flag'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Crypto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField(default=0)),
                ('total_amount', models.FloatField(default=0)),
                ('average_purchase_price_mv', models.FloatField(default=0)),
                ('average_purchase_price_fifo', models.FloatField(default=0)),
                ('rate_of_return_mv', models.FloatField(default=0)),
                ('rate_of_return_fifo', models.FloatField(default=0)),
                ('creation_date', models.DateTimeField(auto_now=True)),
                ('last_update_date', models.DateTimeField(auto_now_add=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crypto', to='assetmasterapp.asset')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crypto', to='auth.user')),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crypto', to='portfolioapp.portfolio')),
            ],
        ),
    ]
