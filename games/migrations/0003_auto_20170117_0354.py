# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-01-17 03:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0002_auto_20161207_1413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]