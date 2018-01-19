# Generated by Django 2.0.1 on 2018-01-19 14:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('slots', '0018_slot_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=25)),
                ('payload', models.PositiveSmallIntegerField(choices=[(1, '1 t'), (2, '2 t'), (3, '3 t'), (4, '4 t'), (5, '5 t'), (6, '6 t'), (7, '7 t'), (8, '8 t'), (9, '9 t'), (10, '10 t'), (11, '11 t'), (12, '12 t'), (13, '13 t'), (14, '14 t'), (15, '15 t'), (16, '16 t'), (17, '17 t'), (18, '18 t'), (19, '19 t'), (20, '20 t'), (21, '21 t'), (22, '22 t'), (23, '23 t'), (24, '24 t'), (25, '25 t'), (26, '26 t'), (27, '27 t'), (28, '28 t'), (29, '29 t'), (30, '30 t'), (31, '31 t'), (32, '32 t'), (33, '33 t'), (34, '34 t'), (35, '35 t'), (36, '36 t'), (37, '37 t'), (38, '38 t'), (39, '39 t'), (40, '40 t')], default=25)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('slot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='slots.Slot')),
            ],
            options={
                'verbose_name_plural': 'Jobs',
                'verbose_name': 'Job',
            },
        ),
    ]