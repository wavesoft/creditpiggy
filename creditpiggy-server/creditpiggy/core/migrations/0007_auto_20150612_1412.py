# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_piggyuser_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectuserrole',
            name='firstAction',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='projectuserrole',
            name='lastAction',
            field=models.IntegerField(default=0),
        ),
    ]
