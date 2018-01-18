# Generated by Django 2.0.1 on 2018-01-18 11:02

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('slots', '0011_auto_20180116_1650'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='role',
            options={'verbose_name': 'Role', 'verbose_name_plural': 'Roles'},
        ),
        migrations.AlterUniqueTogether(
            name='role',
            unique_together={('user', 'station')},
        ),
    ]
