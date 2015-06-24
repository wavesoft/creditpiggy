# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20150624_1904'),
    ]

    operations = [
        migrations.RenameField(
            model_name='piggyproject',
            old_name='urlid',
            new_name='slug',
        ),
        migrations.RenameField(
            model_name='website',
            old_name='urlid',
            new_name='slug',
        ),
    ]
