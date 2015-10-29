# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_auto_20151029_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='public',
            field=models.BooleanField(default=False),
        ),
    ]
