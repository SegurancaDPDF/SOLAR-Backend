# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('processo', '0036_processo_calculo_judicial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManifestacaoAviso',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('numero', models.CharField(default=None, max_length=100, null=True, help_text='N\xfamero do Aviso no Tribunal de Justi\xe7a', blank=True)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='processo_manifestacaoaviso_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='processo_manifestacaoaviso_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('manifestacao', models.ForeignKey(related_name='avisos', to='processo.Manifestacao', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='processo_manifestacaoaviso_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Aviso de Manifesta\xe7\xe3o',
                'verbose_name_plural': 'Avisos de Manifesta\xe7\xf5es',
            },
        ),
    ]
