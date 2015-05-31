# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_projectusercredits'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectusercredits',
            name='claimed',
            field=models.BooleanField(default=False),
        ),
    ]
