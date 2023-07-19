# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('relatorios', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='relatorios',
            options={'permissions': (('view_relat_atividades', 'Can view relatorio atividades comarca ou diretoria'), ('view_relat_atividades_mensal', 'Can view relatorio atividades (mensal)'), ('view_relat_atendimentos_defensor', 'Can view relatorio atendimentos do defensor'), ('view_relat_atendimentos_substitutos', 'Can view relatorio atendimentos dos substitutos'), ('view_relat_plantao_periodo', 'Can view relatorio atividades do defensor'), ('view_relat_plantao_periodo_defensor', 'Can view relatorio atividades do defensor no periodo'), ('view_relat_processos', 'Can view relatorio processos'), ('view_relat_processo_fase_acumulacao', 'Can view relatorio fases proc no periodo'), ('view_relat_processo_fase_substituicao', 'Can view relatorio fases proc no periodo'), ('view_relat_perfil_assistidos', 'Can view relatorio perfil assistidos'))},
        ),
    ]
