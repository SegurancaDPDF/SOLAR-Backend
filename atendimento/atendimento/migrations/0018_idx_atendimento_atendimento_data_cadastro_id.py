# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0017_auto_20160607_1436'),
    ]

    operations = [
        migrations.RunSQL(
            sql="CREATE INDEX idx_atendimento_atendimento_data_cadastro_id ON atendimento_atendimento (date(data_cadastro AT TIME ZONE 'UTC'), id);",
            reverse_sql="DROP INDEX idx_atendimento_atendimento_data_cadastro_id;")
    ]
