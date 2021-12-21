# Generated by Django 4.0 on 2021-12-21 05:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='dashboard', serialize=False, to='auth.user')),
                ('creation_date', models.DateTimeField(auto_now=True)),
                ('last_update_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
