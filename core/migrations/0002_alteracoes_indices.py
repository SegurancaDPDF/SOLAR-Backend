# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
       # ('reversion', '0002_auto_20141216_1509'),
    ]

    operations = [
        migrations.RunSQL(
            sql='DROP INDEX IF EXISTS reversion_version_0c9ba3a3;',
            reverse_sql="""CREATE INDEX reversion_version_0c9ba3a3
                            ON public.reversion_version
                            USING btree (object_id_int);"""
        ),
        migrations.RunSQL(
            sql='DROP INDEX IF EXISTS reversion_version_417f1b1c;',
            reverse_sql="""CREATE INDEX reversion_version_417f1b1c
                            ON public.reversion_version
                            USING btree (content_type_id);"""
        ),
        migrations.RunSQL(
            sql='DROP INDEX IF EXISTS reversion_version_5de09a8d;',
            reverse_sql="""CREATE INDEX reversion_version_5de09a8d
                            ON public.reversion_version
                            USING btree (revision_id);"""
        ),
        migrations.RunSQL(
            sql='DROP INDEX IF EXISTS reversion_revision_b16b0f06',
            reverse_sql="""CREATE INDEX reversion_revision_b16b0f06
                            ON public.reversion_revision
                            USING btree (manager_slug COLLATE pg_catalog."default");"""
        ),
        migrations.RunSQL(
            sql='DROP INDEX IF EXISTS reversion_revision_c69e55a4',
            reverse_sql="""CREATE INDEX reversion_revision_c69e55a4
                            ON public.reversion_revision
                            USING btree (date_created);"""
        ),
        migrations.RunSQL(
            sql='DROP INDEX IF EXISTS reversion_revision_manager_slug_54d21219582503b1_like',
            reverse_sql="""CREATE INDEX reversion_revision_manager_slug_54d21219582503b1_like
                            ON public.reversion_revision
                            USING btree (manager_slug COLLATE pg_catalog."default" varchar_pattern_ops);"""
        ),
        migrations.RunSQL(
            sql='DROP INDEX IF EXISTS reversion_revision_e8701ad4;',
            reverse_sql="""CREATE INDEX reversion_revision_e8701ad4
                            ON public.reversion_revision
                            USING btree (user_id);"""
        ),
        migrations.RunSQL(
            sql='DROP INDEX IF EXISTS public.pf_data_protocolo_2015;',
            reverse_sql="""CREATE INDEX IF NOT EXISTS pf_data_protocolo_2015
                            ON public.processo_fase
                            USING btree (data_protocolo DESC NULLS LAST)
                            WITH(FILLFACTOR=90)
                            WHERE data_protocolo >= '2015-01-01 00:00:00-03'::timestamp with time zone
                            AND data_protocolo <= '2015-12-31 00:00:00-03'::timestamp with time zone;"""
        ),
        migrations.RunSQL(
            sql='DROP INDEX IF EXISTS public.pf_data_protocolo_2016;',
            reverse_sql="""CREATE INDEX IF NOT EXISTS pf_data_protocolo_2016
                            ON public.processo_fase
                            USING btree (data_protocolo DESC NULLS LAST)
                            WITH (FILLFACTOR=90)
                            WHERE data_protocolo >= '2016-01-01 00:00:00-03'::timestamp with time zone
                            AND data_protocolo <= '2016-12-31 00:00:00-03'::timestamp with time zone;"""
        ),
        migrations.RunSQL(
            sql='DROP INDEX IF EXISTS public.pf_data_protocolo_2017;',
            reverse_sql="""CREATE INDEX IF NOT EXISTS pf_data_protocolo_2017
                            ON public.processo_fase
                            USING btree (data_protocolo DESC NULLS LAST)
                            WITH (FILLFACTOR=90)
                            WHERE data_protocolo >= '2017-01-01 00:00:00-03'::timestamp with time zone
                            AND data_protocolo <= '2017-12-31 00:00:00-03'::timestamp with time zone;"""
        ),
        migrations.RunSQL(
            sql='DROP INDEX IF EXISTS public.pf_data_protocolo_antigo;',
            reverse_sql="""CREATE INDEX IF NOT EXISTS pf_data_protocolo_antigo
                            ON public.processo_fase
                            USING btree (data_protocolo DESC NULLS LAST)
                            WITH (FILLFACTOR=90)
                            WHERE data_protocolo < '2015-01-01 00:00:00-03'::timestamp with time zone;"""
        ),
        migrations.RunSQL(
            sql='DROP INDEX IF EXISTS public.processo_processo_698d95a8;',
            reverse_sql="""CREATE INDEX IF NOT EXISTS processo_processo_698d95a8
                            ON public.processo_processo
                            USING btree (cadastrado_por_id);"""
        ),
        migrations.RunSQL(
            sql="""CREATE INDEX IF NOT EXISTS atendimento_ativo
                        ON atendimento_atendimento
                        USING btree (ativo) WITH (fillfactor='70')""",
            reverse_sql='DROP INDEX IF EXISTS atendimento_ativo'
        )
    ]
