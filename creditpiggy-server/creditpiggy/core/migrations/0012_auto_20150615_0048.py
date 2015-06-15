# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20150612_2026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='piggyproject',
            name='achievements',
            field=models.ManyToManyField(to='core.Achievement', blank=True),
        ),
    ]
