# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20150616_1247'),
    ]

    operations = [
        migrations.AddField(
            model_name='website',
            name='short',
            field=models.CharField(default=b'', max_length=200),
        ),
    ]
