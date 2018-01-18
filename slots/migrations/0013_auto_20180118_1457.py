# Generated by Django 2.0.1 on 2018-01-18 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slots', '0012_auto_20180118_1102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dock',
            name='linecount',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='dock',
            name='max_slots',
            field=models.PositiveIntegerField(default=0, help_text='0 for unlimited'),
        ),
        migrations.AlterField(
            model_name='role',
            name='role',
            field=models.PositiveIntegerField(choices=[(1, 'carrier'), (2, 'viewer'), (3, 'charger'), (4, 'loadmaster')], default=2),
        ),
    ]
