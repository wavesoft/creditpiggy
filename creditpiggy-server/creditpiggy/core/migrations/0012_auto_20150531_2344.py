# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20150531_2332'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='creditslot',
            name='claimed',
        ),
        migrations.AddField(
            model_name='creditslot',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, b'Free'), (1, b'Claimed'), (2, b'Discarded')]),
        ),
    ]
