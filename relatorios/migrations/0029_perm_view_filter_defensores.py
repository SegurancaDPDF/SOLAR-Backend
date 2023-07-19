# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.contrib.auth.models import Permission

def migrate_data(apps, schema_editor):

    perm_relatorios = Permission.objects.filter(codename='view_relatorios', content_type__model='relatorios').first()
    perm_filtro = Permission.objects.filter(codename='view_filter_defensores', content_type__model='relatorios').first()

    if perm_relatorios and perm_filtro:
        for grupo in perm_relatorios.group_set.all():
            grupo.permissions.add(perm_filtro)

        for usuario in perm_relatorios.user_set.all():
            usuario.user_permissions.add(perm_filtro)

def reverse_migrate_data(apps, schema_editor):

    perm_filtro = Permission.objects.filter(codename='view_filter_defensores', content_type__model='relatorios').first()

    if perm_filtro:

        for grupo in perm_filtro.group_set.all():
            grupo.permissions.remove(perm_filtro)

        for usuario in perm_filtro.user_set.all():
            usuario.user_permissions.remove(perm_filtro)


class Migration(migrations.Migration):

    dependencies = [
        ('relatorios', '0028_functions_quantitativo_ged_assinado'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='relatorios',
            options={'permissions': (('view_relat_atividades', 'Can view relatorio atividades comarca ou diretoria'), ('view_relat_atividades_mensal', 'Can view relatorio atividades (mensal)'), ('view_relat_atividades_indenizatorias', 'Can view relatorio quantidade atividades indenizatorias'), ('view_relat_atuacoes_servidores_por_periodo', 'Can view relatorio lotacao servidor por periodo'), ('view_relat_atividades_servidores', 'Can view relatorio atividades dos servidores'), ('view_relat_atendimentos_defensor', 'Can view relatorio atendimentos do defensor'), ('view_relat_atendimentos_substitutos', 'Can view relatorio atendimentos dos substitutos'), ('view_relat_atendimentos_acordo', 'Can view relatorio atendimentos de acordo'), ('view_relat_atendimentos_primeiro_do_dia', 'Can view relatorio atendimentos - primeiro do dia'), ('view_relat_multidisciplinar', 'Can view relatorio multidisciplinar'), ('view_relat_diligencia', 'Can view relatorio diligencia'), ('view_relat_plantao_periodo', 'Can view relatorio atividades do defensor'), ('view_relat_plantao_periodo_defensor', 'Can view relatorio atividades do defensor no periodo'), ('view_relat_processos', 'Can view relatorio processos'), ('view_relat_processo_fase_acumulacao', 'Can view relatorio fases proc no periodo'), ('view_relat_processo_fase_substituicao', 'Can view relatorio fases proc no periodo'), ('view_relat_perfil_assistidos', 'Can view relatorio perfil assistidos'), ('view_relat_perfil_assistidos_atendimento', 'Can view relatorio perfil assistidos_atendimento'), ('view_relat_penal_visita', 'Can view relatorio penal visitas (anual)'), ('view_relat_penal_atendimento_interessados', 'Can view relatorio penal atendimento interessados (anual)'), ('view_relat_penal_presos_provisorios', 'Can view relatorio penal presos provisorios'), ('view_relat_penal_presos_condenados', 'Can view relatorio penal presos condenados'), ('view_relat_processos_pendentes_por_defensor', 'Can view relatorio anual processos pendentes defensor'), ('view_relat_tempo_espera_atendimento_defensor', 'Can view relatorio tempo de espera atendimento defensor'), ('view_relat_atendimentos_por_qualificacao_total', 'Can view relatorio atendimento por qualificacao total'), ('view_relat_indeferimentos', 'Can view relatorio indeferimentos'), ('view_filter_defensores', 'Can view filtro defensores'))},
        ),
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
    ]
