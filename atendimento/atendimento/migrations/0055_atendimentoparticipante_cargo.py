# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from toaiff import table TODO ver da onde vem esse toaiff no python3 deu ModuleNotFoundError

from django.db import migrations, models, connection
import django.db.models.deletion

from contrib.models import Cargo, Servidor
from atendimento.atendimento.models import AtendimentoParticipante


def popula_cargos_participantes(apps, schema_editor):

    cursor = connection.cursor()
    cursor.execute('''SELECT contrib_servidor.id, assistido_profissao.nome
                      FROM contrib_servidor 
                      INNER JOIN assistido_profissao ON assistido_profissao.id = contrib_servidor.profissao_id
                      AND contrib_servidor.profissao_id IS NOT NULL;''')
    servidores_cargos = cursor.fetchall()

    for servidor in servidores_cargos:

        print('servidor: %s. cargo: %s' % (servidor[0], servidor[1]))

        total = 0
        participacoes = AtendimentoParticipante.objects.filter(servidor_id=servidor[0])

        if participacoes.exists():
            cargo = Cargo.objects.filter(nome=servidor[1]).first()
            total = participacoes.update(cargo=cargo)

        print(servidor, total)


def popula_cargos_participantes_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0019_cargo'),
        ('atendimento', '0054_remove_old_manytomany_participantes_em_atendimento'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='atendimentoparticipante',
            table='atendimento_atendimento_participantes',
        ),
        migrations.AddField(
            model_name='atendimentoparticipante',
            name='cargo',
            field=models.ForeignKey(related_name='participantes_atendimentos', blank=True, to='contrib.Cargo', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        # migrations.RunPython(popula_cargos_participantes, popula_cargos_participantes_reverse)
    ]
