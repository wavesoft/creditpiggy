# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_campaign_public'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visualmetric',
            name='decimals',
            field=models.IntegerField(default=0, help_text=b'Number of decimals when rounding the value before presenting it'),
        ),
    ]
