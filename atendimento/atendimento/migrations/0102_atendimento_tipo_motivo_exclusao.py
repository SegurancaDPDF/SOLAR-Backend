# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('atendimento', '0101_perm_view_all_tarefas'),
    ]

    operations = [
        migrations.CreateModel(
            name='MotivoExclusao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('nome', models.CharField(max_length=512, db_index=True)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='atendimento_motivoexclusao_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='atendimento_motivoexclusao_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='atendimento_motivoexclusao_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name': 'Motivo de Exclus\xe3o',
                'verbose_name_plural': 'Motivos de Exclus\xe3o',
            },
        ),
        migrations.AlterField(
            model_name='encaminhamento',
            name='endereco',
            field=models.ForeignKey(blank=True, to='contrib.Endereco', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AlterField(
            model_name='encaminhamento',
            name='telefone',
            field=models.ForeignKey(blank=True, to='contrib.Telefone', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='atendimento',
            name='tipo_motivo_exclusao',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, editable=False, to='atendimento.MotivoExclusao', null=True),
        ),
    ]
