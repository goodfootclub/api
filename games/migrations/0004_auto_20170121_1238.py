# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-01-21 12:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0003_auto_20170117_0354'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='game',
            options={'ordering': ['-datetime']},
        ),
    ]
