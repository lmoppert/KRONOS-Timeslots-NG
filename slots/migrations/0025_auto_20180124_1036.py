# Generated by Django 2.0.1 on 2018-01-24 10:36

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('slots', '0024_auto_20180123_1609'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='slot',
            managers=[
                ('drafts', django.db.models.manager.Manager()),
            ],
        ),
    ]
