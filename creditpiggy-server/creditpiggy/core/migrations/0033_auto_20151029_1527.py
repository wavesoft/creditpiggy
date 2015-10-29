# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_auto_20151029_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaignusercredit',
            name='achievements',
            field=models.ManyToManyField(to='core.Achievement', blank=True),
        ),
    ]
