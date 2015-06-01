# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150530_0029'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditslot',
            name='expireTime',
            field=models.IntegerField(default=0),
        ),
    ]
