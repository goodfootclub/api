# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-19 16:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0007_auto_20170129_1745'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rsvpstatus',
            options={'ordering': ['game__datetime'], 'verbose_name': 'RSVP status', 'verbose_name_plural': 'RSVP statuses'},
        ),
    ]