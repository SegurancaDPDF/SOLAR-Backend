# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
from django.db.models import F
import django.db.models.deletion
import jsonfield.fields
from core.models import TipoEvento as TipoEventoNovo

TIPO_PETICAO = 10 # TODO Modificado na migração para python3 para passar, apresenta sintaxe erro na forma antiga
TIPO_RECURSO = 11 # TODO Modificado na migração para python3 para passar, apresenta sintaxe erro na forma antiga
TIPO_ENCAMINHAMENTO = 12 # TODO Modificado na migração para python3 para passar, apresenta sintaxe erro na forma antiga
TIPO_RECEBIMENTO = 13 # TODO Modificado na migração para python3 para passar, apresenta sintaxe erro na forma antiga
TIPO_DECISAO = 14 # TODO Modificado na migração para python3 para passar, apresenta sintaxe erro na forma antiga
TIPO_BAIXA = 15 # TODO Modificado na migração para python3 para passar, apresenta sintaxe erro na forma antiga
TIPO_ANOTACAO = 20 # TODO Modificado na migração para python3 para passar, apresenta sintaxe erro na forma antiga

TIPOS = (
    (TIPO_PETICAO, TipoEventoNovo.TIPO_PETICAO),
    (TIPO_RECURSO, TipoEventoNovo.TIPO_RECURSO),
    (TIPO_ENCAMINHAMENTO, TipoEventoNovo.TIPO_ENCAMINHAMENTO),
    (TIPO_RECEBIMENTO, TipoEventoNovo.TIPO_RECEBIMENTO),
    (TIPO_DECISAO, TipoEventoNovo.TIPO_DECISAO),
    (TIPO_BAIXA, TipoEventoNovo.TIPO_BAIXA),
    (TIPO_ANOTACAO, TipoEventoNovo.TIPO_ANOTACAO),
)

def carregar_dados(apps, schema_editor):
    TipoEvento = apps.get_model('core', 'TipoEvento')
    print('\nMigrando core.TipoEvento...')

    for (velho, novo) in reversed(TIPOS):
        print('{} >>> {}'.format(velho, novo))
        TipoEvento.objects.filter(
            tipo=velho,
        ).update(
            tipo=novo
        )

def reverse_carregar_dados(apps, schema_editor):
    TipoEvento = apps.get_model('core', 'TipoEvento')
    print('\nRevertendo core.TipoEvento...')

    for (velho, novo) in TIPOS:
        print('{} >>> {}'.format(novo, velho))
        TipoEvento.objects.filter(
            tipo=novo,
        ).update(
            tipo=velho
        )

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_documento_atividades_extraordinarias'),
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='complemento',
            field=jsonfield.fields.JSONField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='evento',
            name='encerrado_em',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='evento',
            name='encerrado_por',
            field=models.ForeignKey(related_name='core_evento_encerrado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='tipoevento',
            name='tipo',
            field=models.PositiveSmallIntegerField(default=10, choices=[(10, 'Peti\xe7\xe3o'), (11, 'Recurso'), (12, 'Encaminhamento'), (13, 'Recebimento'), (14, 'Decis\xe3o'), (15, 'Baixa'), (20, 'Anota\xe7\xe3o'), (30, 'Atividade'), (7010, 'Brinquedoteca')]),
        ),
        migrations.RunPython(
            code=carregar_dados,
            reverse_code=reverse_carregar_dados,
        ),
        migrations.AlterField(
            model_name='participante',
            name='evento',
            field=models.ForeignKey(to='core.Evento', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
