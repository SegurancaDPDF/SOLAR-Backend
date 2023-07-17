# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('relatorios', '0011_function_buscar_quantitativo_atividade_geral'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE FUNCTION public.buscar_primeiro_atendimento_dia(
                    IN p_data_inicial date DEFAULT '2017-01-01'::date,
                    IN p_data_final date DEFAULT '2017-05-31'::date,
                    IN p_comarca_id integer DEFAULT '-1'::integer,
                    IN p_defensor_id integer DEFAULT 0)
                RETURNS TABLE(semana integer, seg timestamp without time zone, ter timestamp without time zone, qua timestamp without time zone, qui timestamp without time zone, sex timestamp without time zone, sab timestamp without time zone, dom timestamp without time zone) AS
                $BODY$
                DECLARE consulta text;
                BEGIN
                /*
                    Busca o primeiro atendimento de cada dia realizado pelo Defensor.
                */

                consulta := 'WITH cte_calendario AS ('
                        || ' SELECT'
                        || ' CAST(date_part(''week'', AA.data_atendimento) AS SMALLINT) semana,'
                        || ' CAST(EXTRACT(ISODOW FROM AA.data_atendimento) AS SMALLINT) dia,'
                        || ' min(AA.data_atendimento) data_atendimento'
                        || ' FROM atendimento_defensor AD'
                        || ' INNER JOIN atendimento_atendimento AA ON AD.atendimento_ptr_id = AA.id'
                        || ' 	AND AA.ativo = TRUE'
                        || ' 	AND AA.remarcado_id IS NULL'
                        || ' 	AND AA.tipo IN (1, 2, 4, 7, 9)'
                        || ' 	AND AD.comarca_id = ' || p_comarca_id
                        || '    AND AA.data_atendimento::DATE BETWEEN ''' || p_data_inicial || ''' AND ''' || p_data_final || ''''
                        || '    AND ((AD.defensor_id = ' || p_defensor_id || ' AND AD.substituto_id IS NULL) OR AD.substituto_id = ' || p_defensor_id || ')'
                        || ' INNER JOIN defensor_defensor DD ON DD.id = ' || p_defensor_id 
                        || ' AND DD.servidor_id = AA.atendido_por_id'
                        || ' GROUP BY date_part(''week'', AA.data_atendimento), EXTRACT(ISODOW FROM AA.data_atendimento)'
                    || ')'
                    || ' SELECT'
                    || ' a.semana'
                    || ' , a.dia'
                    || ' , a.data_atendimento AS data_atendimento'
                    || '  FROM cte_calendario a'
                    || ' ORDER BY a.semana, a.data_atendimento';

                RETURN QUERY SELECT * FROM crosstab(consulta, 'SELECT m FROM generate_series(1,7) m'
                ) AS ct (semana int, "Seg" timestamp, "Ter" timestamp, "Qua" timestamp, "Qui" timestamp, "Sex" timestamp, "Sab" timestamp, "Dom" timestamp);

                END;
                $BODY$
                LANGUAGE plpgsql IMMUTABLE STRICT
                COST 100
                ROWS 1000;""",
            reverse_sql="""
                DROP FUNCTION
                public.buscar_primeiro_atendimento_dia
                (date, date, integer, integer)"""
        )
    ]
