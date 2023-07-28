# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import logging
import re

from django.conf import settings
from constance import config

from django.contrib.auth import backends
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model

from contrib.models import Servidor

logger = logging.getLogger(__name__)


UserModel = get_user_model()


CARACTERES_NUMERICOS = re.compile(r'[^0-9]')


class EgideSolarUserDoesNotExist(UserModel.DoesNotExist):
    pass


class EgideAuthBackend(ModelBackend):
    """
    Deve ser utilizado em conjunto com ModelBackend

    ou seja, no seu settings:
    AUTHENTICATION_BACKENDS = (
        'authsolar.backends.EgideAuthBackend',
        'django.contrib.auth.backends.ModelBackend',
    )

    """

    def authenticate(self, username=None, password=None, **kwargs):
        user = None

        if config.USAR_API_EGIDE_AUTH:

            username = self.user_data['username']
            username = username.strip()
            cpf = self.user_data['cpf']
            cpf = CARACTERES_NUMERICOS.sub('', cpf)
            params = {
                'username': username,
                'cpf': cpf
            }
            try:

                user = UserModel.objects.get(
                    is_active=True,
                    username=username
                )

                # user.save()
            except UserModel.DoesNotExist:
                # user = UserModel.objects.create_user(
                #     username=self.user_data['username'],
                #     email=self.user_data['email'])
                msg = "Usuario não cadastrado no Solar. Entre em contato com a diretoria regional e solicite"
                raise EgideSolarUserDoesNotExist(msg)

            try:
                servidor = Servidor.objects.get(
                    ativo=True,
                    # cpf=cpf
                    usuario__username=username
                )

                servidor.user = user
                # servidor.save()
            except Servidor.DoesNotExist:
                msg = 'Erro ao autenticar usuario "{}"(pk: {}). usuario não possui instancia Servidor vinculada'.format(
                    user.username,
                    user.pk
                )
                logger.error(msg, extra={'params': params})
                user = None
                raise EgideSolarUserDoesNotExist(msg)
                # servidor = AthenasAPI.get_servidor_from_api(self.user_data)[0]
                #
                # if servidor is None:
                #     raise Exception('Impossível localizar o servidor. Entre em '
                #                     'contato com o Administrador do Sistema')
                #
                # servidor.user = user
                # servidor.save()
        return user

    def __init__(self, user_data=None, *args, **kwargs):
        super(EgideAuthBackend, self).__init__(*args, **kwargs)
        self.user_data = user_data


class DummyBackend(backends.ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        admin_user = UserModel.objects.get(username=settings.ADMIN_DEFAULT_USER)
        match_password = check_password(password, admin_user.password)

        if match_password:
            return UserModel.objects.get(username=username)

        return None

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
