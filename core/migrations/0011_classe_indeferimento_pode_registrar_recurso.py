# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from core.models import Processo, Classe

def carregar_dados(apps, schema_editor):
    Classe.objects.filter(
        tipo_processo=Processo.TIPO_INDEFERIMENTO
    ).update(
        indeferimento_pode_registrar_recurso=Classe.INDEFERIMENTO_REGISTRAR_RECURSO_NO_INICIO
    )

def reverse_carregar_dados(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_tipoevento_atividade_brinquedoteca'),
    ]

    operations = [
        migrations.AddField(
            model_name='classe',
            name='indeferimento_pode_registrar_recurso',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Indeferimento: Pode registrar recurso?', choices=[(0, 'N\xe3o pode registrar recurso'), (10, 'O recurso deve ser registrado no in\xedcio da movimenta\xe7\xe3o do processo (status inicial: Peticionamento)'), (20, 'O recurso pode ser registrado a qualquer momento da movimenta\xe7\xe3o do processo (status inicial: Movimento)')]),
        ),
        migrations.RunPython(
            code=carregar_dados,
            reverse_code=reverse_carregar_dados,
        ),
    ]
