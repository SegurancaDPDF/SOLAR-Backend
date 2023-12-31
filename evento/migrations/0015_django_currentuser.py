# Generated by Django 3.2 on 2023-06-06 20:56

from django.conf import settings
from django.db import migrations
import django.db.models.deletion
import django_currentuser.db.models.fields
import django_currentuser.middleware


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('evento', '0014_evento_evento_evento_idx_001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoria',
            name='cadastrado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='evento_categoria_cadastrado_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='categoria',
            name='modificado_por',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.SET_NULL, on_update=True, related_name='evento_categoria_modificado_por', to=settings.AUTH_USER_MODEL),
        ),
    ]
