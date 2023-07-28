# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0001_initial'),
        ('atendimento', '0021_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarefa',
            name='documentos',
            field=models.ManyToManyField(related_name='atendimento_tarefa_tarefas', to='djdocuments.Documento', blank=True),
        ),
    ]
