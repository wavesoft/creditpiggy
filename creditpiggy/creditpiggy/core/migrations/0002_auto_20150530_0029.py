# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditslot',
            name='uuid',
            field=models.CharField(help_text=b'The globally unique slot ID as specified by the project owner', max_length=256, db_index=True),
        ),
    ]
