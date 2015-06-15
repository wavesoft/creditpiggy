# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20150612_1412'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectusercredit',
            name='project',
        ),
        migrations.RemoveField(
            model_name='projectusercredit',
            name='user',
        ),
        migrations.AddField(
            model_name='projectuserrole',
            name='credits',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='projectuserrole',
            name='firstAction',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='projectuserrole',
            name='lastAction',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.DeleteModel(
            name='ProjectUserCredit',
        ),
    ]
