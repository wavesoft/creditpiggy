# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20150531_2128'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectusercredit',
            name='claimed',
        ),
        migrations.AddField(
            model_name='creditslot',
            name='claimed',
            field=models.BooleanField(default=False),
        ),
    ]
