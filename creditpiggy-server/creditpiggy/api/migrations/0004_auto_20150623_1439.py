# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_websitecredentials_website'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='singleauthlogintoken',
            name='user',
        ),
        migrations.DeleteModel(
            name='SingleAuthLoginToken',
        ),
    ]
