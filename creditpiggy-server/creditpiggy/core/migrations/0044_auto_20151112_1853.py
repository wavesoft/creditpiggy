# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0043_manualemail'),
    ]

    operations = [
        migrations.AddField(
            model_name='manualemail',
            name='sent_emails',
            field=models.TextField(default=b'', help_text=b'The people already received this e-mail'),
        ),
        migrations.AddField(
            model_name='manualemail',
            name='target_filter',
            field=models.IntegerField(default=1, choices=[(0, b'Achievement'), (1, b'Project Update'), (2, b'Feedback Questions'), (3, b'Administrator (Bypasses user options)')]),
        ),
    ]
