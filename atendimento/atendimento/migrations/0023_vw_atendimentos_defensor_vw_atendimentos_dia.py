# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0022_tarefa_documentos'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DROP VIEW vw_atendimentos_defensor;
            CREATE VIEW vw_atendimentos_defensor AS
             SELECT ad.atendimento_ptr_id,
               aa.numero, aa.tipo,
               aa.data_agendamento,
               aa.data_atendimento,
               a1.nome AS requerente_nome,
               a2.nome AS requerido_nome,
               aa.agenda, ai.inicial_id,
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
               cad.nome as cadastrado_por_nome,
               lib.nome as liberado_por_nome,
               ate.nome as atendido_por_nome
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
               LEFT JOIN contrib_servidor cad on cad.id = aa.cadastrado_por_id
               LEFT JOIN contrib_servidor lib on lib.id = ar.atendido_por_id
               LEFT JOIN contrib_servidor ate on ate.id = aa.atendido_por_id
              WHERE aa.ativo = true AND aa.remarcado_id IS NULL AND (aa.tipo = ANY (ARRAY[1, 2, 4, 9]));""",
            reverse_sql="""
            DROP VIEW vw_atendimentos_defensor;
            CREATE VIEW vw_atendimentos_defensor AS
             SELECT ad.atendimento_ptr_id, aa.numero, aa.tipo, aa.data_agendamento, aa.data_atendimento, a1.nome AS requerente_nome, a2.nome AS requerido_nome, aa.agenda, ai.inicial_id, ai.numero AS inicial_numero, aa.origem_id, ao.tipo AS origem_tipo, ar.id AS recepcao_id, ar.data_atendimento AS data_atendimento_recepcao, ad.defensor_id, (ut.first_name::text || ' '::text) || ut.last_name::text AS defensor_nome, ad.substituto_id, (us.first_name::text || ' '::text) || us.last_name::text AS substituto_nome, ad.responsavel_id, (ur.first_name::text || ' '::text) || ur.last_name::text AS responsavel_nome, ad.defensoria_id, d.nome AS defensoria_nome, d.comarca_id, d.nucleo_id, n.nome AS nucleo_nome, r.nome AS area_nome, q.titulo AS qualificacao_nome, q.especializado_id, aa.ativo, aa.prazo, aa.prioridade
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
               LEFT JOIN auth_user ut ON ut.id = st.usuario_id
               LEFT JOIN defensor_defensor ds ON ds.id = ad.substituto_id
               LEFT JOIN contrib_servidor ss ON ss.id = ds.servidor_id
               LEFT JOIN auth_user us ON us.id = ss.usuario_id
               LEFT JOIN defensor_defensor dr ON dr.id = ad.responsavel_id
               LEFT JOIN contrib_servidor sr ON sr.id = dr.servidor_id
               LEFT JOIN auth_user ur ON ur.id = sr.usuario_id
               LEFT JOIN contrib_defensoria d ON d.id = ad.defensoria_id
               LEFT JOIN nucleo_nucleo n ON n.id = d.nucleo_id
               LEFT JOIN atendimento_qualificacao q ON q.id = aa.qualificacao_id
               LEFT JOIN contrib_area r ON r.id = q.area_id
              WHERE aa.ativo = true AND aa.remarcado_id IS NULL AND (aa.tipo = ANY (ARRAY[1, 2, 4, 9]));""",
        ),
    ]
