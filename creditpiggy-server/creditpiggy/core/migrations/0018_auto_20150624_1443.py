# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20150624_1257'),
    ]

    operations = [
        migrations.AddField(
            model_name='website',
            name='header_background',
            field=models.CharField(default=b'#660099', max_length=24),
        ),
        migrations.AddField(
            model_name='website',
            name='header_foreground',
            field=models.CharField(default=b'#fff', max_length=24),
        ),
        migrations.AddField(
            model_name='website',
            name='header_image',
            field=models.CharField(default=b'', max_length=200),
        ),
        migrations.AlterField(
            model_name='piggyproject',
            name='urlid',
            field=models.CharField(default=b'', help_text=b'An indexing keyword, useful for human-readable URLs', max_length=200, editable=False, db_index=True),
        ),
        migrations.AlterField(
            model_name='website',
            name='urlid',
            field=models.CharField(default=b'', help_text=b'An indexing keyword, useful for human-readable URLs', max_length=200, editable=False, db_index=True),
        ),
    ]
