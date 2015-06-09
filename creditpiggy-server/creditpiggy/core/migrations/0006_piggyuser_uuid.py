# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import creditpiggy.core.models

def generate_uuid(apps, schema_editor):
    PiggyUser = apps.get_model('core', 'PiggyUser')
    for user in PiggyUser.objects.all().iterator():
        user.uuid = creditpiggy.core.models.new_uuid()
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20150607_0838'),
    ]

    operations = [
        migrations.AddField(
            model_name='piggyuser',
            name='uuid',
            field=models.CharField(default=creditpiggy.core.models.new_uuid, help_text=b'Unique user identification string', max_length=32),
            preserve_default=False,
        ),
        migrations.RunPython(
            generate_uuid,
        ),
        migrations.AlterField(
            model_name='piggyuser',
            name='uuid',
            field=models.CharField(default=creditpiggy.core.models.new_uuid, help_text=b'Unique user identification string', unique=True, max_length=32, db_index=True),
            preserve_default=True,
        ),
    ]
