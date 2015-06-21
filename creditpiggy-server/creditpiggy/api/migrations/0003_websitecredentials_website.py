# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20150616_1247'),
        ('api', '0002_projectcredentials_websitecredentials'),
    ]

    operations = [
        migrations.AddField(
            model_name='websitecredentials',
            name='website',
            field=models.ForeignKey(default=None, to='core.Website'),
            preserve_default=False,
        ),
    ]
