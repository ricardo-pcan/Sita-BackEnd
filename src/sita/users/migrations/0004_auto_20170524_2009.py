# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-05-24 20:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20170524_1602'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='conekta_card',
            new_name='conekta_customer',
        ),
    ]
