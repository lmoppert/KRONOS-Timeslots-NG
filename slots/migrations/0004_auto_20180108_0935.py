# Generated by Django 2.0.1 on 2018-01-08 09:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('slots', '0003_auto_20180108_0933'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dock',
            name='deadline',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='slots.Deadline'),
        ),
    ]
