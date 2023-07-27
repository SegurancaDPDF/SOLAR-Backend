# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0011_prisao_origem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prisao',
            name='estabelecimento_penal',
            field=models.ForeignKey(verbose_name='Estabelecimento Penal', to='nadep.EstabelecimentoPenal', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AlterField(
            model_name='prisao',
            name='local_prisao',
            field=models.ForeignKey(verbose_name='Munic\xedpio do Local da Pris\xe3o', to='contrib.Municipio', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AlterField(
            model_name='prisao',
            name='tipificacao',
            field=models.ForeignKey(verbose_name='Tipifica\xe7\xe3o', to='nadep.Tipificacao', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
