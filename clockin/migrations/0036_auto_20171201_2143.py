# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-02 02:43
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clockin', '0035_auto_20171127_1506'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='work',
            name='image',
        ),
        migrations.AlterField(
            model_name='work',
            name='time_in',
            field=models.TimeField(blank=True, default=datetime.time(21, 43, 33, 617591), verbose_name='Time In'),
        ),
        migrations.AlterField(
            model_name='work',
            name='time_out',
            field=models.TimeField(blank=True, default=datetime.time(21, 43, 33, 617591), verbose_name='Time Out'),
        ),
    ]
