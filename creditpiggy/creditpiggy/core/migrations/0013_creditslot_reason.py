# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20150531_2344'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditslot',
            name='reason',
            field=models.CharField(default=None, max_length=32, null=True),
        ),
    ]
