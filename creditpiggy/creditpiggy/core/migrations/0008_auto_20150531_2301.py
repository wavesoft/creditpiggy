# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20150531_2129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditslot',
            name='claimed',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
