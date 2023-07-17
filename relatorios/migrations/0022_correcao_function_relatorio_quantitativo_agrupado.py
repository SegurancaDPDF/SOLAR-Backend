# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('relatorios', '0021_correcao_function_relatorio_quantitativo_agrupado'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION public.buscar_quantitativo_atendimento_geral(
              IN p_ano integer DEFAULT 2017,
              IN p_area_id integer DEFAULT 0,
              IN p_comarca_id integer DEFAULT '-1'::integer,
              IN p_defensor_id integer DEFAULT 0,
              IN p_diretoria_id integer DEFAULT '-1'::integer,
              IN p_defensoria_id integer DEFAULT 0)
            RETURNS TABLE(tipo smallint, tipo_nome character varying, comarca_id integer, area_id integer, defensor_id integer, coordenadoria_id integer, defensoria_id integer, ano smallint, mes smallint, mes_abreviacao character varying, qtd bigint) AS
              $BODY$
                    WITH
                    cte_mes AS (
                        SELECT CAST(1 AS SMALLINT) id, CAST('JAN' AS VARCHAR) mes_abreviacao
                        UNION ALL
                        SELECT 2,'FEV'
                        UNION ALL
                        SELECT 3,'MAR'
                        UNION ALL
                        SELECT 4,'ABR'
                        UNION ALL
                        SELECT 5,'MAI'
                        UNION ALL
                        SELECT 6,'JUN'
                        UNION ALL
                        SELECT 7,'JUL'
                        UNION ALL
                        SELECT 8,'AGO'
                        UNION ALL
                        SELECT 9,'SET'
                        UNION ALL
                        SELECT 10, 'OUT'
                        UNION ALL
                        SELECT 11, 'NOV'
                        UNION ALL
                        SELECT 12, 'DEZ'
                    )
                    , cte_tipo AS (
                      SELECT CAST(1 AS SMALLINT) AS id, CAST('Inicial' AS VARCHAR) AS nome
                      UNION ALL
                      SELECT 2, 'Retorno'
                      UNION ALL
                      SELECT 4, 'Apoio'
                      UNION ALL
                      SELECT 7, 'Visita ao Preso'
                      UNION ALL
                      SELECT 9, 'Encaminhamento'
                    )
                    , cte_cross AS (
                    SELECT mes.id AS mes_id, mes.mes_abreviacao, tipo.id AS tipo_id, tipo.nome AS tipo_nome
                    FROM cte_mes mes
                    CROSS JOIN cte_tipo tipo
                    )
                    --select * From cte_cross
                    , cte_atendimento AS (
                        SELECT
                        aa.tipo
                        , com.id AS comarca_id
                        , aq.area_id AS area_id
                        , COALESCE(ad.substituto_id, ad.defensor_id) AS defensor_id
                        , com.coordenadoria_id
                        , def.id AS defensoria_id
                        , CAST(date_part('year', aa.data_atendimento) AS SMALLINT) ano
                        , CAST(date_part('month', aa.data_atendimento) AS SMALLINT) mes
                        , COUNT(aa.id) AS qtd
                        FROM atendimento_defensor ad
                        INNER JOIN atendimento_atendimento aa ON aa.id = ad.atendimento_ptr_id
                            AND aa.ativo = TRUE
                            AND aa.remarcado_id IS NULL
                            AND aa.tipo IN (1,2,4,7,9)
                            AND date_part('year', aa.data_atendimento) = p_ano
                            AND (
                                (0 = p_defensor_id)
                                OR (
                                  (ad.substituto_id IS NULL AND ad.defensor_id = p_defensor_id)
                                  OR (ad.substituto_id = p_defensor_id)
                                )
                            )
                        INNER JOIN atendimento_qualificacao aq ON aq.id = aa.qualificacao_id
                          AND (aq.area_id = p_area_id OR p_area_id = 0)
                        INNER JOIN contrib_defensoria def ON def.id = ad.defensoria_id
                            AND (def.id = p_defensoria_id OR p_defensoria_id = 0)
                            AND (def.comarca_id = p_comarca_id OR p_comarca_id = -1)
                        INNER JOIN contrib_comarca com ON com.id = ad.comarca_id
                            AND (com.coordenadoria_id = p_diretoria_id
                                 OR com.id = p_diretoria_id
                                 OR p_diretoria_id = -1)
                        LEFT JOIN atendimento_atendimento aa_nucleo ON aa_nucleo.origem_id = ad.atendimento_ptr_id
                            AND aa_nucleo.tipo = 4
                        WHERE aa_nucleo.origem_id IS NULL
                        GROUP BY aa.tipo
                        ,com.id
                        , aq.area_id
                        , ad.defensor_id
                        , ad.substituto_id
                        , com.coordenadoria_id, def.id, ano, mes
                    )
                     SELECT
                     CAST(crosss.tipo_id AS SMALLINT),
                     crosss.tipo_nome,
                       comarca_id,
                       area_id,
                       defensor_id,
                       coordenadoria_id,
                       defensoria_id,
                       ano,
                       CAST(crosss.mes_id AS SMALLINT) mes,
                       crosss.mes_abreviacao,
                       qtd
                     FROM cte_atendimento a
                     FULL JOIN cte_cross crosss ON crosss.mes_id = a.mes
                        AND crosss.tipo_id = a.tipo
              $BODY$
              LANGUAGE sql IMMUTABLE
              COST 100
              ROWS 1000;
            """,
            reverse_sql="""
                CREATE OR REPLACE FUNCTION public.buscar_quantitativo_atendimento_geral(
              IN p_ano integer DEFAULT 2017,
              IN p_area_id integer DEFAULT 0,
              IN p_comarca_id integer DEFAULT '-1'::integer,
              IN p_defensor_id integer DEFAULT 0,
              IN p_diretoria_id integer DEFAULT '-1'::integer,
              IN p_defensoria_id integer DEFAULT 0)
            RETURNS TABLE(tipo smallint, tipo_nome character varying, comarca_id integer, area_id integer, defensor_id integer, coordenadoria_id integer, defensoria_id integer, ano smallint, mes smallint, mes_abreviacao character varying, qtd bigint) AS
              $BODY$
                    WITH
                    cte_mes AS (
                        SELECT CAST(1 AS SMALLINT) id, CAST('JAN' AS VARCHAR) mes_abreviacao
                        UNION ALL
                        SELECT 2,'FEV'
                        UNION ALL
                        SELECT 3,'MAR'
                        UNION ALL
                        SELECT 4,'ABR'
                        UNION ALL
                        SELECT 5,'MAI'
                        UNION ALL
                        SELECT 6,'JUN'
                        UNION ALL
                        SELECT 7,'JUL'
                        UNION ALL
                        SELECT 8,'AGO'
                        UNION ALL
                        SELECT 9,'SET'
                        UNION ALL
                        SELECT 10, 'OUT'
                        UNION ALL
                        SELECT 11, 'NOV'
                        UNION ALL
                        SELECT 12, 'DEZ'
                    )
                    , cte_tipo AS (
                      SELECT CAST(1 AS SMALLINT) AS id, CAST('Inicial' AS VARCHAR) AS nome
                      UNION ALL
                      SELECT 2, 'Retorno'
                      UNION ALL
                      SELECT 4, 'Apoio'
                      UNION ALL
                      SELECT 7, 'Visita ao Preso'
                      UNION ALL
                      SELECT 9, 'Encaminhamento'
                    )
                    , cte_cross AS (
                    SELECT mes.id AS mes_id, mes.mes_abreviacao, tipo.id AS tipo_id, tipo.nome AS tipo_nome
                    FROM cte_mes mes
                    CROSS JOIN cte_tipo tipo
                    )
                    --select * From cte_cross
                    , cte_atendimento AS (
                        SELECT
                        aa.tipo
                        , com.id AS comarca_id
                        , aq.area_id AS area_id
                        , COALESCE(ad.substituto_id, ad.defensor_id) AS defensor_id
                        , com.coordenadoria_id
                        , def.id AS defensoria_id
                        , CAST(date_part('year', aa.data_atendimento) AS SMALLINT) ano
                        , CAST(date_part('month', aa.data_atendimento) AS SMALLINT) mes
                        , COUNT(aa.id) AS qtd
                        FROM atendimento_defensor ad
                        INNER JOIN atendimento_atendimento aa ON aa.id = ad.atendimento_ptr_id
                            AND aa.ativo = TRUE
                            AND aa.remarcado_id IS NULL
                            AND aa.tipo IN (1,2,4,7,9)
                            AND date_part('year', aa.data_atendimento) = p_ano
                            AND (
                                (0 = p_defensor_id)
                                OR (
                                  (ad.substituto_id IS NULL AND ad.defensor_id = p_defensor_id)
                                  OR (ad.substituto_id = p_defensor_id)
                                )
                            )
                        INNER JOIN atendimento_qualificacao aq ON aq.id = aa.qualificacao_id
                          AND (aq.area_id = p_area_id OR p_area_id = 0)
                        INNER JOIN contrib_defensoria def ON def.id = ad.defensoria_id
                            AND (def.id = p_defensoria_id OR p_defensoria_id = 0)
                            AND (def.comarca_id = p_comarca_id OR p_comarca_id = -1)
                        INNER JOIN contrib_comarca com ON com.id = def.comarca_id
                            AND (com.coordenadoria_id = p_diretoria_id
                                 OR com.id = p_diretoria_id
                                 OR p_diretoria_id = -1)
                        LEFT JOIN atendimento_atendimento aa_nucleo ON aa_nucleo.origem_id = ad.atendimento_ptr_id
                            AND aa_nucleo.tipo = 4
                        WHERE aa_nucleo.origem_id IS NULL
                        GROUP BY aa.tipo
                        ,com.id
                        , aq.area_id
                        , ad.defensor_id
                        , ad.substituto_id
                        , com.coordenadoria_id, def.id, ano, mes
                    )
                     SELECT
                     CAST(crosss.tipo_id AS SMALLINT),
                     crosss.tipo_nome,
                       comarca_id,
                       area_id,
                       defensor_id,
                       coordenadoria_id,
                       defensoria_id,
                       ano,
                       CAST(crosss.mes_id AS SMALLINT) mes,
                       crosss.mes_abreviacao,
                       qtd
                     FROM cte_atendimento a
                     FULL JOIN cte_cross crosss ON crosss.mes_id = a.mes
                        AND crosss.tipo_id = a.tipo
              $BODY$
              LANGUAGE sql IMMUTABLE
              COST 100
              ROWS 1000;
            """
        )
    ]
