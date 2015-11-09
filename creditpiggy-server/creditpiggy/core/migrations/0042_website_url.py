# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0041_auto_20151107_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='website',
            name='url',
            field=models.CharField(default=b'', help_text=b'The website URL', max_length=200, blank=True),
        ),
    ]
