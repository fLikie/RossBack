# Generated by Django 3.1.3 on 2020-11-28 08:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_userprofile_date_of_employment'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Status',
            new_name='State',
        ),
        migrations.RenameField(
            model_name='forum',
            old_name='status',
            new_name='state',
        ),
    ]
