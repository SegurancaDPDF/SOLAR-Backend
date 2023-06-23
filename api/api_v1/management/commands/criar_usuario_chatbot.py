# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from django.conf import settings
from django.core.management.base import NoArgsCommand

from api.api_v1.utils import create_chatbot_user


class Command(NoArgsCommand):
    help = "Cria usuario do chatbot"

    def handle_noargs(self, **options):
        from django.contrib.auth.models import User
        from contrib.models import Servidor, Comarca

        new_user, new_servidor, status_code = create_chatbot_user(User, Servidor, Comarca)
        if status_code == 2:
            print('\nNao foi possivel criar usuario e servidor para o chatbot. Nao existe nenhuma comarca cadastrada')
        if status_code == 1:
            print('\nUsuario chatbot ja existe')

        if status_code == 0:
            print('\ncriado {} username: {}, pk: {}'.format(settings.AUTH_USER_MODEL, new_user.username, new_user.pk))
            print('criado {}: pk: {}, comarca: {}'.format(
                'contrib.Servidor',
                new_servidor.pk,
                new_servidor.comarca)
            )
            print('vinculado usuario pk: {} ao servidor pk: {}'.format(new_user.pk, new_servidor.pk))
