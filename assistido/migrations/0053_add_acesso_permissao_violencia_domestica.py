# Generated by Django 3.2 on 2022-04-06 17:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('defensor', '0019_atuacao_designacao_extraordinaria'),
        ('contrib', '0065_alter_papel'),
        ('assistido', '0052_pessoa_cadastro_protegido'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pessoa',
            options={'ordering': ['nome'], 'permissions': (('unificar_pessoa', 'Pode unificar pessoa'), ('visualizar_dados_situacao_sigilosa', 'Pode visualizar dados de pessoa em situação sigilosa'))},
        ),
        migrations.CreateModel(
            name='Acesso',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_solicitacao', models.DateTimeField(blank=True, default=None, null=True)),
                ('data_concessao', models.DateTimeField(blank=True, default=None, null=True)),
                ('data_revogacao', models.DateTimeField(blank=True, default=None, null=True)),
                ('nivel', models.SmallIntegerField(choices=[(0, 'Consulta'), (1, 'Edição'), (2, 'Administração')], default=0)),
                ('ativo', models.BooleanField(default=True)),
                ('assistido', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='assistido.pessoaassistida')),
                ('concedido_por', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='defensor.defensor')),
                ('defensoria', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='contrib.defensoria')),
                ('revogado_por', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='defensor.defensor')),
                ('servidor', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='contrib.servidor')),
            ],
        ),
    ]