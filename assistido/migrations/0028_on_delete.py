# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0027_del_campo_ativo_pessoa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pessoaassistida',
            name='naturalidade_pais',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name='Pa\xeds de Origem',
                blank=True,
                to='contrib.Pais',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='pessoaassistida',
            name='moradia',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to='assistido.Moradia',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='pessoaassistida',
            name='profissao',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to='assistido.Profissao',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='documento',
            name='enviado_por',
            field=models.ForeignKey(
                related_name='+',
                on_delete=django.db.models.deletion.PROTECT,
                default=None,
                blank=True,
                to='contrib.Servidor',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='documento',
            name='excluido_por',
            field=models.ForeignKey(
                related_name='+',
                on_delete=django.db.models.deletion.PROTECT,
                default=None,
                blank=True,
                editable=False,
                to='contrib.Servidor',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='documento',
            name='pessoa',
            field=models.ForeignKey(
                related_name='documentos',
                on_delete=django.db.models.deletion.PROTECT,
                to='assistido.Pessoa'
            ),
        ),
    ]
