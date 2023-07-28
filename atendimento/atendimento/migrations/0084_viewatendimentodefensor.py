# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0083_perm_atender_retroativo'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DROP VIEW public.vw_atendimentos_defensor;
            CREATE OR REPLACE VIEW public.vw_atendimentos_defensor AS
            SELECT ad.atendimento_ptr_id,
                aa.numero,
                aa.tipo,
                aa.data_agendamento,
                aa.data_atendimento,
                a1.nome AS requerente_nome,
                a1.nome_social AS requerente_nome_social,
                a2.nome AS requerido_nome,
                a2.nome_social AS requerido_nome_social,
                aa.agenda_id,
                ai.inicial_id,
                ai.numero AS inicial_numero,
                aa.origem_id,
                ao.tipo AS origem_tipo,
                ar.id AS recepcao_id,
                ar.data_atendimento AS data_atendimento_recepcao,
                ad.defensor_id,
                st.nome AS defensor_nome,
                ad.substituto_id,
                ss.nome AS substituto_nome,
                ad.responsavel_id,
                sr.nome AS responsavel_nome,
                ad.defensoria_id,
                d.nome AS defensoria_nome,
                d.comarca_id,
                d.nucleo_id,
                n.nome AS nucleo_nome,
                r.nome AS area_nome,
                q.titulo AS qualificacao_nome,
                q.especializado_id,
                aa.ativo,
                aa.prazo,
                aa.prioridade,
                to_char(aa.data_agendamento, 'HH24:MI:SS'::text) ~~ '00:00:00'::text AS extra,
                cad.nome AS cadastrado_por_nome,
                lib.nome AS liberado_por_nome,
                ate.nome AS atendido_por_nome,
                adO.defensoria_id AS defensoria_origem_id,
                cdO.nome AS defensoria_origem_nome
            FROM atendimento_defensor ad
                LEFT JOIN atendimento_atendimento aa ON aa.id = ad.atendimento_ptr_id
                LEFT JOIN atendimento_atendimento ai ON ai.id = aa.inicial_id
                LEFT JOIN atendimento_atendimento ao ON ao.id = aa.origem_id
                LEFT JOIN atendimento_defensor adO ON adO.atendimento_ptr_id = ao.origem_id
                LEFT JOIN contrib_defensoria cdO ON cdO.id = adO.defensoria_id
                LEFT JOIN atendimento_atendimento ar ON ar.origem_id = aa.id AND ar.tipo = 3 AND ar.ativo = true
                LEFT JOIN atendimento_pessoa p1 ON p1.atendimento_id =
                CASE
                    WHEN aa.inicial_id IS NULL THEN aa.id
                    ELSE aa.inicial_id
                END AND p1.tipo = 0 AND p1.responsavel = true AND p1.ativo = true
                LEFT JOIN assistido_pessoa a1 ON a1.id = p1.pessoa_id
                LEFT JOIN atendimento_pessoa p2 ON p2.atendimento_id =
                CASE
                    WHEN aa.inicial_id IS NULL THEN aa.id
                    ELSE aa.inicial_id
                END AND p2.tipo = 1 AND p2.responsavel = true AND p2.ativo = true
                LEFT JOIN assistido_pessoa a2 ON a2.id = p2.pessoa_id
                LEFT JOIN defensor_defensor dt ON dt.id = ad.defensor_id
                LEFT JOIN contrib_servidor st ON st.id = dt.servidor_id
                LEFT JOIN defensor_defensor ds ON ds.id = ad.substituto_id
                LEFT JOIN contrib_servidor ss ON ss.id = ds.servidor_id
                LEFT JOIN defensor_defensor dr ON dr.id = ad.responsavel_id
                LEFT JOIN contrib_servidor sr ON sr.id = dr.servidor_id
                LEFT JOIN contrib_defensoria d ON d.id = ad.defensoria_id
                LEFT JOIN nucleo_nucleo n ON n.id = d.nucleo_id
                LEFT JOIN atendimento_qualificacao q ON q.id = aa.qualificacao_id
                LEFT JOIN contrib_area r ON r.id = q.area_id
                LEFT JOIN contrib_servidor cad ON cad.id = aa.cadastrado_por_id
                LEFT JOIN contrib_servidor lib ON lib.id = ar.atendido_por_id
                LEFT JOIN contrib_servidor ate ON ate.id = aa.atendido_por_id
            WHERE aa.ativo = true AND aa.remarcado_id IS NULL AND (aa.tipo = ANY (ARRAY[1, 2, 4, 9]));""",
            reverse_sql="""
            DROP VIEW public.vw_atendimentos_defensor;
            CREATE OR REPLACE VIEW public.vw_atendimentos_defensor AS
            SELECT ad.atendimento_ptr_id,
                aa.numero,
                aa.tipo,
                aa.data_agendamento,
                aa.data_atendimento,
                a1.nome AS requerente_nome,
                a1.nome_social AS requerente_nome_social,
                a2.nome AS requerido_nome,
                a2.nome_social AS requerido_nome_social,
                aa.agenda_id,
                ai.inicial_id,
                ai.numero AS inicial_numero,
                aa.origem_id,
                ao.tipo AS origem_tipo,
                ar.id AS recepcao_id,
                ar.data_atendimento AS data_atendimento_recepcao,
                ad.defensor_id,
                st.nome AS defensor_nome,
                ad.substituto_id,
                ss.nome AS substituto_nome,
                ad.responsavel_id,
                sr.nome AS responsavel_nome,
                ad.defensoria_id,
                d.nome AS defensoria_nome,
                d.comarca_id,
                d.nucleo_id,
                n.nome AS nucleo_nome,
                r.nome AS area_nome,
                q.titulo AS qualificacao_nome,
                q.especializado_id,
                aa.ativo,
                aa.prazo,
                aa.prioridade,
                to_char(aa.data_agendamento, 'HH24:MI:SS'::text) ~~ '00:00:00'::text AS extra,
                cad.nome AS cadastrado_por_nome,
                lib.nome AS liberado_por_nome,
                ate.nome AS atendido_por_nome
            FROM atendimento_defensor ad
                LEFT JOIN atendimento_atendimento aa ON aa.id = ad.atendimento_ptr_id
                LEFT JOIN atendimento_atendimento ai ON ai.id = aa.inicial_id
                LEFT JOIN atendimento_atendimento ao ON ao.id = aa.origem_id
                LEFT JOIN atendimento_atendimento ar ON ar.origem_id = aa.id AND ar.tipo = 3 AND ar.ativo = true
                LEFT JOIN atendimento_pessoa p1 ON p1.atendimento_id =
                CASE
                    WHEN aa.inicial_id IS NULL THEN aa.id
                    ELSE aa.inicial_id
                END AND p1.tipo = 0 AND p1.responsavel = true AND p1.ativo = true
                LEFT JOIN assistido_pessoa a1 ON a1.id = p1.pessoa_id
                LEFT JOIN atendimento_pessoa p2 ON p2.atendimento_id =
                CASE
                    WHEN aa.inicial_id IS NULL THEN aa.id
                    ELSE aa.inicial_id
                END AND p2.tipo = 1 AND p2.responsavel = true AND p2.ativo = true
                LEFT JOIN assistido_pessoa a2 ON a2.id = p2.pessoa_id
                LEFT JOIN defensor_defensor dt ON dt.id = ad.defensor_id
                LEFT JOIN contrib_servidor st ON st.id = dt.servidor_id
                LEFT JOIN defensor_defensor ds ON ds.id = ad.substituto_id
                LEFT JOIN contrib_servidor ss ON ss.id = ds.servidor_id
                LEFT JOIN defensor_defensor dr ON dr.id = ad.responsavel_id
                LEFT JOIN contrib_servidor sr ON sr.id = dr.servidor_id
                LEFT JOIN contrib_defensoria d ON d.id = ad.defensoria_id
                LEFT JOIN nucleo_nucleo n ON n.id = d.nucleo_id
                LEFT JOIN atendimento_qualificacao q ON q.id = aa.qualificacao_id
                LEFT JOIN contrib_area r ON r.id = q.area_id
                LEFT JOIN contrib_servidor cad ON cad.id = aa.cadastrado_por_id
                LEFT JOIN contrib_servidor lib ON lib.id = ar.atendido_por_id
                LEFT JOIN contrib_servidor ate ON ate.id = aa.atendido_por_id
            WHERE aa.ativo = true AND aa.remarcado_id IS NULL AND (aa.tipo = ANY (ARRAY[1, 2, 4, 9]));""",
        ),
        migrations.CreateModel(
            name='ViewAtendimentoDefensor',
            fields=[
                ('id', models.IntegerField(serialize=False, verbose_name='ID', primary_key=True, db_column='atendimento_ptr_id')),
                ('numero', models.CharField(max_length=256, verbose_name='N\xfamero')),
                ('tipo', models.SmallIntegerField(verbose_name='Tipo', choices=[(0, 'Liga\xe7\xe3o'), (1, 'Inicial'), (2, 'Retorno'), (3, 'Recep\xe7\xe3o'), (4, 'Apoio de N\xfacleo Especializado'), (5, 'Anota\xe7\xe3o'), (6, 'Processo'), (7, 'Visita ao Preso'), (8, 'Atendimento ao Interessado'), (9, 'Encaminhamento'), (10, 'Atividade')])),
                ('data_agendamento', models.DateTimeField(verbose_name='Data do agendamento')),
                ('data_atendimento', models.DateTimeField(verbose_name='Data do atendimento')),
                ('requerente_nome', models.CharField(max_length=256, verbose_name='Requerente nome')),
                ('requerente_nome_social', models.CharField(max_length=256, verbose_name='Requerente nome social')),
                ('requerido_nome', models.CharField(max_length=256, verbose_name='Requerido nome')),
                ('requerido_nome_social', models.CharField(max_length=256, verbose_name='Requerido nome social')),
                ('agenda_id', models.IntegerField(verbose_name='Agenda ID')),
                ('inicial_id', models.IntegerField(verbose_name='Inicial ID')),
                ('inicial_numero', models.CharField(max_length=256, verbose_name='Inicial N\xfamero')),
                ('origem_id', models.IntegerField(verbose_name='Origem ID')),
                ('origem_tipo', models.SmallIntegerField(verbose_name='Tipo Origem')),
                ('recepcao_id', models.IntegerField(verbose_name='Atendimento Recep\xe7\xe3o ID')),
                ('data_atendimento_recepcao', models.DateTimeField(verbose_name='Data do atendimento da Recep\xe7\xe3o')),
                ('defensor_id', models.IntegerField(verbose_name='Defensor ID')),
                ('defensor_nome', models.CharField(max_length=256, verbose_name='Defensor nome')),
                ('substituto_id', models.IntegerField(verbose_name='Substituto ID')),
                ('substituto_nome', models.CharField(max_length=256, verbose_name='Substituto nome')),
                ('responsavel_id', models.IntegerField(verbose_name='Respons\xe1vel ID')),
                ('responsavel_nome', models.CharField(max_length=256, verbose_name='Respons\xe1vel nome')),
                ('defensoria_id', models.IntegerField(verbose_name='Defensoria ID')),
                ('defensoria_nome', models.CharField(max_length=256, verbose_name='Defensoria nome')),
                ('comarca_id', models.IntegerField(verbose_name='Comarca ID')),
                ('nucleo_id', models.IntegerField(verbose_name='N\xfacleo ID')),
                ('nucleo_nome', models.CharField(max_length=256, verbose_name='N\xfacleo nome')),
                ('area_nome', models.CharField(max_length=256, verbose_name='\xc1rea nome')),
                ('qualificacao_nome', models.CharField(max_length=256, verbose_name='Qualifica\xe7\xe3o nome')),
                ('especializado_id', models.IntegerField(verbose_name='Especializado ID')),
                ('ativo', models.BooleanField(verbose_name='Ativo')),
                ('prazo', models.BooleanField(verbose_name='Prazo')),
                ('prioridade', models.SmallIntegerField(verbose_name='Prioridade')),
                ('extra', models.BooleanField(verbose_name='Extra-Pauta')),
                ('cadastrado_por_nome', models.CharField(max_length=256, verbose_name='Cadastrado por nome')),
                ('liberado_por_nome', models.CharField(max_length=256, verbose_name='Liberado por nome')),
                ('atendido_por_nome', models.CharField(max_length=256, verbose_name='Atendido por nome')),
                ('defensoria_origem_id', models.IntegerField(verbose_name='Defensoria Origem ID')),
                ('defensoria_origem_nome', models.CharField(max_length=256, verbose_name='Defensoria Origem nome')),
            ],
            options={
                'db_table': 'vw_atendimentos_defensor',
                'managed': False,
            },
        ),
    ]
