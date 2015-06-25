# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20150625_0243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='computingunit',
            name='uuid',
            field=models.CharField(default=b'', help_text=b'A unique ID generated from within the computing unit and delivered to CP through the batch system', unique=True, max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='creditslot',
            name='uuid',
            field=models.CharField(help_text=b'The globally unique slot ID as specified by the project owner', max_length=255, db_index=True),
        ),
    ]
