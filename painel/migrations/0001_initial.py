# Generated by Django 3.2 on 2021-10-21 12:13

import cuser.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

# migrações no Django

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('atendimento', '0107_add_cpf_requerente_e_id_defensoria_views_recepcao'),
        ('comarca', '0005_on_delete'),
    ]

    operations = [
        migrations.CreateModel(
            name='Painel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(blank=True, null=True)),
                ('tipo', models.IntegerField(choices=[(0, 'Painel da Recepção'), (1, 'Painel do Defensor')], db_index=True, default=0)),
                ('atendimento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='atendimento.defensor')),
                ('cadastrado_por', cuser.fields.CurrentUserField(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='painel_painel_cadastrado_por', to=settings.AUTH_USER_MODEL)),
                ('desativado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='painel_painel_desativado_por', to=settings.AUTH_USER_MODEL)),
                ('modificado_por', cuser.fields.CurrentUserField(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='painel_painel_modificado_por', to=settings.AUTH_USER_MODEL)),
                ('predio', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='comarca.predio')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
