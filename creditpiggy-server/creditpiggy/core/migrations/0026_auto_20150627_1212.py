# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import creditpiggy.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_creditslot_machine'),
    ]

    operations = [
        migrations.AddField(
            model_name='computingunit',
            name='website',
            field=models.ForeignKey(default=None, to='core.Website', null=True),
        ),
        migrations.AlterField(
            model_name='creditslot',
            name='expireTime',
            field=models.IntegerField(default=creditpiggy.core.models.new_expire_time),
        ),
    ]
