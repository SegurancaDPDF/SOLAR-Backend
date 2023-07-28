# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def migrate_data(apps, schema_editor):
    Atendimento = apps.get_model("atendimento", "Atendimento")
    AtendimentoParticipante = apps.get_model("atendimento", "AtendimentoParticipante")

    participantes = Atendimento.participantes.through.objects.all()

    para_inserir = []
    for p in participantes:

        para_inserir.append(
            AtendimentoParticipante(id=p.id, atendimento_id=p.atendimento_id, servidor_id=p.servidor_id)
        )

    AtendimentoParticipante.objects.bulk_create(para_inserir)


def reverse_migrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('contrib', '0019_cargo'),
        ('atendimento', '0051_impedimento_anotacao_comunicacao'),
    ]

    operations = [
        migrations.CreateModel(
            name='AtendimentoParticipante',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('atendimento',
                 models.ForeignKey(related_name='participantes_atendimentos', to='atendimento.Atendimento', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('servidor', models.ForeignKey(related_name='participantes_atendimentos', to='contrib.Servidor', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='atendimentoparticipante',
            unique_together=set([('atendimento', 'servidor')]),
        ),
        migrations.RunSQL(
            sql="""SELECT setval('atendimento_atendimentoparticipante_id_seq', 
                                  (SELECT last_value FROM atendimento_atendimento_participantes_id_seq)+1);
            """,
            reverse_sql="""SELECT setval('atendimento_atendimentoparticipante_id_seq', 1);"""
        ),
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
    ]
