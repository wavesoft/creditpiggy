# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150602_1908'),
    ]

    operations = [
        migrations.AddField(
            model_name='piggyproject',
            name='project_url',
            field=models.URLField(default=b''),
        ),
    ]
