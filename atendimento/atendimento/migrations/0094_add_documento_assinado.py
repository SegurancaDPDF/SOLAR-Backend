# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import atendimento.atendimento.models
import cuser.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('atendimento', '0093_atendimento_representante'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentoAssinado',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('arquivo', models.FileField(upload_to=atendimento.atendimento.models.documento_file_name, verbose_name='Arquivo')),
                ('data_enviado', models.DateTimeField(auto_now_add=True, verbose_name='Data de Envio', null=True)),
                ('atendimento', models.ForeignKey(blank=True, to='atendimento.Atendimento', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='atendimento_documentoassinado_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='atendimento_documentoassinado_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='atendimento_documentoassinado_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='documento',
            name='documento_assinado',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='atendimento.DocumentoAssinado', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
