# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0004_auto_20150611_0956'),
        ('processo', '0009_processo_situacao'),
        ('nadep', '0023_auto_20160415_1608'),
    ]

    operations = [
        migrations.CreateModel(
            name='Soltura',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipo', models.SmallIntegerField(verbose_name='Situa\xe7\xe3o', choices=[(1, 'Dec. Ju\xedz do Ato Convers\xe3o em Flagrante'), (2, 'Habeas Corpus'), (3, 'Liberdade Provis\xf3ria'), (4, 'Pagamento de Fian\xe7a'), (5, 'Revoga\xe7\xe3o de Pris\xe3o Preventiva'), (6, 'Senten\xe7a Absolut\xf3ria')])),
                ('historico', models.TextField(default=None, null=True, blank=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('data_exclusao', models.DateTimeField(verbose_name='Data de Exclus\xe3o', null=True, editable=False)),
                ('ativo', models.BooleanField(default=True)),
                ('aprisionamento', models.OneToOneField(to='nadep.Aprisionamento', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('cadastrado_por', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('excluido_por', models.ForeignKey(related_name='+', default=None, blank=True, editable=False, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('processo', models.ForeignKey(default=None, blank=True, to='processo.Processo', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
        ),
        migrations.AlterModelOptions(
            name='mudancaregime',
            options={'ordering': ['prisao__pessoa__nome', 'data_registro'], 'verbose_name': 'Mudan\xe7a de Regime', 'verbose_name_plural': 'Mudan\xe7as de Regime'},
        ),
    ]
