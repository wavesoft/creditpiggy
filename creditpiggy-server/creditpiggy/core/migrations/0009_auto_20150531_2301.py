# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20150531_2301'),
    ]

    operations = [
        migrations.RenameField(
            model_name='creditslot',
            old_name='claimed',
            new_name='claimedBy',
        ),
    ]
