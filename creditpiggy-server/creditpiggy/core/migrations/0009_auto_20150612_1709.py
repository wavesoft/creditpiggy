# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20150612_1701'),
    ]

    operations = [
        migrations.AlterField(
            model_name='achievementinstance',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
