# -*- coding: utf-8 -*-

# Biblioteca Padrao
import coreapi
from requests.exceptions import ConnectionError, HTTPError, ConnectTimeout
import math
from datetime import datetime

# Bibliotecas de terceiros
from constance import config
from coreapi.codecs import JSONCodec, TextCodec
from coreapi.transports.http import HTTPTransport
from openapi_codec import OpenAPICodec


class APIBase(object):
    FORMATO_DATAHORA = '%Y-%m-%dT%H:%M:%S'
    FORMATO_DATAHORA_EXTENDIDA = '%Y-%m-%dT%H:%M:%S.%f'

    listar_action = None
    read_field = None
    read_id = None
    create_encoding = None
    messages = []

    api_url = None
    api_token = None

    def __init__(self):
        pass

    def get_mensagem_conexao_indisponivel(self):
        return NotImplemented

    def esta_ativado(self):
        return NotImplemented

    def action(self, *args, **kwargs):

        if not self.esta_ativado:
            return False, self.get_mensagem_conexao_indisponivel()

        authorization = {'Authorization': 'Token {}'.format(self.api_token)}
        headers = dict(authorization)
        transport = HTTPTransport(credentials=authorization, headers=headers)

        self.client = coreapi.Client(decoders=[OpenAPICodec(), JSONCodec(), TextCodec()], transports=[transport])
        self.messages = []

        try:
            self.schema = self.client.get(self.api_url)
        except Exception as e:
            return False, 'Conexão com {} temporariamente indisponível! Motivo: {}'.format(config.NOME_PROCESSO_TJ, e)

        try:
            response = self.client.action(self.schema, *args, **kwargs)
        except coreapi.exceptions.LinkLookupError:
            return False, u'O recurso {} não foi encontrado! Verifique se o PROCAPI está atualizado!'.format(args)
        except coreapi.exceptions.ErrorMessage as e:
            # Se existir, recupera teor das mensagens adicionais do erro
            if 'messages' in e.error:
                for message in e.error.get('messages'):
                    self.messages.append(message)
            return False, list(e.error.values())[0] if e.error.values() else None
        except (ConnectionError, HTTPError, ConnectTimeout) as e:
            return False, 'Conexão com {} temporariamente indisponível! Motivo: {}'.format(config.NOME_PROCESSO_TJ, e)

        else:
            return True, response

    def listar(self, pagina=1, params={}):
        """
        Retorna uma lista com os registros do serviço (paginado)
        """

        if pagina and pagina >= 1:
            params['page'] = pagina
        else:
            params.pop('page', None)

        # Remove parâmetros nulos
        clean_params = {}
        for key in params:
            if params[key] is not None:
                clean_params[key] = params[key]

        self.pagina = pagina
        self.sucesso, self.resposta = self.action(
            [self.listar_action, 'list'],
            params=clean_params
        )

        return self.sucesso, self.resposta

    def listar_todos(self, params={}):
        """
        Retorna uma lista com todos os registros do serviço
        """

        resultado = []
        continuar = True
        pagina = 1

        while continuar:

            sucesso, resposta = self.listar(pagina=pagina, params=params)

            if sucesso:
                resultado += resposta['results']
                pagina += 1

            if not sucesso or resposta['next'] is None:
                continuar = False

        return resultado

    def consultar(self, pk, params=None):

        validate = False

        if params is None:
            params = {}
            validate = True

        params[self.read_field] = pk

        return self.action([self.listar_action, 'read'], params=params, validate=validate)

    def get(self, pk):
        sucesso, resposta = self.consultar(pk)
        if sucesso:
            return resposta
        else:
            return None

    def criar(self, **params):
        return self.action([self.listar_action, 'create'], params=params, encoding=self.create_encoding)

    def atualizar(self, **params):
        return self.action([self.listar_action, 'partial_update'], params=params, encoding=self.create_encoding)

    def excluir(self, pk):
        return self.action([self.listar_action, 'delete'], params={self.read_field: pk})

    def clear_params(self, params):
        '''
        Remove valores nulos e strings vazias dos parâmetros
        '''

        new_params = {}

        for key in params:
            if isinstance(params[key], dict):
                params[key] = self.clear_params(params[key])
            elif isinstance(params[key], list):
                for k, v in enumerate(params[key]):
                    if isinstance(v, dict):
                        params[key][k] = self.clear_params(v)
                    else:
                        params[key][k] = v
            if params[key] is not None and (type(params[key]) not in [str] or len(params[key])):
                new_params[key] = params[key]

        return new_params

    def get_page_size(self):
        return NotImplemented

    def get_page_obj(self):

        page_obj = {}

        if self.sucesso and self.pagina:

            count = self.resposta['count']
            page = self.pagina

            # Número de registros por página retornados pela API

            if self.resposta['next']:
                page_size = len(self.resposta['results'])
            else:
                page_size = self.get_page_size()

            # TODO: Criar método para aproveitar o cálculo em qualquer página
            num_pages = math.ceil(count / page_size)

            page_obj = {
                'count': count,
                'number': page,
                'paginator': {
                    'num_pages': num_pages,
                    'page_range': range(1, num_pages + 1)
                },
                'has_previous': page > 1,
                'previous_page_number': page - 1,
                'has_next': page != num_pages,
                'next_page_number': page + 1
            }

        return page_obj

    @staticmethod
    def to_datetime(value):
        if len(value) == 19:
            return datetime.strptime(value, APIBase.FORMATO_DATAHORA)
        else:
            return datetime.strptime(value, APIBase.FORMATO_DATAHORA_EXTENDIDA)
