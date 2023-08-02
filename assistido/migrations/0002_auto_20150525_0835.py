# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Bibliotecas de terceiros
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0001_initial'),
        ('contrib', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pessoa',
            name='enderecos',
            field=models.ManyToManyField(to='contrib.Endereco', blank=True),
        ),
        migrations.AddField(
            model_name='pessoa',
            name='telefones',
            field=models.ManyToManyField(to='contrib.Telefone', blank=True),
        ),
        migrations.AddField(
            model_name='patrimonio',
            name='pessoa',
            field=models.OneToOneField(null=True, default=None, blank=True, to='assistido.Pessoa', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='movel',
            name='patrimonio',
            field=models.ForeignKey(related_name='moveis', to='assistido.Patrimonio', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='moradia',
            name='estrutura',
            field=models.ManyToManyField(to='assistido.EstruturaMoradia', blank=True),
        ),
        migrations.AddField(
            model_name='imovel',
            name='patrimonio',
            field=models.ForeignKey(related_name='imoveis', to='assistido.Patrimonio', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='documento',
            name='documento',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Documento', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='documento',
            name='enviado_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='documento',
            name='pessoa',
            field=models.ForeignKey(to='assistido.Pessoa', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='pessoaassistida',
            name='bens',
            field=models.ManyToManyField(to='assistido.Bem', blank=True),
        ),
        migrations.AddField(
            model_name='pessoaassistida',
            name='deficiencias',
            field=models.ManyToManyField(to='contrib.Deficiencia', blank=True),
        ),
        migrations.AddField(
            model_name='pessoaassistida',
            name='moradia',
            field=models.ForeignKey(blank=True, to='assistido.Moradia', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='pessoaassistida',
            name='naturalidade_pais',
            field=models.ForeignKey(blank=True, to='contrib.Pais', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='pessoaassistida',
            name='profissao',
            field=models.ForeignKey(blank=True, to='assistido.Profissao', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='filiacao',
            name='pessoa_assistida',
            field=models.ForeignKey(to='assistido.PessoaAssistida', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
