# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20150531_2301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditslot',
            name='claimedBy',
            field=models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
