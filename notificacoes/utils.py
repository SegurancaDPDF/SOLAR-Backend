# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import logging

import requests
from constance import config
from django.conf import settings
from django.db.models.query import QuerySet
import six

# registrar mensagens de log.
logger = logging.getLogger(__name__)

#  função responsável por enviar notificações.
# armazenar informações relacionadas ao CPF dos usuários.
# Verifica se o modo de depuração está ativado.
def send_notify(mensagem, titulo, url_callback, users_destinatarios_list, user_remetente=None, notification_module=None, notification_type=None, app='SOLAR', debug=settings.DEBUG):  # noqa

    if config.USAR_NOTIFICACOES_SIGNO:

        cpf = ''
        cpfs = []

        if user_remetente and hasattr(user_remetente, 'servidor') and user_remetente.servidor.cpf:
            cpf = user_remetente.servidor.cpf

        if users_destinatarios_list:

            if isinstance(users_destinatarios_list, (tuple, list, set, QuerySet)):
                for user in users_destinatarios_list:
                    if user.is_active and hasattr(user, 'servidor') and user.servidor.ativo and user.servidor.cpf:
                        cpfs.append(user.servidor.cpf)

        if cpfs:

            cpfs_users_destinatarios = ' '.join(cpfs)

            if not titulo:
                titulo = ''

            if debug:
                print('cpfs_users_destinatarios:')
                print(cpfs_users_destinatarios)
                print('cpf:')
                print(cpf)
                print('title:')
                print(titulo)
                print('content:')
                print(mensagem)
                print('app:')
                print(app)
                print('link:')
                print(url_callback)

            payload = {
                'notification[title]': '{}'.format(titulo),
                'notification[content]': '{}'.format(mensagem),
                'notification[app]': app,
                'notification[sender]': cpf,
                'notification[link]': url_callback,
                'notification[users]': cpfs_users_destinatarios
            }

            if notification_module and isinstance(notification_module, six.string_types):
                payload['notification[module]'] = notification_module

            if notification_type and isinstance(notification_type, six.string_types):
                payload['notification[type]'] = notification_type

            response = requests.post(
                url=settings.SIGNO_REST_API_URL,
                headers={'user-agent': 'solar/{}'.format(settings.VERSION)},
                data=payload)

            if debug:
                print('response:')
                print(response)
                print('response status code:')
                print(response.status_code)
                print('response content:')
                print(response.content)

            if response.status_code != 201:
                logger.error('Erro ao enviar notificação para o SIGNO', payload)

            return response
