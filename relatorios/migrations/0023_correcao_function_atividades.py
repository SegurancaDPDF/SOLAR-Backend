# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('relatorios', '0022_correcao_function_relatorio_quantitativo_agrupado'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE FUNCTION public.buscar_quantitativo_atividade_geral(
                    IN p_ano integer DEFAULT 2017,
                    IN p_area_id integer DEFAULT 0,
                    IN p_comarca_id integer DEFAULT '-1'::integer,
                    IN p_defensor_id integer DEFAULT 0)
                  RETURNS TABLE(ordem integer, consulta character varying, area_id integer, area character varying, ano smallint, qtd bigint, mes integer, mes_abreviacao character varying) AS
                $BODY$

                        WITH
                        cte_mes AS (
                            SELECT CAST(1 AS SMALLINT) mes_id, CAST('JAN' as VARCHAR) mes_abreviacao
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
                        , cte_atendimento AS (
                            /* atendimentos - A
                                Busca o quantitativo de atendimentos.
                            */

                            SELECT
                            CAST(1 AS SMALLINT) ordem
                            , CAST('ATENDIMENTOS' AS VARCHAR) AS consulta
                            , area.id AS area_id
                            , area.nome AS area
                            --, pf.atividade
                            , CAST(date_part('year', aa.data_atendimento) AS SMALLINT) ano 
                            , CAST(date_part('month', aa.data_atendimento) AS SMALLINT) mes
                            , COUNT(aa.id) AS qtd
                            FROM atendimento_defensor ad
                            INNER JOIN atendimento_atendimento aa ON aa.id = ad.atendimento_ptr_id
                                AND aa.ativo = TRUE
                                AND aa.remarcado_id is null
                                AND aa.tipo IN (1,2,4,9)
                                AND (-1 = p_comarca_id OR ad.comarca_id = p_comarca_id)
                                AND date_part('year', aa.data_atendimento) = p_ano
                                AND (
                                    (0 = p_defensor_id)
                                    OR (
                                    (ad.substituto_id IS NULL AND ad.defensor_id = p_defensor_id)
                                    OR (ad.substituto_id = p_defensor_id)
                                    )
                                )
                            INNER JOIN atendimento_qualificacao aq ON aq.id = aa.qualificacao_id
                            INNER JOIN public.contrib_area area ON area.id = aq.area_id
                                AND ( 0 = p_area_id OR area.id = p_area_id)
                            INNER JOIN contrib_defensoria def ON def.id = ad.defensoria_id
                            INNER JOIN contrib_comarca com ON com.id = ad.comarca_id
                            LEFT JOIN atendimento_atendimento aa_nucleo ON aa_nucleo.origem_id = ad.atendimento_ptr_id 
                                AND aa_nucleo.tipo = 4
                            --LEFT JOIN aa_nucleo ON aa_nucleo.origem_id = ad.atendimento_ptr_id
                            WHERE
                            aa_nucleo.origem_id IS NULL
                            GROUP BY area.id, area.nome, ano, mes
                        )
                        , cte_visita AS (
                            /* Visitas ao preso - V */
                            SELECT
                            CAST(2 AS SMALLINT) ordem
                            , CAST('VISITAS AOS PRESOS' AS VARCHAR) AS consulta
                            , area.id AS area_id
                            , area.nome AS area
                            --, pf.atividade
                            , CAST(date_part('year', aa.data_atendimento) AS SMALLINT) ano 
                            , CAST(date_part('month', aa.data_atendimento) AS SMALLINT) mes
                            , COUNT(aa.id) AS qtd
                            FROM atendimento_defensor ad
                            INNER JOIN atendimento_atendimento aa ON aa.id = ad.atendimento_ptr_id
                                AND aa.ativo = TRUE
                                AND aa.remarcado_id is null
                                AND aa.tipo = 7
                                AND (-1 = p_comarca_id OR ad.comarca_id = p_comarca_id)
                                AND  date_part('year', aa.data_atendimento) = p_ano
                                AND (
                                    (0 = p_defensor_id)
                                    OR (
                                        (ad.substituto_id IS NULL AND ad.defensor_id = p_defensor_id)
                                    OR (ad.substituto_id = p_defensor_id)
                                    )
                                )
                            INNER JOIN atendimento_qualificacao aq ON aq.id = aa.qualificacao_id
                            INNER JOIN public.contrib_area area ON area.id = aq.area_id
                                AND (area.id = p_area_id OR 0 = p_area_id)
                            INNER JOIN contrib_defensoria def ON def.id = ad.defensoria_id
                            INNER JOIN contrib_comarca com ON com.id = ad.comarca_id
                            GROUP BY area.id, area.nome, ano, mes
                        )
                        , cte_ae AS (
                            /* acoes extrajudiciais - AE */
                            SELECT
                            CAST(3 AS SMALLINT) ordem
                            , CAST('AÇÕES EXTRAJUDICIAIS (SEM HOMOLOGAÇÃO JUDICIAL)' AS VARCHAR) AS consulta
                            , area.id AS area_id
                            , area.nome AS area
                            --, pf.atividade
                            , CAST(date_part('year', ppa.data_cadastro) AS SMALLINT) ano 
                            , CAST(date_part('month', ppa.data_cadastro) AS SMALLINT) mes
                            , COUNT(ppa.id) AS qtd
                            FROM processo_parte ppa
                            INNER JOIN processo_processo pp ON pp.id = ppa.processo_id
                                AND pp.ativo = TRUE
                                AND ppa.ativo = TRUE
                                AND pp.tipo = 0
                                AND pp.area_id IS NOT NULL
                                AND date_part('year', ppa.data_cadastro) = p_ano
                                AND (pp.comarca_id = p_comarca_id OR -1 = p_comarca_id)
                                AND (ppa.defensor_id = p_defensor_id OR 0 = p_defensor_id)
                            INNER JOIN public.contrib_area area ON area.id = pp.area_id
                                AND (0 = p_area_id OR area.id = p_area_id)
                            INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                            GROUP BY area.id, area.nome, ano, mes
                        )
                        , cte_ajp AS (
                            /* acoes judiciais protocoladas - AJP */
                            SELECT
                            CAST(4 AS SMALLINT) ordem
                            , CAST('AÇÕES JUDICIAIS PROTOCOLADAS PELO DEFENSOR' AS VARCHAR) AS consulta
                            , area.id AS area_id
                            , area.nome AS area
                            --, pf.atividade
                            , CAST(date_part('year', ini.data_cadastro) AS SMALLINT) ano 
                            , CAST(date_part('month', ini.data_cadastro) AS SMALLINT) mes
                            , COUNT(distinct(pp.id)) AS qtd
                            FROM processo_parte ppa
                            INNER JOIN processo_processo pp ON pp.id = ppa.processo_id
                            AND pp.ativo = TRUE
                            AND pp.tipo != 0
                            AND pp.area_id IS NOT NULL
                            AND ppa.ativo = TRUE
                            AND (pp.comarca_id = p_comarca_id OR -1 = p_comarca_id)
                            INNER JOIN public.contrib_area area ON area.id = pp.area_id
                                AND (area.id = p_area_id OR 0 = p_area_id)
                            INNER JOIN processo_fase ini ON ini.id = pp.peticao_inicial_id
                            AND ini.ativo = TRUE
                            AND ini.defensor_cadastro_id IS NOT NULL
                            INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                            WHERE
                                (ini.defensor_cadastro_id = p_defensor_id OR 0 = p_defensor_id)
                                AND date_part('year', ini.data_cadastro) = p_ano
                                AND (
                                    date_part('year', ini.data_cadastro) = date_part('year', ini.data_protocolo) AND
                                    date_part('month', ini.data_cadastro) = date_part('month', ini.data_protocolo)
                                    )
                            GROUP BY area.id, area.nome, ano, mes
                        )
                        , cte_ajd AS (
                            /* acoes judiciais designadas - AJD */
                            SELECT
                            CAST(5 AS SMALLINT) ordem
                            , CAST('AÇÕES JUDICIAIS NÃO INICIADAS PELO DEFENSOR' AS VARCHAR) AS consulta
                            , area.id AS area_id
                            , area.nome AS area
                            --, pf.atividade
                            , CAST(date_part('year', ppa.data_cadastro) AS SMALLINT) ano 
                            , CAST(date_part('month', ppa.data_cadastro) AS SMALLINT) mes
                            , COUNT(ppa.id) AS qtd
                            FROM processo_parte ppa
                            INNER JOIN processo_processo pp ON pp.id = ppa.processo_id
                            AND pp.area_id IS NOT NULL
                            AND pp.tipo != 0
                            AND ppa.ativo = TRUE
                            AND pp.ativo = TRUE
                            AND date_part('year', ppa.data_cadastro) = p_ano
                            INNER JOIN public.contrib_area area ON area.id = pp.area_id
                                AND (area.id = p_area_id OR 0 = p_area_id)
                            INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                            LEFT JOIN processo_fase ini ON ini.id = pp.peticao_inicial_id
                            WHERE
                                (
                                    ((ppa.defensor_id IS NOT NULL) AND (ppa.defensor_id = p_defensor_id OR 0 = p_defensor_id) AND (ppa.data_cadastro::date < '2015-04-01')) OR
                                    ((ppa.defensor_cadastro_id IS NOT NULL) AND (ppa.defensor_cadastro_id = p_defensor_id OR 0 = p_defensor_id) AND (ppa.data_cadastro::date >= '2015-04-01'))
                                )
                                AND (pp.comarca_id = p_comarca_id OR -1 = p_comarca_id)
                                AND (pp.peticao_inicial_id IS NULL OR (ppa.defensor_cadastro_id != ini.defensor_cadastro_id AND ini.defensor_cadastro_id IS NOT NULL))
                            GROUP BY area.id, area.nome, ano, mes
                        )
                        , cte_audiencia AS (
                            /* AUDIENCIAS */
                            SELECT
                            CAST(6 AS SMALLINT) ordem
                            , CAST('AUDIÊNCIAS' AS VARCHAR) AS consulta
                            , area.id AS area_id
                            , area.nome AS area
                            --, pf.atividade
                            , CAST(date_part('year', pf.data_protocolo) AS SMALLINT) ano 
                            , CAST(date_part('month', pf.data_protocolo) AS SMALLINT) mes
                            , COUNT(distinct(pa.fase_ptr_id)) AS qtd
                            FROM processo_audiencia pa
                            INNER JOIN processo_fase pf ON pf.id = pa.fase_ptr_id
                            AND pf.ativo = TRUE
                            AND pf.atividade = 1
                            AND pf.defensor_cadastro_id IS NOT NULL
                            AND pa.audiencia_realizada = TRUE
                            AND date_part('year', pf.data_protocolo) = p_ano
                            INNER JOIN processo_processo pp ON pp.id = pf.processo_id
                            AND pp.area_id IS NOT NULL
                            AND pp.ativo = TRUE
                            INNER JOIN public.contrib_area area ON area.id = pp.area_id
                                AND (area.id = p_area_id OR 0 = p_area_id)
                            INNER JOIN processo_parte ppa ON ppa.processo_id = pp.id
                            AND ppa.ativo = TRUE
                            INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                            WHERE
                                (
                                    (
                                        (pf.defensor_cadastro_id = p_defensor_id AND pf.defensor_substituto_id IS NULL) OR
                                        (pf.defensor_substituto_id = p_defensor_id)
                                    )
                                    OR (0 = p_defensor_id)
                                )
                                AND (pp.comarca_id = p_comarca_id OR -1 = p_comarca_id)
                                AND (data_baixa::date <= (data_protocolo::date - interval '1 day' * (date_part('day', data_protocolo)-5)) + interval '1 month' OR data_baixa IS NULL)
                            GROUP BY area.id, area.nome, ano, mes
                        )
                        , cte_juri AS (
                            /* JURI */
                            SELECT
                            CAST(7 AS SMALLINT) ordem
                            , CAST('JÚRIS' AS VARCHAR) AS consulta
                            , area.id AS area_id
                            , area.nome AS area
                            --, pf.atividade
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
                            INNER JOIN public.contrib_area area ON area.id = pp.area_id
                                AND (area.id = p_area_id OR 0 = p_area_id)
                            INNER JOIN processo_parte ppa ON ppa.processo_id = pp.id
                            AND ppa.ativo = TRUE
                            INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                            WHERE
                                (
                                    (
                                        (pf.defensor_cadastro_id = p_defensor_id AND pf.defensor_substituto_id IS NULL) OR
                                        (pf.defensor_substituto_id = p_defensor_id)
                                    )
                                    OR (0 = p_defensor_id)
                                )
                                AND (pp.comarca_id = p_comarca_id OR -1 = p_comarca_id)
                                AND date_part('year', pf.data_protocolo) = p_ano
                                AND (data_baixa::date <= (data_protocolo::date - interval '1 day' * (date_part('day', data_protocolo)-5)) + interval '1 month' OR data_baixa IS NULL)
                            GROUP BY area.id, area.nome, ano, mes
                        )
                        , cte_sentenca AS (
                            /* SENTENCA */
                            SELECT
                            CAST(8 AS SMALLINT) ordem
                            , CAST('SENTENÇAS' AS VARCHAR) AS consulta
                            , area.id AS area_id
                            , area.nome AS area
                            --, pf.atividade
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
                                AND date_part('year', pf.data_protocolo) = p_ano
                            INNER JOIN public.contrib_area area ON area.id = pp.area_id
                                AND (area.id = p_area_id OR 0 = p_area_id)
                            INNER JOIN processo_parte ppa ON ppa.processo_id = pp.id
                                AND ppa.ativo = TRUE
                            INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                            AND (pp.comarca_id = p_comarca_id OR -1 = p_comarca_id)
                            WHERE
                                (
                                    (
                                        (pf.defensor_cadastro_id = p_defensor_id AND pf.defensor_substituto_id IS NULL) OR
                                        (pf.defensor_substituto_id = p_defensor_id)
                                    )
                                    OR (0 = p_defensor_id)
                                )
                                AND (
                                    date_part('year', pf.data_cadastro) = date_part('year', pf.data_protocolo) AND
                                    date_part('month', pf.data_cadastro) = date_part('month', pf.data_protocolo)
                                    )
                            GROUP BY area.id, area.nome, ano, mes
                        )
                        , cte_recurso AS (
                            /* RECURSO */
                            SELECT
                            CAST(9 AS SMALLINT) ordem
                            , CAST('RECURSOS' AS VARCHAR) AS consulta
                            , area.id AS area_id
                            , area.nome AS area
                            --, pf.atividade
                            , CAST(date_part('year', pf.data_cadastro) AS SMALLINT) ano 
                            , CAST(date_part('month', pf.data_cadastro) AS SMALLINT) mes
                            , COUNT(distinct(pf.id)) AS qtd
                            FROM processo_fase pf
                            INNER JOIN processo_processo pp ON pp.id = pf.processo_id
                                AND date_part('year', pf.data_protocolo) = p_ano
                                AND pp.area_id IS NOT NULL
                                AND pf.defensor_cadastro_id IS NOT NULL
                                AND pf.ativo = TRUE
                                AND pf.atividade = 4
                                AND pp.ativo = TRUE
                            INNER JOIN public.contrib_area area ON area.id = pp.area_id
                                AND (area.id = p_area_id OR 0 = p_area_id)
                            INNER JOIN processo_parte ppa ON ppa.processo_id = pp.id
                                AND ppa.ativo = TRUE
                            INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                            WHERE
                                (
                                    (
                                        (pf.defensor_cadastro_id = p_defensor_id AND pf.defensor_substituto_id IS NULL) OR
                                        (pf.defensor_substituto_id = p_defensor_id)
                                    )
                                    OR (0 = p_defensor_id)
                                )
                            AND (pp.comarca_id = p_comarca_id OR -1 = p_comarca_id)

                            AND (
                                date_part('year', pf.data_cadastro) = date_part('year', pf.data_protocolo) AND
                                date_part('month', pf.data_cadastro) = date_part('month', pf.data_protocolo)
                                ) 
                            GROUP BY area.id, ano, mes
                        )
                        , cte_fase AS (
                            /* FASES */
                            SELECT
                            CAST(10 AS SMALLINT) ordem
                            , CAST('DEMAIS FASES PROCESSUAIS' AS VARCHAR) AS consulta
                            , area.id AS area_id
                            , area.nome AS area
                            --, pf.atividade
                            , CAST(date_part('year', pf.data_cadastro) AS SMALLINT) ano 
                            , CAST(date_part('month', pf.data_cadastro) AS SMALLINT) mes
                            , COUNT(distinct(pf.id)) AS qtd
                            FROM processo_fase pf
                            INNER JOIN processo_processo pp ON pp.id = pf.processo_id
                                AND date_part('year', pf.data_protocolo) = p_ano
                                AND pf.ativo = TRUE
                                AND pf.atividade = 0
                                AND pp.area_id IS NOT NULL
                                AND pf.defensor_cadastro_id IS NOT NULL
                                AND pp.ativo = TRUE
                            INNER JOIN public.contrib_area area ON area.id = pp.area_id
                                AND (area.id = p_area_id OR 0 = p_area_id)
                            INNER JOIN processo_parte ppa ON ppa.processo_id = pp.id
                                AND ppa.ativo = TRUE
                            INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                            WHERE
                                (
                                    (
                                        (pf.defensor_cadastro_id = p_defensor_id AND pf.defensor_substituto_id IS NULL) OR
                                        (pf.defensor_substituto_id = p_defensor_id)
                                    )
                                    OR (0 = p_defensor_id)
                                )
                                AND (pp.comarca_id = p_comarca_id OR -1 = p_comarca_id)
                                AND (
                (
                date_part('year', pf.data_cadastro) = date_part('year', pf.data_protocolo) AND
                date_part('month', pf.data_cadastro) = date_part('month', pf.data_protocolo) 
                ) 
                OR (
                    date_part('year', pf.data_cadastro) = date_part('year', pf.data_protocolo) AND
                    date_part('month', pf.data_cadastro) = date_part('month', pf.data_protocolo) AND
                    ppa.data_cadastro >= '20190101' and 
                    ppa.data_cadastro <= pf.data_cadastro
                )
                                    )
                            GROUP BY area.id, ano, mes
                        )
                        SELECT
                        COALESCE(a.ordem, 1)
                        , COALESCE(a.consulta, 'ATENDIMENTOS')
                        , a.area_id
                        , a.area
                        , a.ano
                        , a.qtd
                        , mes.mes_id
                        , mes.mes_abreviacao
                        FROM cte_atendimento a
                        RIGHT JOIN cte_mes mes ON mes_id = a.mes

                        UNION ALL
                        SELECT 
                        COALESCE(a.ordem, 2)
                        , COALESCE(a.consulta, 'VISITAS AOS PRESOS')
                        , a.area_id
                        , a.area
                        , a.ano
                        , a.qtd
                        , mes.mes_id
                        , mes.mes_abreviacao
                        FROM cte_visita a
                        RIGHT JOIN cte_mes mes ON mes_id = a.mes

                        UNION ALL
                        SELECT
                        COALESCE(a.ordem, 3)
                        , COALESCE(a.consulta, 'AÇÕES EXTRAJUDICIAIS (SEM HOMOLOGAÇÃO JUDICIAL)')
                        , a.area_id
                        , a.area
                        , a.ano
                        , a.qtd
                        , mes.mes_id
                        , mes.mes_abreviacao
                        FROM cte_ae a
                        RIGHT JOIN cte_mes mes ON mes_id = a.mes

                        UNION ALL
                        SELECT 
                        COALESCE(a.ordem, 4)
                        , COALESCE(a.consulta, 'AÇÕES JUDICIAIS PROTOCOLADAS PELO DEFENSOR')
                        , a.area_id
                        , a.area
                        , a.ano
                        , a.qtd
                        , mes.mes_id
                        , mes.mes_abreviacao
                        FROM cte_ajp a
                        RIGHT JOIN cte_mes mes ON mes_id = a.mes

                        UNION ALL
                        SELECT 
                        COALESCE(a.ordem, 5)
                        , COALESCE(a.consulta, 'AÇÕES JUDICIAIS NÃO INICIADAS PELO DEFENSOR')
                        , a.area_id
                        , a.area
                        , a.ano
                        , a.qtd
                        , mes.mes_id
                        , mes.mes_abreviacao
                        FROM cte_ajd a
                        RIGHT JOIN cte_mes mes ON mes_id = a.mes

                        UNION ALL
                        SELECT 
                        COALESCE(a.ordem, 6)
                        , COALESCE(a.consulta, 'AUDIÊNCIAS')
                        , a.area_id
                        , a.area
                        , a.ano
                        , a.qtd
                        , mes.mes_id
                        , mes.mes_abreviacao
                        FROM cte_audiencia a
                        RIGHT JOIN cte_mes mes ON mes_id = a.mes

                        UNION ALL
                        SELECT
                        COALESCE(a.ordem, 7)
                        , COALESCE(a.consulta, 'JÚRIS')
                        , a.area_id
                        , a.area
                        , a.ano
                        , a.qtd
                        , mes.mes_id
                        , mes.mes_abreviacao
                        FROM cte_juri a
                        RIGHT JOIN cte_mes mes ON mes_id = a.mes

                        UNION ALL
                        SELECT
                        COALESCE(a.ordem, 8)
                        , COALESCE(a.consulta, 'SENTENÇAS')
                        , a.area_id
                        , a.area
                        , a.ano
                        , a.qtd
                        , mes.mes_id
                        , mes.mes_abreviacao
                        FROM cte_sentenca a
                        RIGHT JOIN cte_mes mes ON mes_id = a.mes

                        UNION ALL
                        SELECT
                        COALESCE(a.ordem, 9)
                        , COALESCE(a.consulta, 'RECURSOS')
                        , a.area_id
                        , a.area
                        , a.ano
                        , a.qtd
                        , mes.mes_id
                        , mes.mes_abreviacao
                        FROM cte_recurso a
                        RIGHT JOIN cte_mes mes ON mes_id = a.mes

                        UNION ALL
                        SELECT 
                        COALESCE(a.ordem, 10)
                        , COALESCE(a.consulta, 'DEMAIS FASES PROCESSUAIS')
                        , a.area_id
                        , a.area
                        , a.ano
                        , a.qtd
                        , mes.mes_id
                        , mes.mes_abreviacao
                        FROM cte_fase a
                        RIGHT JOIN cte_mes mes ON mes_id = a.mes
                $BODY$
              LANGUAGE sql IMMUTABLE
              COST 100
              ROWS 1000;
            """,
            reverse_sql="""
                CREATE OR REPLACE FUNCTION public.buscar_quantitativo_atividade_geral(
	                p_ano integer DEFAULT 2017,
                    p_area_id integer DEFAULT 0,
                    p_comarca_id integer DEFAULT '-1'::integer,
                    p_defensor_id integer DEFAULT 0)
                    RETURNS TABLE(ordem integer, consulta character varying, area_id integer, area character varying, ano smallint, qtd bigint, mes integer, mes_abreviacao character varying) 
                    LANGUAGE 'sql'

                        COST 100
                        IMMUTABLE 
                        ROWS 1000
                    AS $BODY$

                        WITH
                            cte_mes AS (
                                        SELECT CAST(1 AS SMALLINT) mes_id, CAST('JAN' as VARCHAR) mes_abreviacao
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
                                    , cte_atendimento AS (
                                        /* atendimentos - A
                                            Busca o quantitativo de atendimentos.
                                        */

                                        SELECT
                                        CAST(1 AS SMALLINT) ordem
                                        , CAST('ATENDIMENTOS' AS VARCHAR) AS consulta
                                        , area.id AS area_id
                                        , area.nome AS area
                                        --, pf.atividade
                                        , CAST(date_part('year', aa.data_atendimento) AS SMALLINT) ano 
                                        , CAST(date_part('month', aa.data_atendimento) AS SMALLINT) mes
                                        , COUNT(aa.id) AS qtd
                                        FROM atendimento_defensor ad
                                        INNER JOIN atendimento_atendimento aa ON aa.id = ad.atendimento_ptr_id
                                            AND aa.ativo = TRUE
                                            AND aa.remarcado_id is null
                                            AND aa.tipo IN (1,2,4,9)
                                            AND (-1 = p_comarca_id OR ad.comarca_id = p_comarca_id)
                                            AND date_part('year', aa.data_atendimento) = p_ano
                                            AND (
                                                (0 = p_defensor_id)
                                                OR (
                                                (ad.substituto_id IS NULL AND ad.defensor_id = p_defensor_id)
                                                OR (ad.substituto_id = p_defensor_id)
                                                )
                                            )
                                        INNER JOIN atendimento_qualificacao aq ON aq.id = aa.qualificacao_id
                                        INNER JOIN public.contrib_area area ON area.id = aq.area_id
                                            AND ( 0 = p_area_id OR area.id = p_area_id)
                                        INNER JOIN contrib_defensoria def ON def.id = ad.defensoria_id
                                        INNER JOIN contrib_comarca com ON com.id = ad.comarca_id
                                        LEFT JOIN atendimento_atendimento aa_nucleo ON aa_nucleo.origem_id = ad.atendimento_ptr_id 
                                            AND aa_nucleo.tipo = 4
                                        --LEFT JOIN aa_nucleo ON aa_nucleo.origem_id = ad.atendimento_ptr_id
                                        WHERE
                                        aa_nucleo.origem_id IS NULL
                                        GROUP BY area.id, area.nome, ano, mes
                                    )
                                    , cte_visita AS (
                                        /* Visitas ao preso - V */
                                        SELECT
                                        CAST(2 AS SMALLINT) ordem
                                        , CAST('VISITAS AOS PRESOS' AS VARCHAR) AS consulta
                                        , area.id AS area_id
                                        , area.nome AS area
                                        --, pf.atividade
                                        , CAST(date_part('year', aa.data_atendimento) AS SMALLINT) ano 
                                        , CAST(date_part('month', aa.data_atendimento) AS SMALLINT) mes
                                        , COUNT(aa.id) AS qtd
                                        FROM atendimento_defensor ad
                                        INNER JOIN atendimento_atendimento aa ON aa.id = ad.atendimento_ptr_id
                                            AND aa.ativo = TRUE
                                            AND aa.remarcado_id is null
                                            AND aa.tipo = 7
                                            AND (-1 = p_comarca_id OR ad.comarca_id = p_comarca_id)
                                            AND  date_part('year', aa.data_atendimento) = p_ano
                                            AND (
                                                (0 = p_defensor_id)
                                                OR (
                                                    (ad.substituto_id IS NULL AND ad.defensor_id = p_defensor_id)
                                                OR (ad.substituto_id = p_defensor_id)
                                                )
                                            )
                                        INNER JOIN atendimento_qualificacao aq ON aq.id = aa.qualificacao_id
                                        INNER JOIN public.contrib_area area ON area.id = aq.area_id
                                            AND (area.id = p_area_id OR 0 = p_area_id)
                                        INNER JOIN contrib_defensoria def ON def.id = ad.defensoria_id
                                        INNER JOIN contrib_comarca com ON com.id = ad.comarca_id
                                        GROUP BY area.id, area.nome, ano, mes
                                    )
                                    , cte_ae AS (
                                        /* acoes extrajudiciais - AE */
                                        SELECT
                                        CAST(3 AS SMALLINT) ordem
                                        , CAST('AÇÕES EXTRAJUDICIAIS (SEM HOMOLOGAÇÃO JUDICIAL)' AS VARCHAR) AS consulta
                                        , area.id AS area_id
                                        , area.nome AS area
                                        --, pf.atividade
                                        , CAST(date_part('year', ppa.data_cadastro) AS SMALLINT) ano 
                                        , CAST(date_part('month', ppa.data_cadastro) AS SMALLINT) mes
                                        , COUNT(ppa.id) AS qtd
                                        FROM processo_parte ppa
                                        INNER JOIN processo_processo pp ON pp.id = ppa.processo_id
                                            AND pp.ativo = TRUE
                                            AND ppa.ativo = TRUE
                                            AND pp.tipo = 0
                                            AND pp.area_id IS NOT NULL
                                            AND date_part('year', ppa.data_cadastro) = p_ano
                                            AND (pp.comarca_id = p_comarca_id OR -1 = p_comarca_id)
                                            AND (ppa.defensor_id = p_defensor_id OR 0 = p_defensor_id)
                                        INNER JOIN public.contrib_area area ON area.id = pp.area_id
                                            AND (0 = p_area_id OR area.id = p_area_id)
                                        INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                                        GROUP BY area.id, area.nome, ano, mes
                                    )
                                    , cte_ajp AS (
                                        /* acoes judiciais protocoladas - AJP */
                                        SELECT
                                        CAST(4 AS SMALLINT) ordem
                                        , CAST('AÇÕES JUDICIAIS PROTOCOLADAS PELO DEFENSOR' AS VARCHAR) AS consulta
                                        , area.id AS area_id
                                        , area.nome AS area
                                        --, pf.atividade
                                        , CAST(date_part('year', ini.data_cadastro) AS SMALLINT) ano 
                                        , CAST(date_part('month', ini.data_cadastro) AS SMALLINT) mes
                                        , COUNT(distinct(pp.id)) AS qtd
                                        FROM processo_parte ppa
                                        INNER JOIN processo_processo pp ON pp.id = ppa.processo_id
                                        AND pp.ativo = TRUE
                                        AND pp.tipo != 0
                                        AND pp.area_id IS NOT NULL
                                        AND ppa.ativo = TRUE
                                        AND (pp.comarca_id = p_comarca_id OR -1 = p_comarca_id)
                                        INNER JOIN public.contrib_area area ON area.id = pp.area_id
                                            AND (area.id = p_area_id OR 0 = p_area_id)
                                        INNER JOIN processo_fase ini ON ini.id = pp.peticao_inicial_id
                                        AND ini.ativo = TRUE
                                        AND ini.defensor_cadastro_id IS NOT NULL
                                        INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                                        WHERE
                                            (ini.defensor_cadastro_id = p_defensor_id OR 0 = p_defensor_id)
                                            AND date_part('year', ini.data_cadastro) = p_ano
                                            AND (
                                                date_part('year', ini.data_cadastro) = date_part('year', ini.data_protocolo) AND
                                                date_part('month', ini.data_cadastro) = date_part('month', ini.data_protocolo)
                                                )
                                        GROUP BY area.id, area.nome, ano, mes
                                    )
                                    , cte_ajd AS (
                                        /* acoes judiciais designadas - AJD */
                                        SELECT
                                        CAST(5 AS SMALLINT) ordem
                                        , CAST('AÇÕES JUDICIAIS NÃO INICIADAS PELO DEFENSOR' AS VARCHAR) AS consulta
                                        , area.id AS area_id
                                        , area.nome AS area
                                        --, pf.atividade
                                        , CAST(date_part('year', ppa.data_cadastro) AS SMALLINT) ano 
                                        , CAST(date_part('month', ppa.data_cadastro) AS SMALLINT) mes
                                        , COUNT(ppa.id) AS qtd
                                        FROM processo_parte ppa
                                        INNER JOIN processo_processo pp ON pp.id = ppa.processo_id
                                        AND pp.area_id IS NOT NULL
                                        AND pp.tipo != 0
                                        AND ppa.ativo = TRUE
                                        AND pp.ativo = TRUE
                                        AND date_part('year', ppa.data_cadastro) = p_ano
                                        INNER JOIN public.contrib_area area ON area.id = pp.area_id
                                            AND (area.id = p_area_id OR 0 = p_area_id)
                                        INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                                        LEFT JOIN processo_fase ini ON ini.id = pp.peticao_inicial_id
                                        WHERE
                                            (
                                                ((ppa.defensor_id IS NOT NULL) AND (ppa.defensor_id = p_defensor_id OR 0 = p_defensor_id) AND (ppa.data_cadastro::date < '2015-04-01')) OR
                                                ((ppa.defensor_cadastro_id IS NOT NULL) AND (ppa.defensor_cadastro_id = p_defensor_id OR 0 = p_defensor_id) AND (ppa.data_cadastro::date >= '2015-04-01'))
                                            )
                                            AND (pp.comarca_id = p_comarca_id OR -1 = p_comarca_id)
                                            AND (pp.peticao_inicial_id IS NULL OR (ppa.defensor_cadastro_id != ini.defensor_cadastro_id AND ini.defensor_cadastro_id IS NOT NULL))
                                        GROUP BY area.id, area.nome, ano, mes
                                    )
                                    , cte_audiencia AS (
                                        /* AUDIENCIAS */
                                        SELECT
                                        CAST(6 AS SMALLINT) ordem
                                        , CAST('AUDIÊNCIAS' AS VARCHAR) AS consulta
                                        , area.id AS area_id
                                        , area.nome AS area
                                        --, pf.atividade
                                        , CAST(date_part('year', pf.data_protocolo) AS SMALLINT) ano 
                                        , CAST(date_part('month', pf.data_protocolo) AS SMALLINT) mes
                                        , COUNT(distinct(pa.fase_ptr_id)) AS qtd
                                        FROM processo_audiencia pa
                                        INNER JOIN processo_fase pf ON pf.id = pa.fase_ptr_id
                                        AND pf.ativo = TRUE
                                        AND pf.atividade = 1
                                        AND pf.defensor_cadastro_id IS NOT NULL
                                        AND pa.audiencia_realizada = TRUE
                                        AND date_part('year', pf.data_protocolo) = p_ano
                                        INNER JOIN processo_processo pp ON pp.id = pf.processo_id
                                        AND pp.area_id IS NOT NULL
                                        AND pp.ativo = TRUE
                                        INNER JOIN public.contrib_area area ON area.id = pp.area_id
                                            AND (area.id = p_area_id OR 0 = p_area_id)
                                        INNER JOIN processo_parte ppa ON ppa.processo_id = pp.id
                                        AND ppa.ativo = TRUE
                                        INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                                        WHERE
                                            (
                                                (
                                                    (pf.defensor_cadastro_id = p_defensor_id AND pf.defensor_substituto_id IS NULL) OR
                                                    (pf.defensor_substituto_id = p_defensor_id)
                                                )
                                                OR (0 = p_defensor_id)
                                            )
                                            AND (pp.comarca_id = p_comarca_id OR -1 = p_comarca_id)
                                            AND (data_baixa::date <= (data_protocolo::date - interval '1 day' * (date_part('day', data_protocolo)-5)) + interval '1 month' OR data_baixa IS NULL)
                                        GROUP BY area.id, area.nome, ano, mes
                                    )
                                    , cte_juri AS (
                                        /* JURI */
                                        SELECT
                                        CAST(7 AS SMALLINT) ordem
                                        , CAST('JÚRIS' AS VARCHAR) AS consulta
                                        , area.id AS area_id
                                        , area.nome AS area
                                        --, pf.atividade
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
                                        INNER JOIN public.contrib_area area ON area.id = pp.area_id
                                            AND (area.id = p_area_id OR 0 = p_area_id)
                                        INNER JOIN processo_parte ppa ON ppa.processo_id = pp.id
                                        AND ppa.ativo = TRUE
                                        INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                                        WHERE
                                            (
                                                (
                                                    (pf.defensor_cadastro_id = p_defensor_id AND pf.defensor_substituto_id IS NULL) OR
                                                    (pf.defensor_substituto_id = p_defensor_id)
                                                )
                                                OR (0 = p_defensor_id)
                                            )
                                            AND (pp.comarca_id = p_comarca_id OR -1 = p_comarca_id)
                                            AND date_part('year', pf.data_protocolo) = p_ano
                                            AND (data_baixa::date <= (data_protocolo::date - interval '1 day' * (date_part('day', data_protocolo)-5)) + interval '1 month' OR data_baixa IS NULL)
                                        GROUP BY area.id, area.nome, ano, mes
                                    )
                                    , cte_sentenca AS (
                                        /* SENTENCA */
                                        SELECT
                                        CAST(8 AS SMALLINT) ordem
                                        , CAST('SENTENÇAS' AS VARCHAR) AS consulta
                                        , area.id AS area_id
                                        , area.nome AS area
                                        --, pf.atividade
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
                                            AND date_part('year', pf.data_protocolo) = p_ano
                                        INNER JOIN public.contrib_area area ON area.id = pp.area_id
                                            AND (area.id = p_area_id OR 0 = p_area_id)
                                        INNER JOIN processo_parte ppa ON ppa.processo_id = pp.id
                                            AND ppa.ativo = TRUE
                                        INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                                        AND (pp.comarca_id = p_comarca_id OR -1 = p_comarca_id)
                                        WHERE
                                            (
                                                (
                                                    (pf.defensor_cadastro_id = p_defensor_id AND pf.defensor_substituto_id IS NULL) OR
                                                    (pf.defensor_substituto_id = p_defensor_id)
                                                )
                                                OR (0 = p_defensor_id)
                                            )
                                            AND (
                                                date_part('year', pf.data_cadastro) = date_part('year', pf.data_protocolo) AND
                                                date_part('month', pf.data_cadastro) = date_part('month', pf.data_protocolo)
                                                )
                                        GROUP BY area.id, area.nome, ano, mes
                                    )
                                    , cte_recurso AS (
                                        /* RECURSO */
                                        SELECT
                                        CAST(9 AS SMALLINT) ordem
                                        , CAST('RECURSOS' AS VARCHAR) AS consulta
                                        , area.id AS area_id
                                        , area.nome AS area
                                        --, pf.atividade
                                        , CAST(date_part('year', pf.data_cadastro) AS SMALLINT) ano 
                                        , CAST(date_part('month', pf.data_cadastro) AS SMALLINT) mes
                                        , COUNT(distinct(pf.id)) AS qtd
                                        FROM processo_fase pf
                                        INNER JOIN processo_processo pp ON pp.id = pf.processo_id
                                            AND date_part('year', pf.data_protocolo) = p_ano
                                            AND pp.area_id IS NOT NULL
                                            AND pf.defensor_cadastro_id IS NOT NULL
                                            AND pf.ativo = TRUE
                                            AND pf.atividade = 4
                                            AND pp.ativo = TRUE
                                        INNER JOIN public.contrib_area area ON area.id = pp.area_id
                                            AND (area.id = p_area_id OR 0 = p_area_id)
                                        INNER JOIN processo_parte ppa ON ppa.processo_id = pp.id
                                            AND ppa.ativo = TRUE
                                        INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                                        WHERE
                                            (
                                                (
                                                    (pf.defensor_cadastro_id = p_defensor_id AND pf.defensor_substituto_id IS NULL) OR
                                                    (pf.defensor_substituto_id = p_defensor_id)
                                                )
                                                OR (0 = p_defensor_id)
                                            )
                                        AND (pp.comarca_id = p_comarca_id OR -1 = p_comarca_id)

                                        AND (
                                            date_part('year', pf.data_cadastro) = date_part('year', pf.data_protocolo) AND
                                            date_part('month', pf.data_cadastro) = date_part('month', pf.data_protocolo)
                                            )
                                        GROUP BY area.id, ano, mes
                                    )
                                    , cte_fase AS (
                                        /* FASES */
                                        SELECT
                                        CAST(10 AS SMALLINT) ordem
                                        , CAST('DEMAIS FASES PROCESSUAIS' AS VARCHAR) AS consulta
                                        , area.id AS area_id
                                        , area.nome AS area
                                        --, pf.atividade
                                        , CAST(date_part('year', pf.data_cadastro) AS SMALLINT) ano 
                                        , CAST(date_part('month', pf.data_cadastro) AS SMALLINT) mes
                                        , COUNT(distinct(pf.id)) AS qtd
                                        FROM processo_fase pf
                                        INNER JOIN processo_processo pp ON pp.id = pf.processo_id
                                            AND date_part('year', pf.data_protocolo) = p_ano
                                            AND pf.ativo = TRUE
                                            AND pf.atividade = 0
                                            AND pp.area_id IS NOT NULL
                                            AND pf.defensor_cadastro_id IS NOT NULL
                                            AND pp.ativo = TRUE
                                        INNER JOIN public.contrib_area area ON area.id = pp.area_id
                                            AND (area.id = p_area_id OR 0 = p_area_id)
                                        INNER JOIN processo_parte ppa ON ppa.processo_id = pp.id
                                            AND ppa.ativo = TRUE
                                        INNER JOIN contrib_comarca com ON com.id = pp.comarca_id
                                        WHERE
                                            (
                                                (
                                                    (pf.defensor_cadastro_id = p_defensor_id AND pf.defensor_substituto_id IS NULL) OR
                                                    (pf.defensor_substituto_id = p_defensor_id)
                                                )
                                                OR (0 = p_defensor_id)
                                            )
                                            AND (pp.comarca_id = p_comarca_id OR -1 = p_comarca_id)
                                            AND (
                                                date_part('year', pf.data_cadastro) = date_part('year', pf.data_protocolo) AND
                                                date_part('month', pf.data_cadastro) = date_part('month', pf.data_protocolo)
                                                )
                                        GROUP BY area.id, ano, mes
                                    )
                                    SELECT
                                    COALESCE(a.ordem, 1)
                                    , COALESCE(a.consulta, 'ATENDIMENTOS')
                                    , a.area_id
                                    , a.area
                                    , a.ano
                                    , a.qtd
                                    , mes.mes_id
                                    , mes.mes_abreviacao
                                    FROM cte_atendimento a
                                    RIGHT JOIN cte_mes mes ON mes_id = a.mes

                                    UNION ALL
                                    SELECT 
                                    COALESCE(a.ordem, 2)
                                    , COALESCE(a.consulta, 'VISITAS AOS PRESOS')
                                    , a.area_id
                                    , a.area
                                    , a.ano
                                    , a.qtd
                                    , mes.mes_id
                                    , mes.mes_abreviacao
                                    FROM cte_visita a
                                    RIGHT JOIN cte_mes mes ON mes_id = a.mes

                                    UNION ALL
                                    SELECT
                                    COALESCE(a.ordem, 3)
                                    , COALESCE(a.consulta, 'AÇÕES EXTRAJUDICIAIS (SEM HOMOLOGAÇÃO JUDICIAL)')
                                    , a.area_id
                                    , a.area
                                    , a.ano
                                    , a.qtd
                                    , mes.mes_id
                                    , mes.mes_abreviacao
                                    FROM cte_ae a
                                    RIGHT JOIN cte_mes mes ON mes_id = a.mes

                                    UNION ALL
                                    SELECT 
                                    COALESCE(a.ordem, 4)
                                    , COALESCE(a.consulta, 'AÇÕES JUDICIAIS PROTOCOLADAS PELO DEFENSOR')
                                    , a.area_id
                                    , a.area
                                    , a.ano
                                    , a.qtd
                                    , mes.mes_id
                                    , mes.mes_abreviacao
                                    FROM cte_ajp a
                                    RIGHT JOIN cte_mes mes ON mes_id = a.mes

                                    UNION ALL
                                    SELECT 
                                    COALESCE(a.ordem, 5)
                                    , COALESCE(a.consulta, 'AÇÕES JUDICIAIS NÃO INICIADAS PELO DEFENSOR')
                                    , a.area_id
                                    , a.area
                                    , a.ano
                                    , a.qtd
                                    , mes.mes_id
                                    , mes.mes_abreviacao
                                    FROM cte_ajd a
                                    RIGHT JOIN cte_mes mes ON mes_id = a.mes

                                    UNION ALL
                                    SELECT 
                                    COALESCE(a.ordem, 6)
                                    , COALESCE(a.consulta, 'AUDIÊNCIAS')
                                    , a.area_id
                                    , a.area
                                    , a.ano
                                    , a.qtd
                                    , mes.mes_id
                                    , mes.mes_abreviacao
                                    FROM cte_audiencia a
                                    RIGHT JOIN cte_mes mes ON mes_id = a.mes

                                    UNION ALL
                                    SELECT
                                    COALESCE(a.ordem, 7)
                                    , COALESCE(a.consulta, 'JÚRIS')
                                    , a.area_id
                                    , a.area
                                    , a.ano
                                    , a.qtd
                                    , mes.mes_id
                                    , mes.mes_abreviacao
                                    FROM cte_juri a
                                    RIGHT JOIN cte_mes mes ON mes_id = a.mes

                                    UNION ALL
                                    SELECT
                                    COALESCE(a.ordem, 8)
                                    , COALESCE(a.consulta, 'SENTENÇAS')
                                    , a.area_id
                                    , a.area
                                    , a.ano
                                    , a.qtd
                                    , mes.mes_id
                                    , mes.mes_abreviacao
                                    FROM cte_sentenca a
                                    RIGHT JOIN cte_mes mes ON mes_id = a.mes

                                    UNION ALL
                                    SELECT
                                    COALESCE(a.ordem, 9)
                                    , COALESCE(a.consulta, 'RECURSOS')
                                    , a.area_id
                                    , a.area
                                    , a.ano
                                    , a.qtd
                                    , mes.mes_id
                                    , mes.mes_abreviacao
                                    FROM cte_recurso a
                                    RIGHT JOIN cte_mes mes ON mes_id = a.mes

                                    UNION ALL
                                    SELECT 
                                    COALESCE(a.ordem, 10)
                                    , COALESCE(a.consulta, 'DEMAIS FASES PROCESSUAIS')
                                    , a.area_id
                                    , a.area
                                    , a.ano
                                    , a.qtd
                                    , mes.mes_id
                                    , mes.mes_abreviacao
                                    FROM cte_fase a
                                    RIGHT JOIN cte_mes mes ON mes_id = a.mes

                                    $BODY$;
            """
        )
    ]
