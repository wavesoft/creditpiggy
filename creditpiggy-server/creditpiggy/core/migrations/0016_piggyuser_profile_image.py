# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_website_short'),
    ]

    operations = [
        migrations.AddField(
            model_name='piggyuser',
            name='profile_image',
            field=models.CharField(default=b'/static/lib/img/anonymous.png', help_text=b"User's profile image", max_length=1024),
        ),
    ]
