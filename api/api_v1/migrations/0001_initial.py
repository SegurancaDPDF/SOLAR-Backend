# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations

from api.api_v1.utils import create_chatbot_user

#  é executada durante a aplicação da migração. 
#  imprime mensagens informando sobre o resultado da criação do usuário e servidor de chatbot
def do_create_chatbot_user(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL)
    Servidor = apps.get_model('contrib', 'Servidor')
    Comarca = apps.get_model('contrib', 'Comarca')

    new_user, new_servidor, status_code = create_chatbot_user(User, Servidor, Comarca)
    if status_code == 2:
        print('\n    Nao foi possivel criar usuario e servidor para o chatbot. Nao existe nenhuma comarca cadastrada.')
        print('    Crie a comarca e execute manualmente o comando')
        print('    python manage.py criar_usuario_chatbot')
    if status_code == 1:
        print('\n    Usuario chatbot ja existe')

    if status_code == 0:
        print('\n    criado {} username: {}, pk: {}'.format(settings.AUTH_USER_MODEL, new_user.username, new_user.pk))
        print('    criado {}: pk: {}, comarca: {}'.format(
            'contrib.Servidor',
            new_servidor.pk,
            new_servidor.comarca)
        )
        print('    vinculado usuario pk: {} ao servidor pk: {}'.format(new_user.pk, new_servidor.pk))
        print('    ambos os registros estao desativados por padrao. você deve ativa-los manualmente')
    if new_user:
        new_user.is_active = False
        new_user.save()
    if new_servidor:
        new_servidor.ativo = False
        new_servidor.save()

def do_nothing(apps, schema_editor):
    pass


#  define as dependências da migração no atributo dependencies
# define as operações a serem executadas no atributo operations
class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('contrib', '0024_add_uso_interno_em_servidor'),
        ('atendimento', '0057_remove_prazo_resposta_documentos_enviados_pedido_de_apoio'),
    ]

    operations = [
        # migrations.RunPython(
        #     code=do_create_chatbot_user,
        #     reverse_code=do_nothing,
        #     atomic=True
        # )
    ]
