# Generated by Django 4.0 on 2021-12-23 10:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pensionapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pensionasset',
            name='pension',
        ),
    ]
