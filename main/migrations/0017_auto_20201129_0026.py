# Generated by Django 3.1.3 on 2020-11-28 15:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_auto_20201129_0005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favorite',
            name='forum',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='main.forum'),
        ),
    ]
