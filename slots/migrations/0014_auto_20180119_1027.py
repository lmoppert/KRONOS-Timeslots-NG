# Generated by Django 2.0.1 on 2018-01-19 10:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('slots', '0013_auto_20180118_1457'),
    ]

    operations = [
        migrations.RenameField(
            model_name='station',
            old_name='company',
            new_name='location',
        ),
    ]
