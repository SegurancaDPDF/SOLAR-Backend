# -*- coding: utf-8 -*-
# Importações necessárias

from __future__ import unicode_literals
from django.db import migrations, transaction

# Função responsável por migrar dados entre modelos.

@transaction.atomic
def migrate_data(apps, schema_editor):
    Defensoria = apps.get_model("contrib", "Defensoria")
    DefensoriaTipoEvento = apps.get_model('contrib', 'DefensoriaTipoEvento')
    AtividadeExtraordinariaTipo = apps.get_model('atividade_extraordinaria', 'AtividadeExtraordinariaTipo')
# Obter defensorias que podem cadastrar atividades extraordinárias.
    defensorias = Defensoria.objects.filter(pode_cadastrar_atividade_extraordinaria=True)
    tipos = AtividadeExtraordinariaTipo.objects.all()
# Criar instâncias de DefensoriaTipoEvento para cada combinação de defensoria e tipo de atividade.
    for defensoria in defensorias:
        for tipo in tipos:
            DefensoriaTipoEvento.objects.create(
                defensoria=defensoria,
                tipo_evento=tipo,
                conta_estatistica=True
            )

# Função responsável por reverter a migração de dados.
def reverse_data(apps, schema_editor):
    DefensoriaTipoEvento = apps.get_model('contrib', 'DefensoriaTipoEvento')
    DefensoriaTipoEvento.objects.all().delete() # Excluir todos os objetos DefensoriaTipoEvento


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0049_defensoria_tipo_evento'),
        ('atividade_extraordinaria', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_data
        )
    ]
