# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_visualmetric_sum_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='visualmetric',
            name='priority',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='visualmetric',
            name='sum_method',
            field=models.IntegerField(default=1, choices=[(0, b'Pick First'), (1, b'Add'), (2, b'Average'), (3, b'Minimum'), (4, b'Maximum')]),
        ),
    ]
