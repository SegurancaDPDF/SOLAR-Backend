# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0024_tipo_pessoa_obrigatorio_pessoa_perfilcamposobrigatorios'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filiacao',
            name='pessoa_assistida',
            field=models.ForeignKey(related_name='filiacoes', to='assistido.PessoaAssistida', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
