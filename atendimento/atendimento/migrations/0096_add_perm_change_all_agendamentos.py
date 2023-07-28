# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0095_qualificacao_assunto'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='atendimento',
            options={'ordering': ['-ativo', '-numero'], 'verbose_name': 'Atendimento Geral', 'verbose_name_plural': 'Atendimentos Gerais', 'permissions': (('delete_anotacao', 'Pode excluir anota\xe7\xe3o'), ('agendar_com_bloqueio', 'Pode agendar em dia com bloqueio (feriado)'), ('change_all_agendamentos', 'Pode alterar agendamentos de qualquer comarca'), ('view_all_atendimentos', 'Pode ver teor de atendimentos p\xfablicos e privados'), ('view_129', 'Pode ver Painel 129'), ('view_recepcao', 'Pode ver Painel da Recep\xe7\xe3o'), ('view_defensor', 'Pode ver Painel do Defensor'), ('view_distribuicao', 'Pode ver Painel de Distribui\xe7\xe3o de Atendimentos'), ('unificar_atendimento', 'Pode unificar atendimentos'), ('requalificar_atendimento_retroativo', 'Pode requalificar atendimento retroativo'), ('encaminhar_atendimento_para_qualquer_area', 'Pode encaminhar atendimento p/ qualquer \xe1rea'), ('atender_retroativo', 'Pode atender retroativo'))},
        ),
    ]
