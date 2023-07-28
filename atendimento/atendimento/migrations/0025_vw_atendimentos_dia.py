# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0024_vw_atendimentos_defensor_vw_atendimentos_dia'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DROP VIEW vw_atendimentos_dia;
            CREATE OR REPLACE VIEW vw_atendimentos_dia AS
             SELECT ad.atendimento_ptr_id,
                aa.numero,
                aa.inicial_id,
                aa.tipo,
                recepcao.id AS recepcao_id,
                p1.id AS requerente_id,
                a1.nome AS requerente_nome,
                a1.nome_social AS requerente_nome_social,
                    CASE
                        WHEN b1.pne = true THEN true
                        ELSE false
                    END AS requerente_pne,
                p2.id AS requerido_id,
                a2.nome AS requerido_nome,
                a2.nome_social AS requerido_nome_social,
                ca.nome AS area_nome,
                aq.titulo AS qualificacao_titulo,
                cd.nome AS defensoria_nome,
                cd.codigo AS defensoria_codigo,
                tits.nome AS defensor_nome,
                subs.nome AS substituto_nome,
                aa.data_agendamento,
                aa.data_atendimento,
                recepcao.data_atendimento as data_atendimento_recepcao,
                aa.agenda,
                cd.comarca_id,
                cd.predio_id,
                aa.ativo,
                aa.prazo,
                aa.prioridade
               FROM atendimento_defensor ad
                 LEFT JOIN atendimento_atendimento aa ON aa.id = ad.atendimento_ptr_id
                 LEFT JOIN atendimento_atendimento recepcao ON recepcao.origem_id = aa.id AND recepcao.tipo = 3 AND recepcao.ativo = true
                 LEFT JOIN atendimento_qualificacao aq ON aq.id = aa.qualificacao_id
                 LEFT JOIN contrib_area ca ON ca.id = aq.area_id
                 LEFT JOIN contrib_defensoria cd ON cd.id = ad.defensoria_id
                 LEFT JOIN atendimento_pessoa p1 ON p1.atendimento_id =
                    CASE
                        WHEN aa.inicial_id IS NULL THEN aa.id
                        ELSE aa.inicial_id
                    END AND p1.tipo = 0 AND p1.responsavel = true AND p1.ativo = true
                 LEFT JOIN assistido_pessoa a1 ON a1.id = p1.pessoa_id
                 LEFT JOIN assistido_pessoaassistida b1 ON b1.pessoa_ptr_id = p1.pessoa_id
                 LEFT JOIN atendimento_pessoa p2 ON p2.atendimento_id =
                    CASE
                        WHEN aa.inicial_id IS NULL THEN aa.id
                        ELSE aa.inicial_id
                    END AND p2.tipo = 1 AND p2.responsavel = true AND p2.ativo = true
                 LEFT JOIN assistido_pessoa a2 ON a2.id = p2.pessoa_id
                 LEFT JOIN defensor_defensor titd ON titd.id = ad.defensor_id
                 LEFT JOIN contrib_servidor tits ON tits.id = titd.servidor_id
                 LEFT JOIN defensor_defensor subd ON subd.id = ad.substituto_id
                 LEFT JOIN contrib_servidor subs ON subs.id = subd.servidor_id
              WHERE aa.data_agendamento::date = now()::date AND (aa.tipo = ANY (ARRAY[1, 2, 4, 9])) AND aa.remarcado_id IS NULL AND aa.ativo = true;""",
            reverse_sql="""
            DROP VIEW vw_atendimentos_dia;
            CREATE OR REPLACE VIEW vw_atendimentos_dia AS
             SELECT ad.atendimento_ptr_id,
                aa.numero,
                aa.inicial_id,
                aa.tipo,
                recepcao.id AS recepcao_id,
                p1.id AS requerente_id,
                a1.nome AS requerente_nome,
                a1.nome_social AS requerente_nome_social,
                    CASE
                        WHEN b1.pne = true THEN true
                        ELSE false
                    END AS requerente_pne,
                p2.id AS requerido_id,
                a2.nome AS requerido_nome,
                a2.nome_social AS requerido_nome_social,
                ca.nome AS area_nome,
                aq.titulo AS qualificacao_titulo,
                cd.nome AS defensoria_nome,
                cd.codigo AS defensoria_codigo,
                (titu.first_name::text || ' '::text) || titu.last_name::text AS defensor_nome,
                (subu.first_name::text || ' '::text) || subu.last_name::text AS substituto_nome,
                aa.data_agendamento,
                aa.data_atendimento,
                aa.agenda,
                cd.comarca_id,
                cd.predio_id,
                aa.ativo,
                aa.prazo,
                aa.prioridade
               FROM atendimento_defensor ad
                 LEFT JOIN atendimento_atendimento aa ON aa.id = ad.atendimento_ptr_id
                 LEFT JOIN atendimento_atendimento recepcao ON recepcao.origem_id = aa.id AND recepcao.tipo = 3 AND recepcao.ativo = true
                 LEFT JOIN atendimento_qualificacao aq ON aq.id = aa.qualificacao_id
                 LEFT JOIN contrib_area ca ON ca.id = aq.area_id
                 LEFT JOIN contrib_defensoria cd ON cd.id = ad.defensoria_id
                 LEFT JOIN atendimento_pessoa p1 ON p1.atendimento_id =
                    CASE
                        WHEN aa.inicial_id IS NULL THEN aa.id
                        ELSE aa.inicial_id
                    END AND p1.tipo = 0 AND p1.responsavel = true AND p1.ativo = true
                 LEFT JOIN assistido_pessoa a1 ON a1.id = p1.pessoa_id
                 LEFT JOIN assistido_pessoaassistida b1 ON b1.pessoa_ptr_id = p1.pessoa_id
                 LEFT JOIN atendimento_pessoa p2 ON p2.atendimento_id =
                    CASE
                        WHEN aa.inicial_id IS NULL THEN aa.id
                        ELSE aa.inicial_id
                    END AND p2.tipo = 1 AND p2.responsavel = true AND p2.ativo = true
                 LEFT JOIN assistido_pessoa a2 ON a2.id = p2.pessoa_id
                 LEFT JOIN defensor_defensor titd ON titd.id = ad.defensor_id
                 LEFT JOIN contrib_servidor tits ON tits.id = titd.servidor_id
                 LEFT JOIN auth_user titu ON titu.id = tits.usuario_id
                 LEFT JOIN defensor_defensor subd ON subd.id = ad.substituto_id
                 LEFT JOIN contrib_servidor subs ON subs.id = subd.servidor_id
                 LEFT JOIN auth_user subu ON subu.id = subs.usuario_id
              WHERE aa.data_agendamento::date = now()::date AND (aa.tipo = ANY (ARRAY[1, 2, 4, 9])) AND aa.remarcado_id IS NULL AND aa.ativo = true;""",
        )

    ]
