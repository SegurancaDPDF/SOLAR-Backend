# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from assistido.models import PerfilCamposObrigatorios

import cuser.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def altera_perfil_campos_obrigatorios(apps, schema_editor):

    for perfil in PerfilCamposObrigatorios.objects.all():

        configuracao = perfil.configuracao_to_json()

        if 'RendaForm' in configuracao:
            configuracao['RendaForm']['tipo_renda'] = False

        perfil.configuracao = json.dumps(configuracao)
        perfil.save()

def reverse_altera_perfil_campos_obrigatorios(apps, schema_editor):

    for perfil in PerfilCamposObrigatorios.objects.all():

        configuracao = perfil.configuracao_to_json()

        if 'RendaForm' in configuracao:
            configuracao['RendaForm'].pop('tipo_renda', None)

        perfil.configuracao = json.dumps(configuracao)
        perfil.save()
        
class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assistido', '0054_add_situacao_dependente'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoRenda',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(blank=True, null=True)),
                ('nome', models.CharField(max_length=256)),
                ('eh_deducao_salario_minimo', models.BooleanField(default=False, help_text='Caso marcado, deve-se deixar em branco o valor máximo de dedução abaixo e será utilizado o valor da tabela salários', verbose_name='Deve ser realizada dedução máxima de 1 salário mínimo?')),
                ('valor_maximo_deducao', models.DecimalField(decimal_places=2, default=0, help_text='Valor máximo em R$ que será deduzido para este tipo de renda (caso não seja o salário mínimo)', max_digits=16, verbose_name='Valor máximo de dedução')),
                ('cadastrado_por', cuser.fields.CurrentUserField(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assistido_tiporenda_cadastrado_por', to=settings.AUTH_USER_MODEL)),
                ('desativado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assistido_tiporenda_desativado_por', to=settings.AUTH_USER_MODEL)),
                ('modificado_por', cuser.fields.CurrentUserField(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assistido_tiporenda_modificado_por', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Tipo de Renda',
                'verbose_name_plural': 'Tipos de renda',
                'ordering': ['nome'],
            },
        ),
        migrations.AddField(
            model_name='dependente',
            name='tipo_renda',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='tipos_renda', to='assistido.tiporenda'),
        ),
        migrations.AddField(
            model_name='renda',
            name='tipo_renda',
            field=models.ForeignKey(blank=True, default=None, help_text='Tipo da renda individual do assistido', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='tipos', to='assistido.tiporenda', verbose_name='Tipo de renda'),
        ),
        migrations.RunPython(
            code=altera_perfil_campos_obrigatorios,
            reverse_code=reverse_altera_perfil_campos_obrigatorios,
        )
    ]