# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_auto_20150627_1212'),
    ]

    operations = [
        migrations.AddField(
            model_name='piggyproject',
            name='norm_factor',
            field=models.FloatField(default=1.0),
        ),
    ]
