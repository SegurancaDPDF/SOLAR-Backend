# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0062_perm_delete_anotacao'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='atendimento',
            options={'ordering': ['-ativo', '-numero'], 'verbose_name': 'Atendimento Geral', 'verbose_name_plural': 'Atendimentos Gerais', 'permissions': (('delete_anotacao', 'Can delete anota\xe7\xe3o'), ('agendar_com_bloqueio', 'Pode agendar em dia com bloqueio (feriado)'), ('view_all_atendimentos', 'Can view all atendimentos'), ('view_129', 'Can view 129'), ('view_recepcao', 'Can view Recep\xe7\xe3o'), ('view_defensor', 'Can view Defensor'), ('view_distribuicao', 'Can view Distribui\xe7\xe3o'), ('unificar_atendimento', 'Pode unificar atendimento'), ('requalificar_atendimento_retroativo', 'Pode requalificar atendimento retroativo'))},
        ),
    ]
