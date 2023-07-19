# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('relatorios', '0025_permissao_atividades_indenizatorias'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE FUNCTION public.buscar_quantitativo_agendamento_geral(
                    p_ano integer DEFAULT 2019,
                    p_area_id integer DEFAULT 0,
                    p_comarca_id integer DEFAULT '-1'::integer,
                    p_defensor_id integer DEFAULT 0,
                    p_diretoria_id integer DEFAULT '-1'::integer,
                    p_defensoria_id integer DEFAULT 0)
                    RETURNS TABLE(tipo smallint, tipo_nome character varying, comarca_id integer, area_id integer, defensor_id integer, coordenadoria_id integer, defensoria_id integer, ano smallint, mes smallint, mes_abreviacao character varying, qtd bigint) 
                    LANGUAGE 'sql'
                    COST 100
                    IMMUTABLE 
                    ROWS 1000
                AS $BODY$
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
                                      -- UNION ALL
                                      -- SELECT 7, 'Visita ao Preso'
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
                                        , CAST(date_part('year', aa.data_agendamento) AS SMALLINT) ano
                                        , CAST(date_part('month', aa.data_agendamento) AS SMALLINT) mes
                                        , COUNT(aa.id) AS qtd
                                        FROM atendimento_defensor ad
                                        INNER JOIN atendimento_atendimento aa ON aa.id = ad.atendimento_ptr_id
                                            AND aa.ativo = TRUE
                                            AND aa.remarcado_id IS NULL
                                            -- AND aa.data_atendimento IS NULL
                                            AND aa.tipo IN (1,2,4,9)
                                            AND date_part('year', aa.data_agendamento) = p_ano
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
                                        INNER JOIN contrib_comarca com ON com.id = def.comarca_id
                                             AND (-1 = p_comarca_id OR com.id = p_comarca_id)
                                        INNER JOIN contrib_comarca dir ON dir.id = CASE WHEN com.coordenadoria_id IS NULL THEN com.id ELSE com.coordenadoria_id END
                                            AND (-1 = p_diretoria_id OR dir.id = p_diretoria_id)
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
                              $BODY$;
                """,
            reverse_sql="""
                    DROP FUNCTION public.buscar_quantitativo_agendamento_geral(integer, integer, integer, integer, integer, integer);
                """
        ),
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE FUNCTION public.buscar_quantitativo_agendamento_geral_crosstab(
                    p_ano integer DEFAULT 2019,
                    p_area_id integer DEFAULT 0,
                    p_comarca_id integer DEFAULT '-1'::integer,
                    p_defensor_id integer DEFAULT 0,
                    p_diretoria_id integer DEFAULT '-1'::integer,
                    p_defensoria_id integer DEFAULT 0)
                    RETURNS TABLE(tipo_nome character varying, jan integer, fev integer, mar integer, abr integer, mai integer, jun integer, jul integer, ago integer, set integer, "out" integer, nov integer, dez integer) 
                    LANGUAGE 'plpgsql'
                    COST 100
                    IMMUTABLE STRICT 
                    ROWS 1000
                AS $BODY$
                        DECLARE consulta TEXT;
                        BEGIN
                          consulta := 'SELECT tipo_nome, mes, COALESCE(SUM(qtd), 0) AS qtd FROM public.buscar_quantitativo_agendamento_geral(' || p_ano || ', ' || p_area_id || ', ' || p_comarca_id || ', ' || p_defensor_id || ', ' || p_diretoria_id || ',' || p_defensoria_id || ')'
                          || ' GROUP BY tipo, tipo_nome, mes ORDER BY tipo';
                          RETURN QUERY SELECT * FROM crosstab(consulta , 'SELECT * FROM generate_series(1, 12)') 
                            AS ct (consulta VARCHAR, "Jan" INTEGER, "Fev" INTEGER, "Mar" INTEGER, "Abr" INTEGER, "Mai" INTEGER, "Jun" INTEGER, "Jul" INTEGER, "Ago" INTEGER, "Set" INTEGER, "Out" INTEGER, "Nov" INTEGER, "Dez" INTEGER);
                        END;
                    $BODY$;
            """,
            reverse_sql="""
                DROP FUNCTION public.buscar_quantitativo_agendamento_geral_crosstab(integer, integer, integer, integer, integer, integer);
            """
        )
    ]
