# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('relatorios', '0018_functions_ausentes'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE FUNCTION public.buscar_assistido_filiacao(IN p_pessoa_assistida_id integer)
                  RETURNS TABLE(pessoa_assistida_id integer, filiacao_1 character varying, filiacao_2 character varying, filiacao_3 character varying, filiacao_4 character varying) AS
                $BODY$
                                BEGIN
                                    RETURN QUERY SELECT ct.pessoa_assistida_id, ct.filiacao_1, ct.filiacao_2, ct.filiacao_3, ct.filiacao_4
                                    FROM crosstab('SELECT a.pessoa_assistida_id
                                    , ''filiacao_'' || (RANK() OVER(partition by pessoa_assistida_id ORDER BY a.tipo)) AS categoria
                                    , a.nome AS nome
                                    FROM assistido_filiacao a
                                    WHERE a.pessoa_assistida_id = ' || CAST(p_pessoa_assistida_id AS text))
                                    AS ct (pessoa_assistida_id integer, filiacao_1 varchar(256), filiacao_2 varchar(256), filiacao_3 varchar(256), filiacao_4 varchar(256));
                                END;
                                $BODY$
                  LANGUAGE plpgsql IMMUTABLE STRICT
                  COST 100
                  ROWS 10;
            """,
            reverse_sql="DROP FUNCTION public.buscar_assistido_filiacao(integer);"
        )
    ]
