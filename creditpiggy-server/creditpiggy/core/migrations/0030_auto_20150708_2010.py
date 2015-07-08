# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_projectuserrole_norm_credits'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonalAchievement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('visited', models.DateTimeField(auto_now_add=True)),
                ('publisher', models.ForeignKey(related_name='user_publisher', to=settings.AUTH_USER_MODEL)),
                ('visitor', models.ForeignKey(related_name='user_visitor', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='achievement',
            name='personal',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='personalachievement',
            name='achievement',
            field=models.ForeignKey(to='core.Achievement'),
        ),
        migrations.AddField(
            model_name='personalachievement',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
