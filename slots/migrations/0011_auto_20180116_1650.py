# Generated by Django 2.0.1 on 2018-01-16 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slots', '0010_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='role',
            field=models.PositiveIntegerField(choices=[(1, 'viewer'), (2, 'carrier'), (3, 'charger'), (4, 'loadmaster')], default=2),
        ),
    ]
