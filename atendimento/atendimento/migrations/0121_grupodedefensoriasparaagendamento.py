# Generated by Django 3.2 on 2022-10-09 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0068_historicologin'),
        ('atendimento', '0120_add_tipo_qualificacao_botao_remeter'),
    ]

    operations = [
        migrations.CreateModel(
            name='GrupoDeDefensoriasParaAgendamento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=256, verbose_name='Nome')),
                ('ativo', models.BooleanField(default=True)),
                ('defensorias', models.ManyToManyField(blank=True, default=None, related_name='grupos_de_agendamento', to='contrib.Defensoria')),
            ],
            options={
                'verbose_name': 'Grupo de Agendamento',
                'verbose_name_plural': 'Grupos de Agendamento',
                'ordering': ['-ativo', 'nome'],
            },
        ),
    ]