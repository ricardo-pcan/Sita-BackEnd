# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-05-24 15:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='time_zone',
            field=models.IntegerField(default=0),
        ),
    ]
