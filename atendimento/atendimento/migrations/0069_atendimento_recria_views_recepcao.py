# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    atomic = True

    dependencies = [
        ('atendimento', '0068_atendimento_prioridade_80_2'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
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
  WHERE aa.ativo = true AND aa.remarcado_id IS NULL AND (aa.tipo = ANY (ARRAY[1, 2, 4, 9]));
            """,
            reverse_sql=""
        ),
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE VIEW public.vw_atendimentos_dia_aguardando AS 
 WITH cte_atendimentos AS (
         SELECT aa_1.id,
            aa_1.inicial_id,
            COALESCE(aa_1.inicial_id, aa_1.id) AS atendimento_id_inicial,
            aa_1.numero,
            aa_1.tipo,
            aa_1.data_agendamento,
            to_char(aa_1.data_agendamento, 'HH24:MI'::character varying::text) AS horario,
            aa_1.data_atendimento,
            to_char(aa_1.data_atendimento, 'HH24:MI'::character varying::text) AS horario_atendimento,
            aa_1.agenda_id,
            aa_1.ativo,
            aa_1.prazo,
            aa_1.prioridade,
            aa_1.qualificacao_id,
            ad.defensoria_id,
            ad.defensor_id,
            ad.substituto_id
           FROM atendimento_defensor ad
             JOIN atendimento_atendimento aa_1 ON aa_1.id = ad.atendimento_ptr_id AND aa_1.data_agendamento >= 'now'::text::date AND aa_1.data_agendamento <= ('now'::text::date + '23:59:59.999'::interval) AND (aa_1.tipo = 1 OR aa_1.tipo = 2 OR aa_1.tipo = 4 OR aa_1.tipo = 9) AND aa_1.remarcado_id IS NULL AND aa_1.ativo = true
        ), cte_atividades AS (
         SELECT atividades_1.origem_id,
            count(atividades_1.origem_id) AS qtd
           FROM cte_atendimentos aa_1
             JOIN atendimento_atendimento atividades_1 ON aa_1.id = atividades_1.origem_id AND atividades_1.tipo = 10 AND atividades_1.ativo = true
          GROUP BY atividades_1.origem_id
        ), cte_requerentes AS (
         SELECT DISTINCT p1.id,
            a1.id AS pessoa_id,
            a1.nome,
            a1.nome_social,
            a1.apelido,
            a1.tipo,
            b1.pne,
            aa_1.atendimento_id_inicial AS atendimento_id
           FROM cte_atendimentos aa_1
             JOIN atendimento_pessoa p1 ON p1.atendimento_id = aa_1.atendimento_id_inicial AND p1.tipo = 0 AND p1.responsavel = true AND p1.ativo = true
             JOIN assistido_pessoa a1 ON a1.id = p1.pessoa_id
             JOIN assistido_pessoaassistida b1 ON b1.pessoa_ptr_id = p1.pessoa_id
        ), cte_requeridos AS (
         SELECT DISTINCT p2.id,
            a2.id AS pessoa_id,
            a2.nome,
            a2.nome_social,
            a2.apelido,
            a2.tipo,
            aa_1.atendimento_id_inicial AS atendimento_id
           FROM cte_atendimentos aa_1
             JOIN atendimento_pessoa p2 ON p2.atendimento_id = aa_1.atendimento_id_inicial AND p2.tipo = 1 AND p2.responsavel = true AND p2.ativo = true
             JOIN assistido_pessoa a2 ON a2.id = p2.pessoa_id
        )
 SELECT aa.id AS atendimento_ptr_id,
    aa.numero,
    aa.inicial_id,
    aa.tipo,
    recepcao.id AS recepcao_id,
    recepcao.historico AS historico_recepcao,
    requerente.id AS requerente_id,
    requerente.pessoa_id AS requerente_pessoa_id,
    requerente.nome AS requerente_nome,
    requerente.nome_social AS requerente_nome_social,
    requerente.pne AS requerente_pne,
    requerente.apelido AS requerente_apelido,
    requerente.tipo AS requerente_tipo,
    requerido.id AS requerido_id,
    requerido.pessoa_id AS requerido_pessoa_id,
    requerido.nome AS requerido_nome,
    requerido.nome_social AS requerido_nome_social,
    requerido.apelido AS requerido_apelido,
    requerido.tipo AS requerido_tipo,
    ca.nome AS area_nome,
    aq.titulo AS qualificacao_titulo,
    cd.nome AS defensoria_nome,
    cd.codigo AS defensoria_codigo,
    tits.nome AS defensor_nome,
    titu.username AS defensor_username,
    subs.nome AS substituto_nome,
    subu.username AS substituto_username,
    aa.data_agendamento,
    aa.data_atendimento,
        CASE
            WHEN aa.data_atendimento IS NOT NULL THEN 1
            ELSE 0
        END AS historico_atendimento,
    aa.horario,
    aa.horario_atendimento,
    recepcao.data_atendimento AS data_atendimento_recepcao,
    to_char(recepcao.data_atendimento, 'HH24:MI'::text) AS horario_atendimento_recepcao,
    aa.agenda_id,
    cd.comarca_id,
    cd.predio_id,
    aa.ativo,
    aa.prazo,
    aa.prioridade,
    COALESCE(atividades.qtd, 0::bigint) AS atividades,
        CASE
            WHEN aa.horario = '00:00'::text THEN 1
            ELSE 0
        END AS extrapauta
   FROM cte_atendimentos aa
     LEFT JOIN cte_atividades atividades ON aa.id = atividades.origem_id
     LEFT JOIN atendimento_atendimento recepcao ON recepcao.origem_id = aa.id AND recepcao.tipo = 3 AND recepcao.ativo = true
     LEFT JOIN atendimento_qualificacao aq ON aq.id = aa.qualificacao_id
     LEFT JOIN contrib_area ca ON ca.id = aq.area_id
     LEFT JOIN contrib_defensoria cd ON cd.id = aa.defensoria_id
     LEFT JOIN cte_requerentes requerente ON requerente.atendimento_id = aa.atendimento_id_inicial
     LEFT JOIN cte_requeridos requerido ON requerido.atendimento_id = aa.atendimento_id_inicial
     LEFT JOIN defensor_defensor titd ON titd.id = aa.defensor_id
     LEFT JOIN contrib_servidor tits ON tits.id = titd.servidor_id
     LEFT JOIN auth_user titu ON titu.id = tits.usuario_id
     LEFT JOIN defensor_defensor subd ON subd.id = aa.substituto_id
     LEFT JOIN contrib_servidor subs ON subs.id = subd.servidor_id
     LEFT JOIN auth_user subu ON subu.id = subs.usuario_id
  WHERE aa.data_atendimento IS NULL AND recepcao.id IS NULL AND (date_part('hour'::text, aa.data_agendamento) = 0::double precision OR date_part('hour'::text, aa.data_agendamento) <> 0::double precision AND (now() - aa.data_agendamento) < '00:15:00'::interval);
            """,
            reverse_sql=""
        ),
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE VIEW public.vw_atendimentos_dia_atendidos AS 
 WITH cte_atendimentos AS (
         SELECT aa_1.id,
            aa_1.inicial_id,
            COALESCE(aa_1.inicial_id, aa_1.id) AS atendimento_id_inicial,
            aa_1.numero,
            aa_1.tipo,
            aa_1.data_agendamento,
            to_char(aa_1.data_agendamento, 'HH24:MI'::text) AS horario,
            aa_1.data_atendimento,
            to_char(aa_1.data_atendimento, 'HH24:MI'::text) AS horario_atendimento,
            aa_1.agenda_id,
            aa_1.ativo,
            aa_1.prazo,
            aa_1.prioridade,
            aa_1.qualificacao_id,
            ad.defensoria_id,
            ad.defensor_id,
            ad.substituto_id,
            aa_1.historico_recepcao
           FROM atendimento_defensor ad
             JOIN atendimento_atendimento aa_1 ON aa_1.id = ad.atendimento_ptr_id AND aa_1.data_agendamento >= 'now'::text::date AND aa_1.data_agendamento <= ('now'::text::date + '23:59:59.999'::interval) AND (aa_1.tipo = 1 OR aa_1.tipo = 2 OR aa_1.tipo = 4 OR aa_1.tipo = 9) AND aa_1.remarcado_id IS NULL AND aa_1.ativo = true AND aa_1.data_atendimento IS NOT NULL
        ), cte_atividades AS (
         SELECT atividades_1.origem_id,
            count(atividades_1.origem_id) AS qtd
           FROM cte_atendimentos aa_1
             JOIN atendimento_atendimento atividades_1 ON aa_1.id = atividades_1.origem_id AND atividades_1.tipo = 10 AND atividades_1.ativo = true
          GROUP BY atividades_1.origem_id
        ), cte_requerentes AS (
         SELECT DISTINCT p1.id,
            a1.id AS pessoa_id,
            a1.nome,
            a1.nome_social,
            a1.apelido,
            a1.tipo,
            b1.pne,
            aa_1.atendimento_id_inicial AS atendimento_id
           FROM cte_atendimentos aa_1
             JOIN atendimento_pessoa p1 ON p1.atendimento_id = aa_1.atendimento_id_inicial AND p1.tipo = 0 AND p1.responsavel = true AND p1.ativo = true
             JOIN assistido_pessoa a1 ON a1.id = p1.pessoa_id
             JOIN assistido_pessoaassistida b1 ON b1.pessoa_ptr_id = p1.pessoa_id
        ), cte_requeridos AS (
         SELECT DISTINCT p2.id,
            a2.id AS pessoa_id,
            a2.nome,
            a2.nome_social,
            a2.apelido,
            a2.tipo,
            aa_1.atendimento_id_inicial AS atendimento_id
           FROM cte_atendimentos aa_1
             JOIN atendimento_pessoa p2 ON p2.atendimento_id = aa_1.atendimento_id_inicial AND p2.tipo = 1 AND p2.responsavel = true AND p2.ativo = true
             JOIN assistido_pessoa a2 ON a2.id = p2.pessoa_id
        )
 SELECT aa.id AS atendimento_ptr_id,
    aa.numero,
    aa.inicial_id,
    aa.tipo,
    recepcao.id AS recepcao_id,
    btrim(aa.historico_recepcao) AS historico_recepcao,
    requerente.id AS requerente_id,
    requerente.pessoa_id AS requerente_pessoa_id,
    requerente.nome AS requerente_nome,
    requerente.nome_social AS requerente_nome_social,
    requerente.pne AS requerente_pne,
    requerente.apelido AS requerente_apelido,
    requerente.tipo AS requerente_tipo,
    requerido.id AS requerido_id,
    requerido.pessoa_id AS requerido_pessoa_id,
    requerido.nome AS requerido_nome,
    requerido.nome_social AS requerido_nome_social,
    requerido.apelido AS requerido_apelido,
    requerido.tipo AS requerido_tipo,
    ca.nome AS area_nome,
    aq.titulo AS qualificacao_titulo,
    cd.nome AS defensoria_nome,
    cd.codigo AS defensoria_codigo,
    tits.nome AS defensor_nome,
    titu.username AS defensor_username,
    subs.nome AS substituto_nome,
    subu.username AS substituto_username,
    aa.data_agendamento,
    aa.data_atendimento,
        CASE
            WHEN aa.data_atendimento IS NOT NULL THEN 1
            ELSE 0
        END AS historico_atendimento,
    aa.horario,
    aa.horario_atendimento,
    recepcao.data_atendimento AS data_atendimento_recepcao,
    to_char(recepcao.data_atendimento, 'HH24:MI'::text) AS horario_atendimento_recepcao,
    aa.agenda_id,
    cd.comarca_id,
    cd.predio_id,
    aa.ativo,
    aa.prazo,
    aa.prioridade,
    COALESCE(atividades.qtd, 0::bigint) AS atividades,
        CASE
            WHEN aa.horario = '00:00'::text THEN 1
            ELSE 0
        END AS extrapauta
   FROM cte_atendimentos aa
     LEFT JOIN cte_atividades atividades ON aa.id = atividades.origem_id
     LEFT JOIN atendimento_atendimento recepcao ON recepcao.origem_id = aa.id AND recepcao.tipo = 3 AND recepcao.ativo = true
     LEFT JOIN atendimento_qualificacao aq ON aq.id = aa.qualificacao_id
     LEFT JOIN contrib_area ca ON ca.id = aq.area_id
     LEFT JOIN contrib_defensoria cd ON cd.id = aa.defensoria_id
     LEFT JOIN cte_requerentes requerente ON requerente.atendimento_id = aa.atendimento_id_inicial
     LEFT JOIN cte_requeridos requerido ON requerido.atendimento_id = aa.atendimento_id_inicial
     LEFT JOIN defensor_defensor titd ON titd.id = aa.defensor_id
     LEFT JOIN contrib_servidor tits ON tits.id = titd.servidor_id
     LEFT JOIN auth_user titu ON titu.id = tits.usuario_id
     LEFT JOIN defensor_defensor subd ON subd.id = aa.substituto_id
     LEFT JOIN contrib_servidor subs ON subs.id = subd.servidor_id
     LEFT JOIN auth_user subu ON subu.id = subs.usuario_id;
            """,
            reverse_sql=""
        ),
        migrations.RunSQL(
            sql="""CREATE OR REPLACE VIEW public.vw_atendimentos_dia_atrasados AS 
 WITH cte_atendimentos AS (
         SELECT aa_1.id,
            aa_1.inicial_id,
            COALESCE(aa_1.inicial_id, aa_1.id) AS atendimento_id_inicial,
            aa_1.numero,
            aa_1.tipo,
            aa_1.data_agendamento,
            to_char(aa_1.data_agendamento, 'HH24:MI'::text) AS horario,
            aa_1.data_atendimento,
            to_char(aa_1.data_atendimento, 'HH24:MI'::text) AS horario_atendimento,
            aa_1.agenda_id,
            aa_1.ativo,
            aa_1.prazo,
            aa_1.prioridade,
            aa_1.qualificacao_id,
            ad.defensoria_id,
            ad.defensor_id,
            ad.substituto_id,
            aa_1.historico_recepcao
           FROM atendimento_defensor ad
             JOIN atendimento_atendimento aa_1 ON aa_1.id = ad.atendimento_ptr_id AND aa_1.data_agendamento >= 'now'::text::date AND aa_1.data_agendamento <= ('now'::text::date + '23:59:59.999'::interval) AND (aa_1.tipo = 1 OR aa_1.tipo = 2 OR aa_1.tipo = 4 OR aa_1.tipo = 9) AND aa_1.remarcado_id IS NULL AND aa_1.ativo = true
        ), cte_atividades AS (
         SELECT atividades_1.origem_id,
            count(atividades_1.origem_id) AS qtd
           FROM cte_atendimentos aa_1
             JOIN atendimento_atendimento atividades_1 ON aa_1.id = atividades_1.origem_id AND atividades_1.tipo = 10 AND atividades_1.ativo = true
          GROUP BY atividades_1.origem_id
        ), cte_requerentes AS (
         SELECT DISTINCT p1.id,
            a1.id AS pessoa_id,
            a1.nome,
            a1.nome_social,
            a1.apelido,
            a1.tipo,
            b1.pne,
            aa_1.atendimento_id_inicial AS atendimento_id
           FROM cte_atendimentos aa_1
             JOIN atendimento_pessoa p1 ON p1.atendimento_id = aa_1.atendimento_id_inicial AND p1.tipo = 0 AND p1.responsavel = true AND p1.ativo = true
             JOIN assistido_pessoa a1 ON a1.id = p1.pessoa_id
             JOIN assistido_pessoaassistida b1 ON b1.pessoa_ptr_id = p1.pessoa_id
        ), cte_requeridos AS (
         SELECT DISTINCT p2.id,
            a2.id AS pessoa_id,
            a2.nome,
            a2.nome_social,
            a2.apelido,
            a2.tipo,
            aa_1.atendimento_id_inicial AS atendimento_id
           FROM cte_atendimentos aa_1
             JOIN atendimento_pessoa p2 ON p2.atendimento_id = aa_1.atendimento_id_inicial AND p2.tipo = 1 AND p2.responsavel = true AND p2.ativo = true
             JOIN assistido_pessoa a2 ON a2.id = p2.pessoa_id
        )
 SELECT aa.id AS atendimento_ptr_id,
    aa.numero,
    aa.inicial_id,
    aa.tipo,
    recepcao.id AS recepcao_id,
    btrim(aa.historico_recepcao) AS historico_recepcao,
    requerente.id AS requerente_id,
    requerente.pessoa_id AS requerente_pessoa_id,
    requerente.nome AS requerente_nome,
    requerente.nome_social AS requerente_nome_social,
    requerente.apelido AS requerente_apelido,
    requerente.tipo AS requerente_tipo,
    requerente.pne AS requerente_pne,
    requerido.id AS requerido_id,
    requerido.pessoa_id AS requerido_pessoa_id,
    requerido.nome AS requerido_nome,
    requerido.nome_social AS requerido_nome_social,
    requerido.apelido AS requerido_apelido,
    requerido.tipo AS requerido_tipo,
    ca.nome AS area_nome,
    aq.titulo AS qualificacao_titulo,
    cd.nome AS defensoria_nome,
    cd.codigo AS defensoria_codigo,
    tits.nome AS defensor_nome,
    titu.username AS defensor_username,
    subs.nome AS substituto_nome,
    subu.username AS substituto_username,
    aa.data_agendamento,
    aa.data_atendimento,
        CASE
            WHEN aa.data_atendimento IS NOT NULL THEN 1
            ELSE 0
        END AS historico_atendimento,
    aa.horario,
    aa.horario_atendimento,
    recepcao.data_atendimento AS data_atendimento_recepcao,
    to_char(recepcao.data_atendimento, 'HH24:MI'::text) AS horario_atendimento_recepcao,
    aa.agenda_id,
    cd.comarca_id,
    cd.predio_id,
    aa.ativo,
    aa.prazo,
    aa.prioridade,
    COALESCE(atividades.qtd, 0::bigint) AS atividades,
        CASE
            WHEN aa.horario = '00:00'::text THEN 1
            ELSE 0
        END AS extrapauta
   FROM cte_atendimentos aa
     LEFT JOIN cte_atividades atividades ON aa.id = atividades.origem_id
     LEFT JOIN atendimento_atendimento recepcao ON recepcao.origem_id = aa.id AND recepcao.tipo = 3 AND recepcao.ativo = true
     LEFT JOIN atendimento_qualificacao aq ON aq.id = aa.qualificacao_id
     LEFT JOIN contrib_area ca ON ca.id = aq.area_id
     LEFT JOIN contrib_defensoria cd ON cd.id = aa.defensoria_id
     LEFT JOIN cte_requerentes requerente ON requerente.atendimento_id = aa.atendimento_id_inicial
     LEFT JOIN cte_requeridos requerido ON requerido.atendimento_id = aa.atendimento_id_inicial
     LEFT JOIN defensor_defensor titd ON titd.id = aa.defensor_id
     LEFT JOIN contrib_servidor tits ON tits.id = titd.servidor_id
     LEFT JOIN auth_user titu ON titu.id = tits.usuario_id
     LEFT JOIN defensor_defensor subd ON subd.id = aa.substituto_id
     LEFT JOIN contrib_servidor subs ON subs.id = subd.servidor_id
     LEFT JOIN auth_user subu ON subu.id = subs.usuario_id
  WHERE aa.data_atendimento IS NULL AND recepcao.id IS NULL AND date_part('hour'::text, aa.data_agendamento) <> 0::double precision AND (now() - aa.data_agendamento) >= '00:15:00'::interval;""",
            reverse_sql=""
        ),
        migrations.RunSQL(
            sql="""CREATE OR REPLACE VIEW public.vw_atendimentos_dia_em_atendimento AS 
 WITH cte_atendimentos AS (
         SELECT aa_1.id,
            aa_1.inicial_id,
            COALESCE(aa_1.inicial_id, aa_1.id) AS atendimento_id_inicial,
            aa_1.numero,
            aa_1.tipo,
            aa_1.data_agendamento,
            to_char(aa_1.data_agendamento, 'HH24:MI'::text) AS horario,
            aa_1.data_atendimento,
            to_char(aa_1.data_atendimento, 'HH24:MI'::text) AS horario_atendimento,
            aa_1.agenda_id,
            aa_1.ativo,
            aa_1.prazo,
            aa_1.prioridade,
            aa_1.qualificacao_id,
            ad.defensoria_id,
            ad.defensor_id,
            ad.substituto_id,
            aa_1.historico_recepcao
           FROM atendimento_defensor ad
             JOIN atendimento_atendimento aa_1 ON aa_1.id = ad.atendimento_ptr_id AND aa_1.data_agendamento >= 'now'::text::date AND aa_1.data_agendamento <= ('now'::text::date + '23:59:59.999'::interval) AND (aa_1.tipo = 1 OR aa_1.tipo = 2 OR aa_1.tipo = 4 OR aa_1.tipo = 9) AND aa_1.remarcado_id IS NULL AND aa_1.ativo = true
        ), cte_atividades AS (
         SELECT atividades_1.origem_id,
            count(atividades_1.origem_id) AS qtd
           FROM cte_atendimentos aa_1
             JOIN atendimento_atendimento atividades_1 ON aa_1.id = atividades_1.origem_id AND atividades_1.tipo = 10 AND atividades_1.ativo = true
          GROUP BY atividades_1.origem_id
        ), cte_requerentes AS (
         SELECT DISTINCT p1.id,
            a1.id AS pessoa_id,
            a1.nome,
            a1.nome_social,
            a1.apelido,
            a1.tipo,
            b1.pne,
            aa_1.atendimento_id_inicial AS atendimento_id
           FROM cte_atendimentos aa_1
             JOIN atendimento_pessoa p1 ON p1.atendimento_id = aa_1.atendimento_id_inicial AND p1.tipo = 0 AND p1.responsavel = true AND p1.ativo = true
             JOIN assistido_pessoa a1 ON a1.id = p1.pessoa_id
             JOIN assistido_pessoaassistida b1 ON b1.pessoa_ptr_id = p1.pessoa_id
        ), cte_requeridos AS (
         SELECT DISTINCT p2.id,
            a2.id AS pessoa_id,
            a2.nome,
            a2.nome_social,
            a2.apelido,
            a2.tipo,
            aa_1.atendimento_id_inicial AS atendimento_id
           FROM cte_atendimentos aa_1
             JOIN atendimento_pessoa p2 ON p2.atendimento_id = aa_1.atendimento_id_inicial AND p2.tipo = 1 AND p2.responsavel = true AND p2.ativo = true
             JOIN assistido_pessoa a2 ON a2.id = p2.pessoa_id
        )
 SELECT DISTINCT aa.id AS atendimento_ptr_id,
    aa.numero,
    aa.inicial_id,
    aa.tipo,
    recepcao.id AS recepcao_id,
    btrim(aa.historico_recepcao) AS historico_recepcao,
    requerente.id AS requerente_id,
    requerente.pessoa_id AS requerente_pessoa_id,
    requerente.nome AS requerente_nome,
    requerente.nome_social AS requerente_nome_social,
    requerente.pne AS requerente_pne,
    requerente.apelido AS requerente_apelido,
    requerente.tipo AS requerente_tipo,
    requerido.id AS requerido_id,
    requerido.pessoa_id AS requerido_pessoa_id,
    requerido.nome AS requerido_nome,
    requerido.nome_social AS requerido_nome_social,
    requerido.apelido AS requerido_apelido,
    requerido.tipo AS requerido_tipo,
    ca.nome AS area_nome,
    aq.titulo AS qualificacao_titulo,
    cd.nome AS defensoria_nome,
    cd.codigo AS defensoria_codigo,
    tits.nome AS defensor_nome,
    titu.username AS defensor_username,
    subs.nome AS substituto_nome,
    subu.username AS substituto_username,
    aa.data_agendamento,
    aa.data_atendimento,
        CASE
            WHEN aa.data_atendimento IS NOT NULL THEN 1
            ELSE 0
        END AS historico_atendimento,
    aa.horario,
    aa.horario_atendimento,
    recepcao.data_atendimento AS data_atendimento_recepcao,
    to_char(recepcao.data_atendimento, 'HH24:MI'::text) AS horario_atendimento_recepcao,
    aa.agenda_id,
    cd.comarca_id,
    cd.predio_id,
    aa.ativo,
    aa.prazo,
    aa.prioridade,
    COALESCE(atividades.qtd, 0::bigint) AS atividades,
        CASE
            WHEN aa.horario = '00:00'::text THEN 1
            ELSE 0
        END AS extrapauta
   FROM cte_atendimentos aa
     LEFT JOIN cte_atividades atividades ON aa.id = atividades.origem_id
     LEFT JOIN atendimento_atendimento recepcao ON recepcao.origem_id = aa.id AND recepcao.tipo = 3 AND recepcao.ativo = true
     LEFT JOIN atendimento_qualificacao aq ON aq.id = aa.qualificacao_id
     LEFT JOIN contrib_area ca ON ca.id = aq.area_id
     LEFT JOIN contrib_defensoria cd ON cd.id = aa.defensoria_id
     LEFT JOIN cte_requerentes requerente ON requerente.atendimento_id = aa.atendimento_id_inicial
     LEFT JOIN cte_requeridos requerido ON requerido.atendimento_id = aa.atendimento_id_inicial
     LEFT JOIN defensor_defensor titd ON titd.id = aa.defensor_id
     LEFT JOIN contrib_servidor tits ON tits.id = titd.servidor_id
     LEFT JOIN auth_user titu ON titu.id = tits.usuario_id
     LEFT JOIN defensor_defensor subd ON subd.id = aa.substituto_id
     LEFT JOIN contrib_servidor subs ON subs.id = subd.servidor_id
     LEFT JOIN auth_user subu ON subu.id = subs.usuario_id
     LEFT JOIN atendimento_cronometro cr ON cr.atendimento_id = aa.id
  WHERE aa.data_atendimento IS NULL AND recepcao.id IS NOT NULL AND cr.finalizado = false AND cr.termino >= recepcao.data_atendimento;""",
            reverse_sql=""
        ),
        migrations.RunSQL(
            sql="""CREATE OR REPLACE VIEW public.vw_atendimentos_dia_liberados AS 
 WITH cte_atendimentos AS (
         SELECT aa_1.id,
            aa_1.inicial_id,
            COALESCE(aa_1.inicial_id, aa_1.id) AS atendimento_id_inicial,
            aa_1.numero,
            aa_1.tipo,
            aa_1.data_agendamento,
            to_char(aa_1.data_agendamento, 'HH24:MI'::text) AS horario,
            aa_1.data_atendimento,
            to_char(aa_1.data_atendimento, 'HH24:MI'::text) AS horario_atendimento,
            aa_1.agenda_id,
            aa_1.ativo,
            aa_1.prazo,
            aa_1.prioridade,
            aa_1.qualificacao_id,
            ad.defensoria_id,
            ad.defensor_id,
            ad.substituto_id,
            aa_1.historico_recepcao
           FROM atendimento_defensor ad
             JOIN atendimento_atendimento aa_1 ON aa_1.id = ad.atendimento_ptr_id AND aa_1.data_agendamento >= 'now'::text::date AND aa_1.data_agendamento <= ('now'::text::date + '23:59:59.999'::interval) AND (aa_1.tipo = 1 OR aa_1.tipo = 2 OR aa_1.tipo = 4 OR aa_1.tipo = 9) AND aa_1.remarcado_id IS NULL AND aa_1.ativo = true
        ), cte_atividades AS (
         SELECT atividades_1.origem_id,
            count(atividades_1.origem_id) AS qtd
           FROM cte_atendimentos aa_1
             JOIN atendimento_atendimento atividades_1 ON aa_1.id = atividades_1.origem_id AND atividades_1.tipo = 10 AND atividades_1.ativo = true
          GROUP BY atividades_1.origem_id
        ), cte_requerentes AS (
         SELECT DISTINCT p1.id,
            a1.id AS pessoa_id,
            a1.nome,
            a1.nome_social,
            a1.apelido,
            a1.tipo,
            b1.pne,
            aa_1.atendimento_id_inicial AS atendimento_id
           FROM cte_atendimentos aa_1
             JOIN atendimento_pessoa p1 ON p1.atendimento_id = aa_1.atendimento_id_inicial AND p1.tipo = 0 AND p1.responsavel = true AND p1.ativo = true
             JOIN assistido_pessoa a1 ON a1.id = p1.pessoa_id
             JOIN assistido_pessoaassistida b1 ON b1.pessoa_ptr_id = p1.pessoa_id
        ), cte_requeridos AS (
         SELECT DISTINCT p2.id,
            a2.id AS pessoa_id,
            a2.nome,
            a2.nome_social,
            a2.apelido,
            a2.tipo,
            aa_1.atendimento_id_inicial AS atendimento_id
           FROM cte_atendimentos aa_1
             JOIN atendimento_pessoa p2 ON p2.atendimento_id = aa_1.atendimento_id_inicial AND p2.tipo = 1 AND p2.responsavel = true AND p2.ativo = true
             JOIN assistido_pessoa a2 ON a2.id = p2.pessoa_id
        )
 SELECT aa.id AS atendimento_ptr_id,
    aa.numero,
    aa.inicial_id,
    aa.tipo,
    recepcao.id AS recepcao_id,
    btrim(aa.historico_recepcao) AS historico_recepcao,
    requerente.id AS requerente_id,
    requerente.pessoa_id AS requerente_pessoa_id,
    requerente.nome AS requerente_nome,
    requerente.nome_social AS requerente_nome_social,
    requerente.pne AS requerente_pne,
    requerente.apelido AS requerente_apelido,
    requerente.tipo AS requerente_tipo,
    requerido.id AS requerido_id,
    requerido.pessoa_id AS requerido_pessoa_id,
    requerido.nome AS requerido_nome,
    requerido.nome_social AS requerido_nome_social,
    requerido.apelido AS requerido_apelido,
    requerido.tipo AS requerido_tipo,
    ca.nome AS area_nome,
    aq.titulo AS qualificacao_titulo,
    cd.nome AS defensoria_nome,
    cd.codigo AS defensoria_codigo,
    tits.nome AS defensor_nome,
    titu.username AS defensor_username,
    subs.nome AS substituto_nome,
    subu.username AS substituto_username,
    aa.data_agendamento,
    aa.data_atendimento,
        CASE
            WHEN aa.data_atendimento IS NOT NULL THEN 1
            ELSE 0
        END AS historico_atendimento,
    aa.horario,
    aa.horario_atendimento,
    recepcao.data_atendimento AS data_atendimento_recepcao,
    to_char(recepcao.data_atendimento, 'HH24:MI'::text) AS horario_atendimento_recepcao,
    aa.agenda_id,
    cd.comarca_id,
    cd.predio_id,
    aa.ativo,
    aa.prazo,
    aa.prioridade,
    COALESCE(atividades.qtd, 0::bigint) AS atividades,
        CASE
            WHEN aa.horario = '00:00'::text THEN 1
            ELSE 0
        END AS extrapauta
   FROM cte_atendimentos aa
     LEFT JOIN cte_atividades atividades ON aa.id = atividades.origem_id
     LEFT JOIN atendimento_atendimento recepcao ON recepcao.origem_id = aa.id AND recepcao.tipo = 3 AND recepcao.ativo = true
     LEFT JOIN atendimento_qualificacao aq ON aq.id = aa.qualificacao_id
     LEFT JOIN contrib_area ca ON ca.id = aq.area_id
     LEFT JOIN contrib_defensoria cd ON cd.id = aa.defensoria_id
     LEFT JOIN cte_requerentes requerente ON requerente.atendimento_id = aa.atendimento_id_inicial
     LEFT JOIN cte_requeridos requerido ON requerido.atendimento_id = aa.atendimento_id_inicial
     LEFT JOIN defensor_defensor titd ON titd.id = aa.defensor_id
     LEFT JOIN contrib_servidor tits ON tits.id = titd.servidor_id
     LEFT JOIN auth_user titu ON titu.id = tits.usuario_id
     LEFT JOIN defensor_defensor subd ON subd.id = aa.substituto_id
     LEFT JOIN contrib_servidor subs ON subs.id = subd.servidor_id
     LEFT JOIN auth_user subu ON subu.id = subs.usuario_id
     LEFT JOIN atendimento_cronometro cr ON cr.atendimento_id = aa.id AND cr.termino >= recepcao.data_atendimento
  WHERE aa.data_atendimento IS NULL AND recepcao.id IS NOT NULL AND cr.id IS NULL;""",
            reverse_sql=""
        )
    ]
