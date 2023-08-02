# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assistido', '0013_auto_20171204_1700'),
    ]

    operations = [
        migrations.AddField(
            model_name='pessoa',
            name='cadastrado_em',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='pessoa',
            name='cadastrado_por',
            field=cuser.fields.CurrentUserField(related_name='assistido_pessoa_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='pessoa',
            name='desativado_em',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='pessoa',
            name='desativado_por',
            field=models.ForeignKey(related_name='assistido_pessoa_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='pessoa',
            name='modificado_em',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='pessoa',
            name='modificado_por',
            field=cuser.fields.CurrentUserField(related_name='assistido_pessoa_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
