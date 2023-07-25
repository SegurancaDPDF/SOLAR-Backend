# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from bulk_update.helper import bulk_update
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields

from contrib.models import Util

def migrate_data(apps, schema_editor):

    FaseTipo = apps.get_model("processo", "FaseTipo")
    User = apps.get_model("auth", "User")

    agora = datetime.now()
    usuario = User.objects.filter(is_superuser=True, is_active=True, is_staff=True).order_by('date_joined').first()

    FaseTipo.objects.filter(
        ativo=False,
        desativado_em__isnull=True
    ).update(
        desativado_por=usuario,
        desativado_em=agora
    )

    tipos_fase = FaseTipo.objects.all()
    for tipo in tipos_fase:
        tipo.nome_norm = Util.normalize(tipo.nome)
    
    if len(tipos_fase):
        bulk_update(tipos_fase, update_fields=['nome_norm'], batch_size=1000)

def reverse_migrate_data(apps, schema_editor):

    FaseTipo = apps.get_model("processo", "FaseTipo")

    FaseTipo.objects.filter(
        desativado_em__isnull=False
    ).update(
        ativo=False
    )


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('processo', '0041_processo_valor_causa_default_0'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='processo',
            options={'ordering': ['numero_puro', '-ativo', 'id'], 'permissions': (('view_distribuicao', 'Pode ver Painel de Distribui\xe7\xe3o de Processos'),)},
        ),
        migrations.AddField(
            model_name='manifestacao',
            name='fase',
            field=models.OneToOneField(null=True, default=None, blank=True, to='processo.Fase', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AlterModelOptions(
            name='fasetipo',
            options={'ordering': ['-desativado_em', 'nome'], 'verbose_name': 'Tipo de Fase do Processo', 'verbose_name_plural': 'Tipos de Fases dos Processos'},
        ),
        migrations.AddField(
            model_name='fasetipo',
            name='cadastrado_em',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='fasetipo',
            name='cadastrado_por',
            field=cuser.fields.CurrentUserField(related_name='processo_fasetipo_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='fasetipo',
            name='desativado_em',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='fasetipo',
            name='desativado_por',
            field=models.ForeignKey(related_name='processo_fasetipo_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='fasetipo',
            name='modificado_em',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='fasetipo',
            name='modificado_por',
            field=cuser.fields.CurrentUserField(related_name='processo_fasetipo_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='fasetipo',
            name='nome_norm',
            field=models.CharField(default=None, max_length=512, null=True, blank=True),
        ),
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
        migrations.RemoveField(
            model_name='fasetipo',
            name='ativo',
        ),
    ]
