# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import creditpiggy.core.metrics
import creditpiggy.core.models
import django.contrib.auth.models
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='PiggyUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, verbose_name='username')),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('display_name', models.CharField(default=b'', max_length=200)),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(creditpiggy.core.metrics.MetricsModelMixin, models.Model),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ComputingUnit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(default=b'', help_text=b'A unique ID generated from within the computing unit and delivered to CP through the batch system', unique=True, max_length=32, db_index=True)),
                ('owner', models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            bases=(creditpiggy.core.metrics.MetricsModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CreditSlot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(help_text=b'The globally unique slot ID as specified by the project owner', max_length=256, db_index=True)),
                ('expireTime', models.IntegerField(default=0)),
                ('credits', models.IntegerField(default=None, null=True)),
                ('minBound', models.IntegerField(default=None, null=True)),
                ('maxBound', models.IntegerField(default=None, null=True)),
                ('status', models.IntegerField(default=0, choices=[(0, b'Free'), (1, b'Claimed'), (2, b'Discarded')])),
                ('reason', models.CharField(default=None, max_length=32, null=True)),
            ],
            bases=(creditpiggy.core.metrics.MetricsModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PiggyProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(default=creditpiggy.core.models.new_uuid, help_text=b'A unique ID identifying the specified project', unique=True, max_length=32, db_index=True)),
                ('display_name', models.CharField(help_text=b"Project's full name", max_length=1024)),
                ('desc', models.TextField(help_text=b'Project description')),
                ('profileImage', models.CharField(help_text=b"Project's profile image", max_length=1024)),
            ],
            bases=(creditpiggy.core.metrics.MetricsModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ProjectCredentials',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(default=creditpiggy.core.models.new_uuid, help_text=b'Anonymous authentication token for the credentials', unique=True, max_length=32, db_index=True)),
                ('secret', models.CharField(default=creditpiggy.core.models.gen_token_key, help_text=b'Shared secret between project and administrator', max_length=48)),
                ('project', models.ForeignKey(to='core.PiggyProject')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectUserCredit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('credits', models.IntegerField(default=0)),
                ('project', models.ForeignKey(to='core.PiggyProject')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            bases=(creditpiggy.core.metrics.MetricsModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ProjectUserRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.IntegerField(default=3, choices=[(0, b'Owner'), (1, b'Administrator'), (2, b'Moderator'), (3, b'Member')])),
                ('project', models.ForeignKey(to='core.PiggyProject')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='creditslot',
            name='project',
            field=models.ForeignKey(to='core.PiggyProject'),
        ),
    ]
