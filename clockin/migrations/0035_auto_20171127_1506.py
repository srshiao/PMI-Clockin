# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-27 20:06
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clockin', '0034_auto_20171127_1242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='work',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='work',
            name='time_in',
            field=models.TimeField(blank=True, default=datetime.time(15, 6, 26, 332482), verbose_name='Time In'),
        ),
        migrations.AlterField(
            model_name='work',
            name='time_out',
            field=models.TimeField(blank=True, default=datetime.time(15, 6, 26, 332482), verbose_name='Time Out'),
        ),
    ]
