# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-21 16:37
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clockin', '0034_auto_20171121_1136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='work',
            name='time_in',
            field=models.TimeField(blank=True, default=datetime.time(11, 37, 25, 955202), verbose_name='Time In'),
        ),
        migrations.AlterField(
            model_name='work',
            name='time_out',
            field=models.TimeField(blank=True, default=datetime.time(11, 37, 25, 955228), verbose_name='Time Out'),
        ),
    ]
