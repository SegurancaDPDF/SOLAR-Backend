# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0088_functions_relatorios_atendimento_agendamento'),
    ]

    operations = [
        migrations.RunSQL(
            reverse_sql="""DROP FUNCTION public.buscar_quantitativo_atividades_acoes_extrajudiciais(
            timestamp without time zone, timestamp without time zone, integer, integer, integer, integer, integer);""",
            sql="""CREATE OR REPLACE FUNCTION public.buscar_quantitativo_atividades_acoes_extrajudiciais(
                p_data_inicial timestamp without time zone DEFAULT '2020-01-01 00:00:00'::timestamp without time zone,
                p_data_final timestamp without time zone DEFAULT '2020-12-31 23:59:59'::timestamp without time zone,
                p_defensor_id integer DEFAULT 0,
                p_defensoria_id integer DEFAULT 0,
                p_area_id integer DEFAULT 0,
                p_comarca_id integer DEFAULT '-1'::integer,
                p_diretoria_id integer DEFAULT '-1'::integer)
                RETURNS TABLE(
                  defensor_id integer,
                  defensoria_id integer,
                  area_id integer,
                  comarca_id integer,
                  coordenadoria_id integer,
                  ano smallint,
                  mes smallint,
                  qtd bigint
                ) 
                LANGUAGE 'sql'
            
                COST 100
                IMMUTABLE 
                ROWS 1000
            AS $BODY$
            
                SELECT
                ppa.defensor_id
                , ad.defensoria_id
                , pp.area_id
                , com.id AS comarca_id
                , dir.id AS coordenadoria_id
                , CAST(date_part('year', ppa.data_cadastro) AS SMALLINT) ano 
                , CAST(date_part('month', ppa.data_cadastro) AS SMALLINT) mes
                , COUNT(ppa.id) AS qtd
                FROM processo_parte ppa
                INNER JOIN processo_processo pp ON pp.id = ppa.processo_id
                    AND pp.ativo = TRUE
                    AND ppa.ativo = TRUE
                    AND pp.tipo = 0
                    AND pp.area_id IS NOT NULL
                    AND ppa.data_cadastro BETWEEN p_data_inicial::timestamp AND p_data_final::timestamp
                    AND (0 = p_area_id OR pp.area_id = p_area_id)
                    AND (0 = p_defensor_id OR ppa.defensor_id = p_defensor_id)
                INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                    AND (-1 = p_comarca_id OR pp.comarca_id = p_comarca_id)
                INNER JOIN contrib_comarca dir ON dir.id = COALESCE(com.coordenadoria_id, com.id)
                    AND (-1 = p_diretoria_id OR dir.id = p_diretoria_id)
                INNER JOIN atendimento_defensor ad ON ad.atendimento_ptr_id = ppa.atendimento_id
                    AND (0 = p_defensoria_id OR ad.defensoria_id = p_defensoria_id)
                
                GROUP BY ppa.defensor_id, ad.defensoria_id, pp.area_id, com.id, dir.id, ano, mes
        $BODY$;"""),
        migrations.RunSQL(
            reverse_sql="""DROP FUNCTION public.buscar_quantitativo_atividades_acoes_judiciais_designadas(
            timestamp without time zone, timestamp without time zone, integer, integer, integer, integer, integer);""",
            sql="""CREATE OR REPLACE FUNCTION public.buscar_quantitativo_atividades_acoes_judiciais_designadas(
                p_data_inicial timestamp without time zone DEFAULT '2020-01-01 00:00:00'::timestamp without time zone,
                p_data_final timestamp without time zone DEFAULT '2020-12-31 23:59:59'::timestamp without time zone,
                p_defensor_id integer DEFAULT 0,
                p_defensoria_id integer DEFAULT 0,
                p_area_id integer DEFAULT 0,
                p_comarca_id integer DEFAULT '-1'::integer,
                p_diretoria_id integer DEFAULT '-1'::integer)
                RETURNS TABLE(
                  defensor_id integer, 
                  defensoria_id integer, 
                  area_id integer, 
                  comarca_id integer, 
                  coordenadoria_id integer, 
                  ano smallint, 
                  mes smallint, 
                  qtd bigint
                ) 
                LANGUAGE 'sql'
            
                COST 100
                IMMUTABLE 
                ROWS 1000
            AS $BODY$
            
                SELECT
                    CASE
                        WHEN ppa.data_cadastro::date < '2015-04-01'::date THEN ppa.defensor_id
                        ELSE ppa.defensor_cadastro_id
                    END AS defensor_id
                    , 0 --ad.defensoria_id
                    , pp.area_id
                    , com.id AS comarca_id
                    , dir.id AS coordenadoria_id
                    , CAST(date_part('year', ppa.data_cadastro) AS SMALLINT) ano 
                    , CAST(date_part('month', ppa.data_cadastro) AS SMALLINT) mes
                    , COUNT(ppa.id) AS qtd
                    FROM processo_parte ppa
                    INNER JOIN processo_processo pp ON pp.id = ppa.processo_id
                        AND pp.area_id IS NOT NULL
                        AND (0 = p_area_id OR pp.area_id = p_area_id)
                        AND pp.tipo != 0
                        AND ppa.ativo = TRUE
                        AND pp.ativo = TRUE
                        AND ppa.data_cadastro BETWEEN p_data_inicial::timestamp AND p_data_final::timestamp
                    INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                        AND (-1 = p_comarca_id OR com.id = p_comarca_id)
                    INNER JOIN contrib_comarca dir ON dir.id = COALESCE(com.coordenadoria_id, com.id)
                        AND (-1 = p_diretoria_id OR dir.id = p_diretoria_id)
                    /*INNER JOIN atendimento_defensor ad ON ad.atendimento_ptr_id = ppa.atendimento_id
                        AND (p_defensoria_id = 0 OR ad.defensoria_id = p_defensoria_id)*/
                    LEFT JOIN processo_fase ini ON ini.id = pp.peticao_inicial_id
                    
                    WHERE
                        (
                            (
                                ppa.data_cadastro < '2015-04-01 00:00:00'
                                AND ppa.defensor_id IS NOT NULL
                                AND (0 = p_defensor_id OR ppa.defensor_id = p_defensor_id) 
                            )
                            OR
                            (
                                ppa.data_cadastro >= '2015-04-01 00:00:00'
                                AND ppa.defensor_cadastro_id IS NOT NULL
                                AND (0 = p_defensor_id OR ppa.defensor_cadastro_id = p_defensor_id) 
                            )
                        )
                        AND (pp.peticao_inicial_id IS NULL OR (ppa.defensor_cadastro_id != ini.defensor_cadastro_id AND ini.defensor_cadastro_id IS NOT NULL))
                    GROUP BY CASE
                        WHEN ppa.data_cadastro::date < '2015-04-01'::date THEN ppa.defensor_id
                        ELSE ppa.defensor_cadastro_id
                    END,
                    /*ad.defensoria_id,*/ pp.area_id, com.id, dir.id,ano, mes;
            $BODY$;"""),
        migrations.RunSQL(
            reverse_sql="""DROP FUNCTION public.buscar_quantitativo_atividades_acoes_judiciais_protocoladas(
            timestamp without time zone, timestamp without time zone, integer, integer, integer, integer, integer);""",
            sql="""CREATE OR REPLACE FUNCTION public.buscar_quantitativo_atividades_acoes_judiciais_protocoladas(
                p_data_inicial timestamp without time zone DEFAULT '2020-01-01 00:00:00'::timestamp without time zone,
                p_data_final timestamp without time zone DEFAULT '2020-12-31 23:59:59'::timestamp without time zone,
                p_defensor_id integer DEFAULT 0,
                p_defensoria_id integer DEFAULT 0,
                p_area_id integer DEFAULT 0,
                p_comarca_id integer DEFAULT '-1'::integer,
                p_diretoria_id integer DEFAULT '-1'::integer)
                RETURNS TABLE(
                  defensor_id integer, 
                  defensoria_id integer, 
                  area_id integer, 
                  comarca_id integer, 
                  coordenadoria_id integer, 
                  ano smallint, 
                  mes smallint, 
                  qtd bigint
                ) 
                LANGUAGE 'sql'
            
                COST 100
                IMMUTABLE 
                ROWS 1000
            AS $BODY$
            
                SELECT
                ini.defensor_cadastro_id AS defensor_id
                , 0 --ad.defensoria_id
                , pp.area_id
                , com.id AS comarca_id
                , dir.id AS coordenadoria_id
                , CAST(date_part('year', ini.data_cadastro) AS SMALLINT) ano 
                , CAST(date_part('month', ini.data_cadastro) AS SMALLINT) mes
                , COUNT(distinct(pp.id)) AS qtd
                FROM processo_parte ppa
                INNER JOIN processo_processo pp ON pp.id = ppa.processo_id
                    AND pp.ativo = TRUE
                    AND pp.tipo != 0
                    AND pp.area_id IS NOT NULL
                    AND ppa.ativo = TRUE
                    AND (0 = p_area_id OR pp.area_id = p_area_id)
                    --AND pp.area_id = 1
                INNER JOIN processo_fase ini ON ini.id = pp.peticao_inicial_id
                    AND ini.ativo = TRUE
                    AND ini.defensor_cadastro_id IS NOT NULL				 
                INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                    AND (-1 = p_comarca_id OR pp.comarca_id = p_comarca_id)
                    --AND pp.comarca_id = 2
                INNER JOIN contrib_comarca dir ON dir.id = COALESCE(com.coordenadoria_id, com.id)
                    AND (-1 = p_diretoria_id OR dir.id = p_diretoria_id)
                /*INNER JOIN atendimento_defensor ad ON ad.atendimento_ptr_id = ppa.atendimento_id
                    AND (p_defensoria_id = 0 OR ad.defensoria_id = p_defensoria_id)*/		 
                WHERE
                    (0 = p_defensor_id OR ini.defensor_cadastro_id = p_defensor_id)
                    AND ini.data_cadastro BETWEEN p_data_inicial::timestamp AND p_data_final::timestamp
                    --ini.data_cadastro BETWEEN '2020-01-01'::timestamp AND '2020-12-31'::timestamp
                    AND (
                        date_part('year', ini.data_cadastro) = date_part('year', ini.data_protocolo) AND
                        date_part('month', ini.data_cadastro) = date_part('month', ini.data_protocolo)
                        )
                GROUP BY ini.defensor_cadastro_id, /*ad.defensoria_id,*/ pp.area_id, com.id, dir.id, ano, mes
            $BODY$;"""),
        migrations.RunSQL(
            reverse_sql="""DROP FUNCTION public.buscar_quantitativo_atividades_audiencias(
            timestamp without time zone, timestamp without time zone, integer, integer, integer, integer, integer);""",
            sql="""CREATE OR REPLACE FUNCTION public.buscar_quantitativo_atividades_audiencias(
                p_data_inicial timestamp without time zone DEFAULT '2020-01-01 00:00:00'::timestamp without time zone,
                p_data_final timestamp without time zone DEFAULT '2020-12-31 23:59:59'::timestamp without time zone,
                p_defensor_id integer DEFAULT 0,
                p_defensoria_id integer DEFAULT 0,
                p_area_id integer DEFAULT 0,
                p_comarca_id integer DEFAULT '-1'::integer,
                p_diretoria_id integer DEFAULT '-1'::integer)
                RETURNS TABLE(
                  defensor_id integer, 
                  defensoria_id integer, 
                  area_id integer, 
                  comarca_id integer, 
                  coordenadoria_id integer, 
                  ano smallint, 
                  mes smallint, 
                  qtd bigint
                ) 
                LANGUAGE 'sql'
            
                COST 100
                IMMUTABLE 
                ROWS 1000
            AS $BODY$
            
                SELECT
                COALESCE(pf.defensor_substituto_id, pf.defensor_cadastro_id) AS defensor_id
                , 0 --ad.defensoria_id
                , pp.area_id
                , com.id AS comarca_id
                , dir.id AS coordenadoria_id
                , CAST(date_part('year', pf.data_protocolo) AS SMALLINT) ano 
                , CAST(date_part('month', pf.data_protocolo) AS SMALLINT) mes
                , COUNT(DISTINCT(pa.fase_ptr_id)) AS qtd
                FROM processo_audiencia pa
                INNER JOIN processo_fase pf ON pf.id = pa.fase_ptr_id
                    AND pf.ativo = TRUE
                    AND pf.atividade = 1
                    AND pf.defensor_cadastro_id IS NOT NULL
                    AND pa.audiencia_realizada = TRUE
                    AND pf.data_protocolo BETWEEN p_data_inicial::timestamp AND p_data_final::timestamp
                    AND (
                        0 = p_defensor_id OR 
                        COALESCE(pf.defensor_substituto_id, pf.defensor_cadastro_id) = p_defensor_id
                    )
                INNER JOIN processo_processo pp ON pp.id = pf.processo_id
                    AND pp.ativo = TRUE
                    AND pp.area_id IS NOT NULL
                    AND (0 = p_area_id OR pp.area_id = p_area_id)
                INNER JOIN processo_parte ppa ON ppa.processo_id = pp.id
                    AND ppa.ativo = TRUE
                INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                    AND (-1 = p_comarca_id OR com.id = p_comarca_id)
                INNER JOIN contrib_comarca dir ON dir.id = COALESCE(com.coordenadoria_id, com.id)
                    AND (-1 = p_diretoria_id OR dir.id = p_diretoria_id)
                /*INNER JOIN atendimento_defensor ad ON ad.atendimento_ptr_id = ppa.atendimento_id
                    AND (
                        ad.defensor_id = ppa.defensor_cadastro_id 
                        OR ad.defensor_id = ppa.defensor_id
                        --OR ad.defensor_id = COALESCE(pf.defensor_substituto_id, pf.defensor_cadastro_id)
                    )
                    AND (0 = p_defensoria_id OR ad.defensoria_id = p_defensoria_id)	
                */
                WHERE
                    data_baixa IS NULL 
                    OR (data_baixa::date <= (data_protocolo::date - interval '1 day' * (date_part('day', data_protocolo)-5)) + interval '1 month')
                GROUP BY COALESCE(pf.defensor_substituto_id, pf.defensor_cadastro_id), /*ad.defensoria_id,*/ pp.area_id, com.id, dir.id, ano, mes;
            $BODY$;"""),
        migrations.RunSQL(
            reverse_sql="""DROP FUNCTION public.buscar_quantitativo_atividades_demais_fases_processuais(
            timestamp without time zone, timestamp without time zone, integer, integer, integer, integer, integer);""",
            sql="""CREATE OR REPLACE FUNCTION public.buscar_quantitativo_atividades_demais_fases_processuais(
                p_data_inicial timestamp without time zone DEFAULT '2020-01-01 00:00:00'::timestamp without time zone,
                p_data_final timestamp without time zone DEFAULT '2020-12-31 23:59:59'::timestamp without time zone,
                p_defensor_id integer DEFAULT 0,
                p_defensoria_id integer DEFAULT 0,
                p_area_id integer DEFAULT 0,
                p_comarca_id integer DEFAULT '-1'::integer,
                p_diretoria_id integer DEFAULT '-1'::integer)
                RETURNS TABLE(
                  defensor_id integer, 
                  defensoria_id integer, 
                  area_id integer, 
                  comarca_id integer, 
                  coordenadoria_id integer, 
                  ano smallint, 
                  mes smallint, 
                  qtd bigint
                ) 
                LANGUAGE 'sql'
            
                COST 100
                IMMUTABLE 
                ROWS 1000
            AS $BODY$
            
                SELECT
                COALESCE(pf.defensor_substituto_id, pf.defensor_cadastro_id) AS defensor_id
                , 0 -- ad.defensoria_id
                , pp.area_id
                , com.id AS comarca_id
                , dir.id AS coordenadoria_id
                , CAST(date_part('year', pf.data_cadastro) AS SMALLINT) ano 
                , CAST(date_part('month', pf.data_cadastro) AS SMALLINT) mes
                , COUNT(distinct(pf.id)) AS qtd
                FROM processo_fase pf
                INNER JOIN processo_processo pp ON pp.id = pf.processo_id
                    AND pf.data_protocolo BETWEEN p_data_inicial::timestamp AND p_data_final::timestamp
                    AND pf.ativo = TRUE
                    AND pf.atividade = 0
                    AND pp.area_id IS NOT NULL
                    AND pf.defensor_cadastro_id IS NOT NULL
                    AND pp.ativo = TRUE
                    AND (0 = p_area_id OR pp.area_id = p_area_id)
                INNER JOIN processo_parte ppa ON ppa.processo_id = pp.id
                    AND ppa.ativo = TRUE
                INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                INNER JOIN contrib_comarca dir ON dir.id = COALESCE(com.coordenadoria_id, com.id)
                    AND (-1 = p_diretoria_id OR dir.id = p_diretoria_id)
                /*INNER JOIN atendimento_defensor ad ON ad.atendimento_ptr_id = ppa.atendimento_id
                    AND (0 = p_defensoria_id OR ad.defensoria_id = p_defensoria_id)	*/
                WHERE
                    (-1 = p_comarca_id OR pp.comarca_id = p_comarca_id)
                    AND (
                        0 = p_defensor_id OR 
                        COALESCE(pf.defensor_substituto_id, pf.defensor_cadastro_id) =  p_defensor_id
                    )
                    AND (
                            (
                                date_part('year', pf.data_cadastro) = date_part('year', pf.data_protocolo) AND
                                date_part('month', pf.data_cadastro) = date_part('month', pf.data_protocolo) 
                            ) 
                            OR 
                            (
                                date_part('year', pf.data_cadastro) = date_part('year', pf.data_protocolo) AND
                                date_part('month', pf.data_cadastro) = date_part('month', pf.data_protocolo) AND
                                ppa.data_cadastro >= '20190101' and 
                                ppa.data_cadastro <= pf.data_cadastro
                            )
                        )
                GROUP BY pf.defensor_substituto_id, pf.defensor_cadastro_id, /*ad.defensoria_id,*/ pp.area_id, com.id, dir.id, ano, mes;
            $BODY$;"""),
        migrations.RunSQL(
            reverse_sql="""DROP FUNCTION public.buscar_quantitativo_atividades_juris(
            timestamp without time zone, timestamp without time zone, integer, integer, integer, integer, integer);""",
            sql="""CREATE OR REPLACE FUNCTION public.buscar_quantitativo_atividades_juris(
                p_data_inicial timestamp without time zone DEFAULT '2020-01-01 00:00:00'::timestamp without time zone,
                p_data_final timestamp without time zone DEFAULT '2020-12-31 23:59:59'::timestamp without time zone,
                p_defensor_id integer DEFAULT 0,
                p_defensoria_id integer DEFAULT 0,
                p_area_id integer DEFAULT 0,
                p_comarca_id integer DEFAULT '-1'::integer,
                p_diretoria_id integer DEFAULT '-1'::integer)
                RETURNS TABLE(
                  defensor_id integer, 
                  defensoria_id integer, 
                  area_id integer, 
                  comarca_id integer, 
                  coordenadoria_id integer, 
                  ano smallint, 
                  mes smallint, 
                  qtd bigint
                ) 
                LANGUAGE 'sql'
            
                COST 100
                IMMUTABLE 
                ROWS 1000
            AS $BODY$
            
                SELECT
                COALESCE(pf.defensor_substituto_id, pf.defensor_cadastro_id) AS defensor_id
                , 0 --ad.defensoria_id
                , pp.area_id
                , com.id AS comarca_id
                , dir.id AS coordenadoria_id
                , CAST(date_part('year', pf.data_protocolo) AS SMALLINT) ano 
                , CAST(date_part('month', pf.data_protocolo) AS SMALLINT) mes
                , COUNT(distinct(pf.id)) AS qtd
                FROM processo_audiencia pa
                INNER JOIN processo_fase pf ON pf.id = pa.fase_ptr_id
                    AND pf.ativo = TRUE
                    AND pf.atividade = 2
                    AND pa.audiencia_realizada = TRUE
                    AND pf.defensor_cadastro_id IS NOT NULL
                INNER JOIN processo_processo pp ON pp.id = pf.processo_id
                    AND pp.ativo = TRUE
                    AND pp.area_id IS NOT NULL
                    AND (0 = p_area_id OR pp.area_id = p_area_id)
                INNER JOIN processo_parte ppa ON ppa.processo_id = pp.id
                    AND ppa.ativo = TRUE
                INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                INNER JOIN contrib_comarca dir ON dir.id = COALESCE(com.coordenadoria_id, com.id)
                    AND (-1 = p_diretoria_id OR dir.id = p_diretoria_id)
                /*INNER JOIN atendimento_defensor ad ON ad.atendimento_ptr_id = ppa.atendimento_id
                    AND (0 = p_defensoria_id OR ad.defensoria_id = p_defensoria_id)	*/
                WHERE
                    (
                        0 = p_defensor_id OR
                        COALESCE(pf.defensor_substituto_id, pf.defensor_cadastro_id) = p_defensor_id	
                    )
                    AND (-1 = p_comarca_id OR pp.comarca_id = p_comarca_id)
                    AND pf.data_protocolo BETWEEN p_data_inicial::timestamp AND p_data_final::timestamp
                                 
                    AND (data_baixa::date <= (data_protocolo::date - interval '1 day' * (date_part('day', data_protocolo)-5)) + interval '1 month' OR data_baixa IS NULL)
                GROUP BY pf.defensor_substituto_id, pf.defensor_cadastro_id, /*ad.defensoria_id,*/ pp.area_id, com.id, dir.id, ano, mes;
            $BODY$;"""),
        migrations.RunSQL(
            reverse_sql="""DROP FUNCTION public.buscar_quantitativo_atividades_recursos(
            timestamp without time zone, timestamp without time zone, integer, integer, integer, integer, integer);""",
            sql="""CREATE OR REPLACE FUNCTION public.buscar_quantitativo_atividades_recursos(
                p_data_inicial timestamp without time zone DEFAULT '2020-01-01 00:00:00'::timestamp without time zone,
                p_data_final timestamp without time zone DEFAULT '2020-12-31 23:59:59'::timestamp without time zone,
                p_defensor_id integer DEFAULT 0,
                p_defensoria_id integer DEFAULT 0,
                p_area_id integer DEFAULT 0,
                p_comarca_id integer DEFAULT '-1'::integer,
                p_diretoria_id integer DEFAULT '-1'::integer)
                RETURNS TABLE(
                  defensor_id integer, 
                  defensoria_id integer, 
                  area_id integer, 
                  comarca_id integer, 
                  coordenadoria_id integer, 
                  ano smallint, 
                  mes smallint, 
                  qtd bigint
                ) 
                LANGUAGE 'sql'
            
                COST 100
                IMMUTABLE 
                ROWS 1000
            AS $BODY$
            
                SELECT
                COALESCE(pf.defensor_substituto_id, pf.defensor_cadastro_id) AS defensor
                , 0 -- ad.defensoria_id
                , pp.area_id
                , com.id AS comarca_id
                , dir.id AS coordenadoria_id
                , CAST(date_part('year', pf.data_cadastro) AS SMALLINT) ano 
                , CAST(date_part('month', pf.data_cadastro) AS SMALLINT) mes
                , COUNT(distinct(pf.id)) AS qtd
                FROM processo_fase pf
                INNER JOIN processo_processo pp ON pp.id = pf.processo_id
                    AND pf.data_protocolo BETWEEN p_data_inicial::timestamp AND p_data_final::timestamp
                    AND pp.area_id IS NOT NULL
                    AND pf.defensor_cadastro_id IS NOT NULL
                    AND pf.ativo = TRUE
                    AND pf.atividade = 4
                    AND pp.ativo = TRUE
                    AND (0 = p_area_id OR pp.area_id = p_area_id)
                INNER JOIN processo_parte ppa ON ppa.processo_id = pp.id
                    AND ppa.ativo = TRUE
                INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                INNER JOIN contrib_comarca dir ON dir.id = COALESCE(com.coordenadoria_id, com.id)
                    AND (-1 = p_diretoria_id OR dir.id = p_diretoria_id)
                /*INNER JOIN atendimento_defensor ad ON ad.atendimento_ptr_id = ppa.atendimento_id
                    AND (0 = p_defensoria_id OR ad.defensoria_id = p_defensoria_id)*/	
                WHERE
                    (
                        0 = p_defensor_id OR 
                        COALESCE(pf.defensor_substituto_id, pf.defensor_cadastro_id) =  p_defensor_id
                    )
                AND (-1 = p_comarca_id OR pp.comarca_id = p_comarca_id)
                
                AND (
                    date_part('year', pf.data_cadastro) = date_part('year', pf.data_protocolo) AND
                    date_part('month', pf.data_cadastro) = date_part('month', pf.data_protocolo)
                    ) 
                GROUP BY pf.defensor_substituto_id, pf.defensor_cadastro_id, /*ad.defensoria_id,*/ pp.area_id, com.id, dir.id, ano, mes;
            $BODY$;"""),
        migrations.RunSQL(
            reverse_sql="""DROP FUNCTION public.buscar_quantitativo_atividades_sentencas(
            timestamp without time zone, timestamp without time zone, integer, integer, integer, integer, integer);""",
            sql="""
            CREATE OR REPLACE FUNCTION public.buscar_quantitativo_atividades_sentencas(
                p_data_inicial timestamp without time zone DEFAULT '2020-01-01 00:00:00'::timestamp without time zone,
                p_data_final timestamp without time zone DEFAULT '2020-12-31 23:59:59'::timestamp without time zone,
                p_defensor_id integer DEFAULT 0,
                p_defensoria_id integer DEFAULT 0,
                p_area_id integer DEFAULT 0,
                p_comarca_id integer DEFAULT '-1'::integer,
                p_diretoria_id integer DEFAULT '-1'::integer)
                RETURNS TABLE(
                  defensor_id integer, 
                  defensoria_id integer, 
                  area_id integer, 
                  comarca_id integer, 
                  coordenadoria_id integer, 
                  ano smallint, 
                  mes smallint, 
                  qtd bigint
                ) 
                LANGUAGE 'sql'
            
                COST 100
                IMMUTABLE 
                ROWS 1000
            AS $BODY$
            
                SELECT
                COALESCE(pf.defensor_substituto_id, pf.defensor_cadastro_id) AS defensor_id
                , 0 --ad.defensoria_id
                , pp.area_id
                , com.id AS comarca_id
                , dir.id AS diretoria_id
                , CAST(date_part('year', pf.data_cadastro) AS SMALLINT) ano 
                , CAST(date_part('month', pf.data_cadastro) AS SMALLINT) mes
                , COUNT(distinct(pf.id)) AS qtd
                FROM processo_fase pf
                INNER JOIN processo_processo pp ON pp.id = pf.processo_id
                    AND pp.area_id IS NOT NULL
                    AND pf.defensor_cadastro_id IS NOT NULL
                    AND pp.ativo = TRUE
                    AND pf.ativo = TRUE
                    AND pf.atividade = 3
                    AND pf.data_protocolo BETWEEN p_data_inicial::timestamp AND p_data_final::timestamp
                    AND (0 = p_area_id OR pp.area_id = p_area_id)
                INNER JOIN processo_parte ppa ON ppa.processo_id = pp.id
                    AND ppa.ativo = TRUE
                INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                    AND (-1 = p_comarca_id OR pp.comarca_id = p_comarca_id)
                INNER JOIN contrib_comarca dir ON dir.id = COALESCE(com.coordenadoria_id, com.id)
                    AND (-1 = p_diretoria_id OR dir.id = p_diretoria_id)
                /*INNER JOIN atendimento_defensor ad ON ad.atendimento_ptr_id = ppa.atendimento_id
                    AND (0 = p_defensoria_id OR ad.defensoria_id = p_defensoria_id)*/
                WHERE
                    (
                        0 = p_defensor_id OR 
                        COALESCE(pf.defensor_substituto_id, pf.defensor_cadastro_id) =  p_defensor_id
                    )
                    AND (
                        date_part('year', pf.data_cadastro) = date_part('year', pf.data_protocolo) AND
                        date_part('month', pf.data_cadastro) = date_part('month', pf.data_protocolo)
                    )
                GROUP BY pf.defensor_substituto_id, pf.defensor_cadastro_id, /*ad.defensoria_id,*/ pp.area_id, com.id, dir.id, ano, mes;
            $BODY$;"""),
        migrations.RunSQL(
            reverse_sql="""DROP FUNCTION public.buscar_quantitativo_atividades(
            timestamp without time zone, timestamp without time zone, integer, integer, integer, integer, integer);""",
            sql="""
            CREATE OR REPLACE FUNCTION public.buscar_quantitativo_atividades(
              p_data_inicial timestamp without time zone DEFAULT '2020-01-01 00:00:00'::timestamp without time zone,
              p_data_final timestamp without time zone DEFAULT '2020-12-31 23:59:59'::timestamp without time zone,
              p_defensor_id integer DEFAULT 0,
              p_defensoria_id integer DEFAULT 0,
              p_area_id integer DEFAULT 0,
              p_comarca_id integer DEFAULT '-1'::integer,
              p_diretoria_id integer DEFAULT '-1'::integer)
              RETURNS TABLE(
                ordem smallint, 
                consulta character varying, 
                defensor_id integer, 
                defensoria_id integer, 
                area_id integer, 
                comarca_id integer, 
                coordenadoria_id integer, 
                ano smallint, 
                mes smallint, 
                mes_abreviacao character varying, 
                qtd bigint
              ) 
        LANGUAGE 'sql'
    
        COST 100
        IMMUTABLE 
        ROWS 1000
    AS $BODY$
    
    WITH
    cte_mes AS (
        SELECT CAST(1 AS SMALLINT) AS mes, CAST('JAN' as VARCHAR) mes_abreviacao
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
    , cte_union AS (
        SELECT
        CAST(1 AS SMALLINT) ordem
        , CAST('ATENDIMENTOS' AS VARCHAR) AS consulta
        , aa.defensor_id
        , aa.defensoria_id
        , aa.area_id
        , aa.comarca_id
        , aa.coordenadoria_id
        , aa.ano
        , mes.mes
        , mes.mes_abreviacao
        , COALESCE(aa.qtd, 0) AS qtd
        FROM public.buscar_quantitativo_agendamento_atendimento(
            2, -- agendamentos atendidos
            p_data_inicial, 
            p_data_final, 
            p_area_id, 
            p_comarca_id, 
            p_defensor_id, 
            p_diretoria_id, 
            p_defensoria_id	
            ) AS aa
        RIGHT JOIN cte_mes mes ON mes.mes = aa.mes
        WHERE aa.tipo <> 7 -- atendimentos
        
    
        UNION ALL
        SELECT
        CAST(2 AS SMALLINT) ordem
        , CAST('VISITAS AOS PRESOS' AS VARCHAR) AS consulta
        , aa.defensor_id
        , aa.defensoria_id
        , aa.area_id
        , aa.comarca_id
        , aa.coordenadoria_id
        , aa.ano
        , mes.mes
        , mes.mes_abreviacao
        , COALESCE(aa.qtd, 0) AS qtd
        FROM public.buscar_quantitativo_agendamento_atendimento(
            2, -- agendamentos atendidos
            p_data_inicial, 
            p_data_final, 
            p_area_id, 
            p_comarca_id, 
            p_defensor_id, 
            p_diretoria_id, 
            p_defensoria_id	
            ) AS aa
        RIGHT JOIN cte_mes mes ON mes.mes = aa.mes
        WHERE aa.tipo = 7 -- visita aos presos
    
        UNION ALL
        SELECT
        CAST(3 AS SMALLINT) ordem
        , CAST('AÇÕES EXTRAJUDICIAIS (SEM HOMOLOGAÇÃO JUDICIAL)' AS VARCHAR) AS consulta
        , aa.defensor_id
        , aa.defensoria_id
        , aa.area_id
        , aa.comarca_id
        , aa.coordenadoria_id
        , aa.ano
        , mes.mes
        , mes.mes_abreviacao
        , COALESCE(aa.qtd, 0) AS qtd
        FROM public.buscar_quantitativo_atividades_acoes_extrajudiciais(
            p_data_inicial,
            p_data_final,
            p_defensor_id,
            p_defensoria_id,
            p_area_id, 
            p_comarca_id,
            p_diretoria_id	
        ) AS aa
        RIGHT JOIN cte_mes mes ON mes.mes = aa.mes
    
        UNION ALL
        SELECT 
        CAST(4 AS SMALLINT) AS ordem
        , CAST('AÇÕES JUDICIAIS PROTOCOLADAS PELO DEFENSOR' AS VARCHAR) AS consulta
        , aa.defensor_id
        , aa.defensoria_id
        , aa.area_id
        , aa.comarca_id
        , aa.coordenadoria_id
        , aa.ano
        , mes.mes
        , mes.mes_abreviacao
        , COALESCE(aa.qtd, 0) AS qtd
        FROM public.buscar_quantitativo_atividades_acoes_judiciais_protocoladas(
            p_data_inicial,
            p_data_final,
            p_defensor_id,
            p_defensoria_id,
            p_area_id, 
            p_comarca_id,
            p_diretoria_id	
        ) AS aa
        RIGHT JOIN cte_mes mes ON mes.mes = aa.mes
    
        UNION ALL
        SELECT
        CAST(5 AS SMALLINT) AS ordem
        , CAST('AÇÕES JUDICIAIS NÃO INICIADAS PELO DEFENSOR' AS VARCHAR) AS consulta
        , aa.defensor_id
        , aa.defensoria_id
        , aa.area_id
        , aa.comarca_id
        , aa.coordenadoria_id
        , aa.ano
        , mes.mes
        , mes.mes_abreviacao
        , COALESCE(aa.qtd, 0) AS qtd
        FROM public.buscar_quantitativo_atividades_acoes_judiciais_designadas(
            p_data_inicial,
            p_data_final,
            p_defensor_id,
            p_defensoria_id,
            p_area_id, 
            p_comarca_id,
            p_diretoria_id	
        ) AS aa
        RIGHT JOIN cte_mes mes ON mes.mes = aa.mes
    
        UNION ALL
        SELECT 
        CAST(6 AS SMALLINT) AS ordem
        , CAST('AUDIÊNCIAS' AS VARCHAR) AS consulta
        , aa.defensor_id
        , aa.defensoria_id
        , aa.area_id
        , aa.comarca_id
        , aa.coordenadoria_id
        , aa.ano
        , mes.mes
        , mes.mes_abreviacao
        , COALESCE(aa.qtd, 0) AS qtd
        FROM public.buscar_quantitativo_atividades_audiencias(
            p_data_inicial,
            p_data_final,
            p_defensor_id,
            p_defensoria_id,
            p_area_id, 
            p_comarca_id,
            p_diretoria_id	
        ) AS aa
        RIGHT JOIN cte_mes mes ON mes.mes = aa.mes
    
        UNION ALL
        SELECT
        CAST(7 AS SMALLINT) AS ordem
        , CAST('JÚRIS' AS VARCHAR) AS consulta
        , aa.defensor_id
        , aa.defensoria_id
        , aa.area_id
        , aa.comarca_id
        , aa.coordenadoria_id
        , aa.ano
        , mes.mes
        , mes.mes_abreviacao
        , COALESCE(aa.qtd, 0) AS qtd
        FROM public.buscar_quantitativo_atividades_juris(
            p_data_inicial,
            p_data_final,
            p_defensor_id,
            p_defensoria_id,
            p_area_id, 
            p_comarca_id,
            p_diretoria_id	
        ) AS aa
        RIGHT JOIN cte_mes mes ON mes.mes = aa.mes
    
        UNION ALL
        SELECT
        CAST(8 AS SMALLINT) AS ordem
        , CAST('SENTENÇAS' AS VARCHAR) AS consulta
        , aa.defensor_id
        , aa.defensoria_id
        , aa.area_id
        , aa.comarca_id
        , aa.coordenadoria_id
        , aa.ano
        , mes.mes
        , mes.mes_abreviacao
        , COALESCE(aa.qtd, 0) AS qtd
        FROM public.buscar_quantitativo_atividades_sentencas(
            p_data_inicial,
            p_data_final,
            p_defensor_id,
            p_defensoria_id,
            p_area_id, 
            p_comarca_id,
            p_diretoria_id	
        ) AS aa
        RIGHT JOIN cte_mes mes ON mes.mes = aa.mes
    
        UNION ALL
        SELECT
        CAST(9 AS SMALLINT) AS ordem
        , CAST('RECURSOS' AS VARCHAR) AS consulta
        , aa.defensor_id
        , aa.defensoria_id
        , aa.area_id
        , aa.comarca_id
        , aa.coordenadoria_id
        , aa.ano
        , mes.mes
        , mes.mes_abreviacao
        , COALESCE(aa.qtd, 0) AS qtd
        FROM public.buscar_quantitativo_atividades_recursos(
            p_data_inicial,
            p_data_final,
            p_defensor_id,
            p_defensoria_id,
            p_area_id, 
            p_comarca_id,
            p_diretoria_id	
        ) AS aa
        RIGHT JOIN cte_mes mes ON mes.mes = aa.mes
    
        UNION ALL
        SELECT 
        CAST(10 AS SMALLINT) AS ordem
        , CAST('DEMAIS FASES PROCESSUAIS' AS VARCHAR) AS consulta
        , aa.defensor_id
        , aa.defensoria_id
        , aa.area_id
        , aa.comarca_id
        , aa.coordenadoria_id
        , aa.ano
        , mes.mes
        , mes.mes_abreviacao
        , COALESCE(aa.qtd, 0) AS qtd
        FROM public.buscar_quantitativo_atividades_demais_fases_processuais(
            p_data_inicial,
            p_data_final,
            p_defensor_id,
            p_defensoria_id,
            p_area_id, 
            p_comarca_id,
            p_diretoria_id	
        ) AS aa
        RIGHT JOIN cte_mes mes ON mes.mes = aa.mes
    )
    SELECT
    aa.ordem
    , aa.consulta
    , aa.defensor_id
    , aa.defensoria_id
    , aa.area_id
    , aa.comarca_id
    , aa.coordenadoria_id
    , aa.ano
    , CAST(aa.mes AS SMALLINT)
    , aa.mes_abreviacao
    , CAST(aa.qtd AS BIGINT) AS qtd
    FROM cte_union aa;
    $BODY$;"""),
        migrations.RunSQL(
            reverse_sql="""DROP FUNCTION public.buscar_quantitativo_atividades_crosstab(
            timestamp without time zone, timestamp without time zone, integer, integer, integer, integer, integer);""",
            sql="""CREATE OR REPLACE FUNCTION public.buscar_quantitativo_atividades_crosstab(
                p_data_inicial timestamp without time zone DEFAULT '2020-01-01 00:00:00'::timestamp without time zone,
                p_data_final timestamp without time zone DEFAULT '2020-12-31 23:59:59'::timestamp without time zone,
                p_defensor_id integer DEFAULT 0,
                p_defensoria_id integer DEFAULT 0,
                p_area_id integer DEFAULT 0,
                p_comarca_id integer DEFAULT '-1'::integer,
                p_coordenadoria_id integer DEFAULT '-1'::integer)
                RETURNS TABLE(
                  tipo_nome character varying, 
                  jan integer, 
                  fev integer, 
                  mar integer, 
                  abr integer, 
                  mai integer, 
                  jun integer, 
                  jul integer, 
                  ago integer, 
                  set integer, 
                  "out" integer, 
                  nov integer, 
                  dez integer
                ) 
                LANGUAGE 'plpgsql'
            
                COST 100
                IMMUTABLE STRICT 
                ROWS 1000
                AS $BODY$
                    DECLARE consulta text;
                    BEGIN
                    consulta := 'SELECT consulta, mes, COALESCE(SUM(qtd), 0) AS qtd'
                            || ' FROM public.buscar_quantitativo_atividades('''
                            || p_data_inicial || '''::timestamp, ''' 
                            || p_data_final  || '''::timestamp, '
                            || p_defensor_id || ', ' 
                            || p_defensoria_id || ', '
                            || p_area_id || ', ' 
                            || p_comarca_id || ', ' 
                            || p_coordenadoria_id || ')'
                            || ' GROUP BY ordem, consulta, mes ORDER BY ordem';
                    RETURN QUERY SELECT * FROM crosstab(consulta , 'SELECT * FROM generate_series(1, 12)') 
                        AS ct (
                        consulta varchar, 
                        "Jan" integer, 
                        "Fev" integer, 
                        "Mar" integer, 
                        "Abr" integer, 
                        "Mai" integer, 
                        "Jun" integer, 
                        "Jul" integer, 
                        "Ago" integer, 
                        "Set" integer, 
                        "Out" integer, 
                        "Nov" integer, 
                        "Dez" integer
                        );
                    END;
                $BODY$;""")
    ]
