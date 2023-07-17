# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('relatorios', '0024_relat_indeferimentos'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='relatorios',
            options={'permissions': (('view_relat_atividades', 'Can view relatorio atividades comarca ou diretoria'), ('view_relat_atividades_mensal', 'Can view relatorio atividades (mensal)'), ('view_relat_atividades_indenizatorias', 'Can view relatorio quantidade atividades indenizatorias'), ('view_relat_atuacoes_servidores_por_periodo', 'Can view relatorio lotacao servidor por periodo'), ('view_relat_atividades_servidores', 'Can view relatorio atividades dos servidores'), ('view_relat_atendimentos_defensor', 'Can view relatorio atendimentos do defensor'), ('view_relat_atendimentos_substitutos', 'Can view relatorio atendimentos dos substitutos'), ('view_relat_atendimentos_acordo', 'Can view relatorio atendimentos de acordo'), ('view_relat_atendimentos_primeiro_do_dia', 'Can view relatorio atendimentos - primeiro do dia'), ('view_relat_multidisciplinar', 'Can view relatorio multidisciplinar'), ('view_relat_diligencia', 'Can view relatorio diligencia'), ('view_relat_plantao_periodo', 'Can view relatorio atividades do defensor'), ('view_relat_plantao_periodo_defensor', 'Can view relatorio atividades do defensor no periodo'), ('view_relat_processos', 'Can view relatorio processos'), ('view_relat_processo_fase_acumulacao', 'Can view relatorio fases proc no periodo'), ('view_relat_processo_fase_substituicao', 'Can view relatorio fases proc no periodo'), ('view_relat_perfil_assistidos', 'Can view relatorio perfil assistidos'), ('view_relat_penal_visita', 'Can view relatorio penal visitas (anual)'), ('view_relat_penal_atendimento_interessados', 'Can view relatorio penal atendimento interessados (anual)'), ('view_relat_penal_presos_provisorios', 'Can view relatorio penal presos provisorios'), ('view_relat_penal_presos_condenados', 'Can view relatorio penal presos condenados'), ('view_relat_processos_pendentes_por_defensor', 'Can view relatorio anual processos pendentes defensor'), ('view_relat_tempo_espera_atendimento_defensor', 'Can view relatorio tempo de espera atendimento defensor'), ('view_relat_atendimentos_por_qualificacao_total', 'Can view relatorio atendimento por qualificacao total'), ('view_relat_indeferimentos', 'Can view relatorio indeferimentos'))},
        ),
    ]
