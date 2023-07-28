# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
from freezegun import freeze_time


def migrate_data(apps, schema_editor):

    Cronometro = apps.get_model("atendimento", "Cronometro")
    AtendimentoVisualizacao = apps.get_model("atendimento", "AtendimentoVisualizacao")
    pagina = 0

    print('\nGerando registro de visualização de atendimentos a partir dos cronômetros...')

    while True:

        primeiro = pagina * 1000
        ultimo = primeiro + 1000
        registros = 0

        cronometros = Cronometro.objects.select_related(
            'atendimento',
            'servidor',
        ).filter(
            pk__range=[primeiro, ultimo]
        ).exclude(
            servidor=None,
        ).exclude(
            atendimento__defensor=None
        )

        print('Importanto de {} a {}'.format(primeiro, ultimo))

        for cron in cronometros:

            registros += 1

            if cron.atendimento.inicial_id:
                atendimento_id = cron.atendimento.inicial_id
            else:
                atendimento_id = cron.atendimento.id

            with freeze_time(cron.inicio):
                AtendimentoVisualizacao.objects.create(
                    atendimento_id=atendimento_id,
                    evento_id=cron.atendimento_id,
                    visualizado_por_id=cron.servidor.usuario_id,
                    visualizado_em=cron.inicio,
                )

        if registros == 0:
            break

        pagina += 1

    print('Concluido!')


def reverse_migrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('atendimento', '0060_perm_unificar_atendimento'),
    ]

    operations = [
        migrations.CreateModel(
            name='AtendimentoVisualizacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('visualizado_em', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('atendimento', models.ForeignKey(related_name='visualizacoes', to='atendimento.Atendimento', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('evento', models.ForeignKey(related_name='+', to='atendimento.Atendimento', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('visualizado_por', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['atendimento', '-visualizado_em'],
                'db_table': 'atendimento_atendimento_visualizacao',
            },
        ),
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
    ]
