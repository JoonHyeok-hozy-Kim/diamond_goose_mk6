# Generated by Django 4.0 on 2022-01-12 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hozylabapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='temptransaction',
            name='applied_flag',
            field=models.BooleanField(default=False),
        ),
    ]
