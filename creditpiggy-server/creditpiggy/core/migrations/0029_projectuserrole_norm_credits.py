# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_userlinklogs'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectuserrole',
            name='norm_credits',
            field=models.FloatField(default=0.0),
        ),
    ]
