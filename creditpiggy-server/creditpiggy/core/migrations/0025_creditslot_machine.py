# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_auto_20150625_1934'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditslot',
            name='machine',
            field=models.ForeignKey(default=None, blank=True, to='core.ComputingUnit', null=True),
        ),
    ]
