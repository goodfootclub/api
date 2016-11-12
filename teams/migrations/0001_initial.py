# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-12 11:35
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('CAP', 'Captain'), ('FLD', 'Field player'), ('SUB', 'Substitute')], default='FLD', max_length=3)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('managers', models.ManyToManyField(related_name='managed_teams', to=settings.AUTH_USER_MODEL)),
                ('players', models.ManyToManyField(related_name='teams', through='teams.Role', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='role',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teams.Team'),
        ),
        migrations.AlterUniqueTogether(
            name='role',
            unique_together=set([('player', 'team')]),
        ),
    ]
