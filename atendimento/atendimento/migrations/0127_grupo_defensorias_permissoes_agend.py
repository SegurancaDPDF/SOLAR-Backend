# Generated by Django 3.2 on 2023-01-23 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0126_perm_atendimento_atender_sem_liberar'),
    ]

    operations = [
        migrations.AddField(
            model_name='grupodedefensoriasparaagendamento',
            name='aceitar_agend_extrapauta',
            field=models.BooleanField(default=False, help_text='Permitir que as defensorias do grupo e o disk 129 agendem na extra-pauta', verbose_name='Aceitar agendamento na extra-pauta'),
        ),
        migrations.AddField(
            model_name='grupodedefensoriasparaagendamento',
            name='aceitar_agend_pauta',
            field=models.BooleanField(default=True, help_text='Permitir que as defensorias do grupo e o disk 129 agendem na pauta', verbose_name='Aceitar agendamento na pauta'),
        ),
    ]