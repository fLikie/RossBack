# Generated by Django 3.1.3 on 2020-11-28 07:50

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20201128_1529'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='date_of_employment',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
