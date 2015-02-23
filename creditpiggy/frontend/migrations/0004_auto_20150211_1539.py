# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import frontend.models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0003_projectrevision_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectrevision',
            name='uuid',
            field=models.CharField(default=frontend.models.project_uuid, editable=False, max_length=32, help_text=b'A unique key for this project version', unique=True, db_index=True),
        ),
    ]
