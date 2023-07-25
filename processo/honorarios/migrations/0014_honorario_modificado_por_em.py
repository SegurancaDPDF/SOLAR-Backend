# Generated by Django 3.2 on 2022-12-13 16:42

import cuser.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('honorarios', '0013_honorario_atendimento'),
    ]

    operations = [
        migrations.AddField(
            model_name='honorario',
            name='modificado_em',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='honorario',
            name='modificado_por',
            field=cuser.fields.CurrentUserField(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='honorarios_honorario_modificado_por', to=settings.AUTH_USER_MODEL),
        ),
    ]
