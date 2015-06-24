# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_piggyuser_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='piggyproject',
            name='urlid',
            field=models.CharField(default=b'', help_text=b'An indexing keyword, useful for human-readable URLs', max_length=200, db_index=True),
        ),
        migrations.AddField(
            model_name='website',
            name='urlid',
            field=models.CharField(default=b'', help_text=b'An indexing keyword, useful for human-readable URLs', max_length=200, db_index=True),
        ),
        migrations.AlterField(
            model_name='piggyuser',
            name='profile_image',
            field=models.CharField(default=b'', help_text=b"User's profile image", max_length=1024),
        ),
    ]
