# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('relatorios', '0012_function_buscar_primeiro_atendimento_dia'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE FUNCTION public.buscar_assistido_telefone(IN p_pessoa_id integer)
                RETURNS TABLE(pessoa_id integer, telefone_1 text, telefone_2 text, telefone_3 text, telefone_4 text, telefone_5 text, telefone_6 text) AS
                $BODY$
                BEGIN
                    RETURN QUERY SELECT ct.pessoa_id, ct.telefone_1, ct.telefone_2, ct.telefone_3, ct.telefone_4, ct.telefone_5, ct.telefone_6
                    FROM crosstab('SELECT a.pessoa_id
                    , ''telefone_'' || (RANK() OVER(partition by pessoa_id ORDER BY tel.id)) AS categoria
                    , ''('' || tel.ddd || '') '' || tel.numero AS telefone
                    FROM assistido_pessoa_telefones a
                    INNER JOIN contrib_telefone tel ON tel.id = a.telefone_id
                    WHERE a.pessoa_id = ' || CAST(p_pessoa_id AS text))
                    AS ct (pessoa_id integer, telefone_1 text, telefone_2 text, telefone_3 text, telefone_4 text, telefone_5 text, telefone_6 text);
                END;
                $BODY$
                LANGUAGE plpgsql IMMUTABLE STRICT
                COST 100
                ROWS 500;""",
            reverse_sql="""DROP FUNCTION public.buscar_assistido_telefone(integer);"""
        )
    ]
