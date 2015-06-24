# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20150624_1507'),
    ]

    operations = [
        migrations.AddField(
            model_name='visualmetric',
            name='sum_method',
            field=models.IntegerField(default=1, choices=[(0, b'Pick First'), (1, b'Add'), (1, b'Average'), (2, b'Minimum'), (3, b'Maximum')]),
        ),
    ]
