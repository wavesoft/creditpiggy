# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20150625_0155'),
    ]

    operations = [
        migrations.AddField(
            model_name='computingunit',
            name='firstAction',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 24, 23, 43, 21, 776095, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='computingunit',
            name='lastAction',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 24, 23, 43, 25, 272122, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
