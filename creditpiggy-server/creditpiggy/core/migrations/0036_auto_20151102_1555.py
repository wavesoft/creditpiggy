# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_auto_20151029_1626'),
    ]

    operations = [
        migrations.AddField(
            model_name='piggyuser',
            name='email_achievement',
            field=models.BooleanField(default=True, help_text=b'Receive e-mail on achievement'),
        ),
        migrations.AddField(
            model_name='piggyuser',
            name='email_projects',
            field=models.BooleanField(default=True, help_text=b'Receive e-mails from project owners'),
        ),
        migrations.AddField(
            model_name='piggyuser',
            name='email_surveys',
            field=models.BooleanField(default=True, help_text=b'Receive e-mails for surveys'),
        ),
        migrations.AddField(
            model_name='piggyuser',
            name='priv_leaderboards',
            field=models.BooleanField(default=True, help_text=b'Show on leaderboards'),
        ),
    ]
