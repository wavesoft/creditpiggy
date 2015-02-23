# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import frontend.models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0002_auto_20150211_1219'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectrevision',
            name='uuid',
            field=models.CharField(default=frontend.models.project_uuid, help_text=b'A unique key for this project version', unique=True, max_length=32, db_index=True),
            preserve_default=True,
        ),
    ]
