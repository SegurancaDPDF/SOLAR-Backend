# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0087_multiplicador_atendimento'),
    ]

    operations = [
        migrations.RunSQL(
            reverse_sql="""DROP FUNCTION public.buscar_quantitativo_agendamento_atendimento(
            integer, timestamp without time zone, timestamp without time zone, integer, integer, integer, integer, integer);""",  # noga
            sql="""
CREATE OR REPLACE FUNCTION public.buscar_quantitativo_agendamento_atendimento(
	p_tipo_relatorio integer DEFAULT 0,
	p_data_inicial timestamp without time zone DEFAULT '2020-01-01 00:00:00'::timestamp without time zone,
	p_data_final timestamp without time zone DEFAULT '2020-12-31 23:59:59'::timestamp without time zone,
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
                      UNION ALL
                      SELECT aux.* FROM (SELECT 7, 'Visita ao Preso') AS aux WHERE p_tipo_relatorio = 2
                      UNION ALL
                      SELECT 9, 'Encaminhamento'
                    )
                    , cte_cross AS (
                    SELECT mes.id AS mes_id, mes.mes_abreviacao, tipo.id AS tipo_id, tipo.nome AS tipo_nome
                    FROM cte_mes mes
                    CROSS JOIN cte_tipo tipo
                    )
                    , cte_atendimento AS (
                        SELECT
                        aa.tipo
                        , com.id AS comarca_id
                        , aq.area_id AS area_id
                        , COALESCE(ad.substituto_id, ad.defensor_id) AS defensor_id
                        , com.coordenadoria_id
                        , def.id AS defensoria_id
						, CASE 
							WHEN p_tipo_relatorio = 0 AND aa.tipo != 7 THEN CAST(date_part('year', aa.data_agendamento) AS SMALLINT)
							WHEN p_tipo_relatorio = 0 AND aa.tipo = 7 THEN CAST(date_part('year', aa.data_atendimento) AS SMALLINT)
							WHEN p_tipo_relatorio = 1 THEN CAST(date_part('year', aa.data_agendamento) AS SMALLINT)	
							WHEN p_tipo_relatorio = 2 THEN CAST(date_part('year', aa.data_atendimento) AS SMALLINT)
						END AS ano
						, CASE 
							WHEN p_tipo_relatorio = 0 AND aa.tipo != 7 THEN CAST(date_part('month', aa.data_agendamento) AS SMALLINT)
							WHEN p_tipo_relatorio = 0 AND aa.tipo = 7 THEN CAST(date_part('month', aa.data_atendimento) AS SMALLINT)
							WHEN p_tipo_relatorio = 1 THEN CAST(date_part('month', aa.data_agendamento) AS SMALLINT)	
							WHEN p_tipo_relatorio = 2 THEN CAST(date_part('month', aa.data_atendimento) AS SMALLINT)
						END AS mes
                        , COUNT(aa.id) AS qtd
                        FROM atendimento_defensor ad
                        INNER JOIN atendimento_atendimento aa ON aa.id = ad.atendimento_ptr_id
                            AND aa.ativo = TRUE
                            AND aa.remarcado_id IS NULL
                            AND aa.tipo IN (1,2,4,7,9)
							AND (
									(p_tipo_relatorio = 0 AND
									 	(
											(aa.tipo != 7 
												AND aa.data_agendamento BETWEEN p_data_inicial::timestamp AND p_data_final::timestamp
											) /*OR
											(aa.tipo = 7 -- visita ao preso não tem data_agendamento
												AND aa.data_atendimento BETWEEN p_data_inicial::timestamp AND p_data_final::timestamp
											)*/
										)
										
									) OR
									(p_tipo_relatorio = 1
									 	AND aa.data_atendimento IS NULL
										AND aa.data_agendamento BETWEEN p_data_inicial::timestamp AND p_data_final::timestamp
									) OR
									(p_tipo_relatorio = 2
										AND aa.data_atendimento BETWEEN p_data_inicial::timestamp AND p_data_final::timestamp
									)
							)
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
                        INNER JOIN contrib_comarca com ON com.id = ad.comarca_id
							AND (com.id = p_comarca_id OR p_comarca_id = -1)
						INNER JOIN contrib_comarca dir ON dir.id = COALESCE(com.coordenadoria_id, com.id)
							AND (-1 = p_diretoria_id OR dir.id = p_diretoria_id)
                        LEFT JOIN atendimento_atendimento aa_nucleo ON aa_nucleo.origem_id = ad.atendimento_ptr_id
                            AND p_tipo_relatorio = 2
							AND aa_nucleo.tipo = 4
                        WHERE -- p_tipo_relatorio != 2
						-- OR (
							-- p_tipo_relatorio = 2 AND
							aa_nucleo.origem_id IS NULL
						-- ) 
                        GROUP BY aa.tipo
                        ,com.id
                        , aq.area_id
                        , ad.defensor_id
                        , ad.substituto_id
                        , com.coordenadoria_id, 
						def.id, 
						ano, 
						mes
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
                     FULL JOIN cte_cross crosss ON crosss.tipo_id = a.tipo
					 	AND crosss.mes_id = a.mes
              $BODY$;
        """),

        migrations.RunSQL(
            reverse_sql="""DROP FUNCTION public.buscar_quantitativo_agendamento_atendimento_crosstab(
integer, timestamp without time zone, timestamp without time zone, integer, integer, integer, integer, integer);""",  # noga
            sql="""
            CREATE OR REPLACE FUNCTION public.buscar_quantitativo_agendamento_atendimento_crosstab(
	p_tipo_relatorio integer DEFAULT 0,
	p_data_inicial timestamp without time zone DEFAULT '2020-01-01 00:00:00'::timestamp without time zone,
	p_data_final timestamp without time zone DEFAULT '2020-12-31 23:59:59'::timestamp without time zone,
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
	  consulta := 'SELECT tipo_nome, mes, COALESCE(SUM(qtd), 0) AS qtd FROM public.buscar_quantitativo_agendamento_atendimento(' || p_tipo_relatorio || ', ''' || p_data_inicial || '''::timestamp, ''' || p_data_final  || '''::timestamp, ' || p_area_id || ', ' || p_comarca_id || ', ' || p_defensor_id || ', ' || p_diretoria_id || ',' || p_defensoria_id || ')'
	  || ' GROUP BY tipo, tipo_nome, mes ORDER BY tipo';
	  RETURN QUERY SELECT * FROM crosstab(consulta , 'SELECT * FROM generate_series(1, 12)') 
		AS ct (consulta VARCHAR, "Jan" INTEGER, "Fev" INTEGER, "Mar" INTEGER, "Abr" INTEGER, "Mai" INTEGER, "Jun" INTEGER, "Jul" INTEGER, "Ago" INTEGER, "Set" INTEGER, "Out" INTEGER, "Nov" INTEGER, "Dez" INTEGER);
	END;
$BODY$;
            """
        )
    ]
