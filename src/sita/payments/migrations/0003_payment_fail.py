# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-05-26 22:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_payment_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='fail',
            field=models.BooleanField(default=False),
        ),
    ]
