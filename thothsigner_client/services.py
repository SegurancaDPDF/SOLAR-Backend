# -*- coding: utf-8 -*-

# Biblioteca Padrao
import requests
from requests.exceptions import ConnectionError
import json

# Bibliotecas de terceiros
from constance import config

from .exceptions import ThothsignerFailed, ThothsignerUnavailable

# função para testa a funcionalidade do assinador.


class Assinador():

    headers = {'content-type': 'application/json'}

    def testar(self):

        payload = {'content': ''}
        request = requests.post(
            "{}testar".format(config.URL_THOTH_SIGNER), data=json.dumps(payload), headers=self.headers
        )
        if request.ok:
            return request.json()
        else:
            raise ThothsignerFailed()

# função para assinar um documento utilizando o assinador.

    def assinar(self, documentobase64):

        try:
            payload = {'content': documentobase64}
            request = requests.post(
                "{}sign".format(config.URL_THOTH_SIGNER), data=json.dumps(payload), headers=self.headers
            )
        except ConnectionError:
            raise ThothsignerUnavailable()
        if request.ok:
            return request.json()
        else:
            raise ThothsignerFailed()
