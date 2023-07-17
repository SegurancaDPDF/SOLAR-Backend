# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('relatorios', '0027_permissao_perfil_assistidos_atendimento'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE FUNCTION public.buscar_quantitativo_ged_finalizado(
                p_ano integer DEFAULT 2019,
                p_tipo_documento_id integer DEFAULT 0,
                p_comarca_id integer DEFAULT 0,
                p_defensor_id integer DEFAULT 0,
                p_defensoria_id integer DEFAULT 0,
                p_diretoria_id integer DEFAULT 0)
                RETURNS TABLE(tipo_documento_id integer, tipo_documento character varying, defensor_id integer, defensoria_id integer, comarca_id integer, diretoria_id integer, ano smallint, mes smallint, mes_abreviacao character varying, qtd bigint)
                LANGUAGE 'sql'
                COST 100
                IMMUTABLE
                ROWS 100
            AS $BODY$

            WITH cte_mes AS (
                SELECT CAST(1 AS SMALLINT) mes_id, CAST('JAN' AS VARCHAR) mes_abreviacao
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
            ),
            cte_ged AS (
                SELECT
                tip.id tipo_documento_id,
                tip.titulo tipo_documento,
                -- ass.id assinatura_id,
                ass.grupo_assinante_id,
                -- ass.grupo_assinante_nome,
                ass.assinado_por_id,
                CAST(date_part('year', doc.data_assinado) AS SMALLINT) ano,
                CAST(date_part('month', doc.data_assinado) AS SMALLINT) mes,
                -- ass.assinado_nome,
                -- doc.id documento_id,
                -- doc.finalizado_por_id,
                -- doc.finalizado_por_nome
                com.id comarca_id,
                dir.id diretoria_id,
                COUNT(*) qtd
                FROM djdocuments_assinatura ass
                INNER JOIN djdocuments_documento doc ON doc.id = ass.documento_id
                    AND ass.esta_assinado = true
                    AND ass.ativo = true
                    AND doc.esta_assinado = true
                    AND doc.esta_ativo = true
                    AND doc.is_removed = false
                    AND doc.eh_modelo_padrao = false
                    AND doc.eh_modelo = false
                    AND doc.finalizado_por_id IS NOT NULL
                    AND date_part('year', doc.data_assinado) = p_ano
                    AND (doc.tipo_documento_id = p_tipo_documento_id OR p_tipo_documento_id = 0)
                INNER JOIN djdocuments_tipodocumento tip ON tip.id = doc.tipo_documento_id
                INNER JOIN contrib_defensoria def ON def.id = ass.grupo_assinante_id
                    AND (def.id = p_defensoria_id OR p_defensoria_id = 0)
                INNER JOIN contrib_comarca com ON com.id = def.comarca_id
                     AND (0 = p_comarca_id OR com.id = p_comarca_id)
                INNER JOIN contrib_comarca dir ON dir.id = CASE WHEN com.coordenadoria_id IS NULL THEN com.id ELSE com.coordenadoria_id END
                    AND (0 = p_diretoria_id OR dir.id = p_diretoria_id)
                GROUP BY
                    tip.id,
                    tip.titulo,
                    ass.grupo_assinante_id,
                    ass.assinado_por_id,
                    ano,
                    mes,
                    com.id,
                    dir.id
            )
            SELECT
            ged.tipo_documento_id,
            ged.tipo_documento,
            ged.assinado_por_id as defensor_id,
            ged.grupo_assinante_id as defensoria_id,
            ged.comarca_id,
            ged.diretoria_id,
            ged.ano,
            ged.mes,
            mes.mes_abreviacao,
            COALESCE(ged.qtd, 0)
            FROM cte_ged ged
            RIGHT JOIN cte_mes mes ON mes.mes_id = ged.mes

            $BODY$;
                """,
            reverse_sql="""
                DROP FUNCTION public.buscar_quantitativo_ged_finalizado(
                    integer, integer, integer, integer, integer, integer
                );
                """
        ),
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE FUNCTION public.buscar_quantitativo_get_finalizado_crosstab(
                p_ano integer DEFAULT 2019,
                p_tipo_documento_id integer DEFAULT 0,
                p_comarca_id integer DEFAULT 0,
                p_defensor_id integer DEFAULT 0,
                p_defensoria_id integer DEFAULT 0,
                p_diretoria_id integer DEFAULT 0)
                RETURNS TABLE(tipo_documento character varying, jan integer, fev integer, mar integer, abr integer, mai integer, jun integer, jul integer, ago integer, set integer, "out" integer, nov integer, dez integer, total integer)
                LANGUAGE 'plpgsql'
                COST 100
                IMMUTABLE STRICT
                ROWS 1000
            AS $BODY$
                DECLARE consulta TEXT;
                BEGIN
                  consulta := 'SELECT tipo_documento, mes, SUM(COALESCE(qtd, 0)) AS qtd FROM public.buscar_quantitativo_ged_finalizado('
                  || p_ano || ', '
                  || p_tipo_documento_id || ', '
                  || p_comarca_id || ', '
                  || p_defensor_id || ', '
                  || p_defensoria_id || ', '
                  || p_diretoria_id || ') GROUP BY tipo_documento_id, tipo_documento, mes ORDER BY tipo_documento';

                  RETURN QUERY	WITH cte_cross (tipo_documento, jan, fev, mar, abr, mai, jun, jul, ago, set, out, nov, dez) AS (
                        SELECT * FROM crosstab(consulta , 'SELECT * FROM generate_series(1, 12)')
                        AS ct (tipo_documento VARCHAR, "Jan" INTEGER, "Fev" INTEGER, "Mar" INTEGER, "Abr" INTEGER,
                           "Mai" INTEGER, "Jun" INTEGER, "Jul" INTEGER, "Ago" INTEGER, "Set" INTEGER, "Out" INTEGER, "Nov" INTEGER, "Dez" INTEGER)
                      WHERE ct.tipo_documento IS NOT NULL
                        )
                      SELECT cte_cross.tipo_documento,
                      COALESCE(cte_cross.jan, 0) jan,
                      COALESCE(cte_cross.fev, 0) fev,
                      COALESCE(cte_cross.mar, 0) mar,
                      COALESCE(cte_cross.abr, 0) abr,
                      COALESCE(cte_cross.mai, 0) mai,
                      COALESCE(cte_cross.jun, 0) jun,
                      COALESCE(cte_cross.jul, 0) jul,
                      COALESCE(cte_cross.ago, 0) ago,
                      COALESCE(cte_cross.set, 0) AS set,
                      COALESCE(cte_cross.out, 0) AS out,
                      COALESCE(cte_cross.nov, 0) nov,
                      COALESCE(cte_cross.dez, 0) dez,
                      COALESCE(cte_cross.jan, 0) + COALESCE(cte_cross.fev, 0) + COALESCE(cte_cross.mar, 0) + COALESCE(cte_cross.abr, 0) +
                        COALESCE(cte_cross.mai, 0) + COALESCE(cte_cross.jun, 0) + COALESCE(cte_cross.jul, 0) + COALESCE(cte_cross.ago, 0) +
                        COALESCE(cte_cross.set, 0) + COALESCE(cte_cross.out, 0) + COALESCE(cte_cross.nov, 0) + COALESCE(cte_cross.dez, 0) as total
                      FROM cte_cross
                      ;
                END;
            $BODY$;
            """,
            reverse_sql="""
                DROP FUNCTION public.buscar_quantitativo_get_finalizado_crosstab(
                    integer, integer, integer, integer, integer, integer
                );
            """
        )
    ]
