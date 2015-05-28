# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import creditpiggy.api.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AuthToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('auth_key', models.CharField(default=creditpiggy.api.models.gen_token_key, help_text=b'A unique ID used by server-side software to identify the user', max_length=64, db_index=True)),
                ('auth_salt', models.CharField(default=creditpiggy.api.models.gen_token_salt, help_text=b'The salt for authenticaton checksum token', max_length=64)),
                ('auth_hash', models.CharField(help_text=b"A validation checksum hash for the secret key in the user's computer", max_length=256, verbose_name=b'Secret')),
                ('tokenType', models.CharField(default=b'US', max_length=2, choices=[(b'US', b'User'), (b'DE', b'Devleoper'), (b'SV', b'Service')])),
            ],
        ),
        migrations.CreateModel(
            name='CreditCache',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('credit', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CreditSlot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectAuthToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tokenType', models.CharField(default=b'US', max_length=2, choices=[(b'US', b'User'), (b'DE', b'Devleoper'), (b'SV', b'Service')])),
            ],
        ),
    ]
