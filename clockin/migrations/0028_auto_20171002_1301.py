# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-02 17:01
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clockin', '0027_auto_20170928_1311'),
    ]

    operations = [
        migrations.AlterField(
            model_name='work',
            name='time_in',
            field=models.TimeField(blank=True, default=datetime.time(13, 1, 35, 105956), verbose_name='Time In'),
        ),
        migrations.AlterField(
            model_name='work',
            name='time_out',
            field=models.TimeField(blank=True, default=datetime.time(13, 1, 35, 105956), verbose_name='Time Out'),
        ),
    ]
