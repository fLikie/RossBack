# Generated by Django 3.1.3 on 2020-11-27 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_favorite_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='status',
            name='service',
            field=models.BooleanField(default=False),
        ),
    ]
