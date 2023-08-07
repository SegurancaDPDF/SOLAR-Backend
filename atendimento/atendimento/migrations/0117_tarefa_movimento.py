# Generated by Django 3.2 on 2022-06-22 13:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('propac', '0002_tipoanexodocumentopropac_ativo'),
        ('atendimento', '0116_vw_atendimento_defensor_historico_agendamento'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarefa',
            name='movimento',
            field=models.ForeignKey(blank=True, help_text='Movimento de Propac ou Procedimento.', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='tarefas', to='propac.movimento', verbose_name='movimento (propac/procedimento)'),
        ),
    ]