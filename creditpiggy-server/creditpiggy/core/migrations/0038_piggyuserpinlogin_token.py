# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import creditpiggy.core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_piggyuserpinlogin'),
    ]

    operations = [
        migrations.AddField(
            model_name='piggyuserpinlogin',
            name='token',
            field=models.CharField(default=creditpiggy.core.models.gen_token_key, max_length=48),
        ),
    ]
