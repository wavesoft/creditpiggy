# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_auto_20150708_2010'),
    ]

    operations = [
        migrations.AddField(
            model_name='visualmetric',
            name='decimals',
            field=models.FloatField(default=0, help_text=b'Number of decimals when rounding the value before presenting it'),
        ),
        migrations.AddField(
            model_name='visualmetric',
            name='scale',
            field=models.FloatField(default=1.0, help_text=b'Scale of the metrics value when presenting it'),
        ),
    ]
