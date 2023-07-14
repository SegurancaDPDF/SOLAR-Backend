# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import logging
import json
import ldap
import mimetypes
import os
import pathlib
import re
import requests
import six
import uuid
import ffmpeg

from constance import config
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.core.files import File
from django.urls import reverse
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from django.template.response import SimpleTemplateResponse
from django.core.mail import BadHeaderError, send_mail
from ldap.filter import filter_format
from PIL import Image
from pydub import AudioSegment
from reportlab.pdfgen.canvas import Canvas

from djdocuments.views.documentos import PrintPDFConfiguracaoMixin
from wkhtmltopdf.utils import render_pdf_from_template

from .models import Cartorio, Estado, Municipio, Papel, Servidor
from .utils import criar_username_de_nome
from .validators import validate_CPF

CARACTERES_NUMERICOS = re.compile(r'[^0-9]')

logger = logging.getLogger(__name__)

__all__ = (
    'CARACTERES_NUMERICOS',
    'consultar_api_athenas',
    'LDAPAPI',
    'buscar_servidor_api_athenas_e_ldap'
)


def consultar_api_athenas(cpf=None, matricula=None, username=None, buscar_supervisor=True):
    """

    :param cpf:
    :param matricula:
    :param username:
    :param buscar_supervisor:
    :return: {} se não localizar ou dict no formato:
            {
                'cpf': str or None,
                'first_name': str or None
                'nome': str or None,
                'matricula': str or None,
                'email': str or None,
                'username': str or None,
                'sexo': str or None,
                'foto': str or None,
                'defensor_supervisor': defensor.Defensor instance or None,
                'esta_ativo': boolean,
                'athenas_offline': boolean
            }

    """
    dados = {}
    athenas_online = True
    try:
        if cpf:
            querystring = 'pessoa_fisica__cpf'
            valor = CARACTERES_NUMERICOS.sub('', cpf)
        elif matricula:
            querystring = 'matricula'
            valor = matricula
        else:
            querystring = 'user__username'
            valor = username
        ATHENAS_API_URL = settings.ATHENAS_API_URL
        if ATHENAS_API_URL and ATHENAS_API_URL[-1] != "/":
            ATHENAS_API_URL = "{}/".format(ATHENAS_API_URL)
        r = requests.get(
            "{}servidores/?{}={}".format(ATHENAS_API_URL, querystring, valor))
    except Exception:
        athenas_online = False  # noqa
    else:
        resultado = None
        try:
            resultado = r.json()["results"]
        except Exception:
            pass

        if resultado:
            resultado = resultado[0]
            ativo = resultado['ativo']

            dados = {
                'cpf': resultado['cpf'],
                'first_name': None,
                'nome': resultado['nome'],
                'matricula': resultado['matricula'],
                'email': resultado['email'],
                'username': None,
                'sexo': None,
                'foto': None,
                'defensor_supervisor': None,
                'esta_ativo': ativo,
            }

            if resultado['user']:
                dados['username'] = resultado['user']['username']

            if buscar_supervisor:
                if resultado['chefe_imediato'] and resultado['chefe_imediato']['cpf']:
                    cpf_supervisor = resultado['chefe_imediato']['cpf']
                    status, dados_supervisor = consultar_api_athenas(cpf_supervisor, buscar_supervisor=False)

                    if status and dados_supervisor:
                        try:
                            matricula_supervisor = dados_supervisor.get('matricula')

                            q = Q(cpf=cpf_supervisor, supervisor=None, eh_defensor=True)
                            if matricula_supervisor:
                                q |= Q(matricula=matricula_supervisor, supervisor=None, eh_defensor=True)
                            servidor = Servidor.objects.get(q)
                        except Exception:
                            pass
                        else:
                            if servidor.defensor:
                                dados['defensor_supervisor'] = servidor.defensor
        return athenas_online, dados


class LDAPAPI(object):
    def __init__(self):
        for key, value in six.iteritems(settings.PYTHON_LDAP_CONFIG):
            attr_name = '_{key}'.format(key=key)
            setattr(self, attr_name, value)

        # self._LDAP_AUTH_GLOBAL_OPTIONS = settings.LDAP_AUTH_GLOBAL_OPTIONS
        # self._LDAP_AUTH_SERVER_URI = settings.LDAP_AUTH_SERVER_URI
        # self._LDAP_AUTH_BIND_DN = settings.LDAP_AUTH_BIND_DN
        # self._LDAP_AUTH_BIND_PASSWORD = settings.LDAP_AUTH_BIND_PASSWORD
        # self._LDAP_AUTH_BIND_SUFFIX = settings.LDAP_AUTH_BIND_SUFFIX

        super(LDAPAPI, self).__init__()
        for opt, value in self._LDAP_AUTH_GLOBAL_OPTIONS.items():
            ldap.set_option(opt, value)

        self._query_by_name_template = '(&(objectCategory=person)(objectClass=user)(name=*%s*)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))'  # noqa: E501
        self._query_by_name_username = '(&(objectCategory=person)(objectClass=user)(sAMAccountName=*%s*)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))'  # noqa: E501

        try:
            ldap_connection = ldap.initialize(self._LDAP_AUTH_SERVER_URI)
            ldap_connection.simple_bind_s(self._LDAP_AUTH_BIND_DN, self._LDAP_AUTH_BIND_PASSWORD)
            self._ldap_connection = ldap_connection
        except ldap.LDAPError as e:
            raise Exception(e)

    def _query(self, query, atributos_para_retorno=None):
        ldap_online = True
        if not atributos_para_retorno:
            atributos_para_retorno = ['distinguishedName', 'name', 'givenName', 'sAMAccountName', 'mail']
        else:
            atributos_para_retorno = [six.binary_type(attr) for attr in atributos_para_retorno]
        lista = []

        try:
            response = self._ldap_connection.search_s(self._LDAP_AUTH_BIND_SUFFIX,
                                                      ldap.SCOPE_SUBTREE,
                                                      query,
                                                      atributos_para_retorno)
        except ldap.LDAPError as e:
            ldap_online = False
            raise Exception(e)
        else:
            mapa = {
                'name': 'nome',
                'givenName': 'first_name',
                'mail': 'email',
                'sAMAccountName': 'username'
            }
            for x in response:
                if x and x[0]:
                    dados_saida = {
                        'cpf': None,
                        'first_name': None,
                        'nome': None,
                        'matricula': None,
                        'email': None,
                        'username': None,
                        'sexo': None,
                        'foto': None,
                        'defensor_supervisor': None,
                        'esta_ativo': True
                    }
                    for key, value in six.iteritems(x[1]):

                        if len(value) >= 1 and key in mapa.keys():
                            valor_atual = value[0]
                            if isinstance(value[0], six.binary_type):
                                valor_atual = valor_atual.decode('utf-8')
                            dados_saida[mapa[key]] = valor_atual
                    lista.append(dados_saida)

        return ldap_online, lista

    def query_by_name(self, name):
        q = filter_format(self._query_by_name_template, [name])

        return self._query(query=q)

    def query_by_username(self, username):
        q = filter_format(self._query_by_name_username, [username])
        return self._query(query=q)


def buscar_servidor_api_athenas_e_ldap(cpf, nome_completo):
    errors = []
    botoes = []
    servidor = None
    dados_servidor_no_athenas = None
    dados_servidor_ldap = None
    foi_consulta_matricula = False  # noqa
    ativo_no_athenas = False
    athenas_online = True
    username_athenas_gerado = False  # noqa
    ldap_online = True
    dados_obtidos = {
        'origem': None,
        'dados_servidor': {},
        'errors': [],
        'botoes': [],
        'editaveis': {}

    }
    if cpf:
        cpf = CARACTERES_NUMERICOS.sub('', cpf)
    try:
        validate_CPF(cpf)
    except ValidationError:
        errors.append(
            'SOLAR: CPF Inválido. Digite o CPF com 11 digitos, sem pontuacao e traço')
    if cpf:
        if config.USAR_API_ATHENAS:
            try:
                # tenta consultar pelo cpf
                athenas_online, dados_servidor_no_athenas = consultar_api_athenas(cpf=cpf)
                if not dados_servidor_no_athenas:
                    # tenta consultar pela matricula
                    athenas_online, dados_servidor_no_athenas = consultar_api_athenas(matricula=cpf)
                    if dados_servidor_no_athenas:
                        foi_consulta_matricula = True  # noqa

                if dados_servidor_no_athenas:
                    ativo_no_athenas = dados_servidor_no_athenas['esta_ativo']

                if not athenas_online:
                    errors.append(
                        'ATHENAS: Impossivel verificar o Nome/CPF/Matricula. Athenas indisponivel. Tente novamente em alguns instantes. Caso ainda não consiga cadastrar, por favor, abra um chamado no Helpdesk')  # noqa: E501
            except Exception:
                errors.append(
                    'ATHENAS: Impossivel verificar o Nome/CPF/Matricula. Athenas indisponivel. Tente novamente em alguns instantes. Caso ainda não consiga cadastrar, por favor, abra um chamado no Helpdesk')  # noqa: E501

        try:
            servidor = Servidor.objects.select_related('usuario').get(cpf=cpf)
        except Servidor.DoesNotExist:
            pass
        except Servidor.MultipleObjectsReturned:
            errors.append(
                'SOLAR: Impossivel continuar. Existem multiplos cadastros com esse CPF. Por favor, abra um chamado solicitando correção dos dados e informe o nome completo, CPF, matricula')  # noqa: E501

        if not servidor:
            try:
                servidor = Servidor.objects.select_related('usuario').get(matricula=cpf)
            except Servidor.DoesNotExist:
                pass
            except Servidor.MultipleObjectsReturned:
                errors.append(
                    'SOLAR: Impossivel continuar. Existem multiplos cadastros com essa Matricula. Por favor, abra um chamado no Helpdesk solicitando correção dos dados e informe o nome completo, CPF, matricula')  # noqa: E501

        if servidor and dados_servidor_no_athenas and not ativo_no_athenas:
            msg = 'SOLAR: Impossivel continuar. O servidor possui cadastro no Solar, contudo não está com cadastro ativo no Athenas. Entre em contato com o RH'  # noqa: E501
            errors.append(msg)

        if not servidor and dados_servidor_no_athenas and not ativo_no_athenas:
            errors.append('O servidor deve estar com cadastro ativo no Athenas. Entre em contato com o RH.')

        if servidor:
            msg = 'SOLAR: "{}" já possui cadastro no sistema'.format(servidor.usuario.get_full_name())
            if not servidor.ativo:
                msg = '{}, mas está desativado'.format(msg)
            url = reverse('editar_servidor', kwargs={'servidor_id': servidor.usuario_id})

            a = {
                'url': url,
                'msg_botao': 'clique aqui para ver o cadastro',
                'msg': msg
            }
            botoes.append(a)

    if config.USAR_API_LDAP:
        if nome_completo and not servidor:
            ldapapi = LDAPAPI()
            ldap_online, users = ldapapi.query_by_name(nome_completo)
            if not ldap_online:
                errors.append(
                    'LDAP: Impossivel verificar o Nome/CPF/Matricula. LDAP indisponivel. Tente novamente em alguns instantes. Caso ainda não consiga cadastrar, por favor, abra um chamado no Helpdesk'  # noqa: E501
                )
            if ldap_online and users:
                if len(users) > 1:
                    msg = 'LDAP: Existem multiplos cadastros com esse Nome.'
                    errors.append(msg)
                else:
                    # pega sempre o primeiro item da lista
                    dados_servidor_ldap = users[0]

            else:
                errors.append(
                    'LDAP: Servidor não foi localizada. Por favor, solicite a criação do usuario da rede com o Departamento de Redes'  # noqa: E501
                )

    if dados_servidor_no_athenas:
        dados_obtidos['origem'] = 'athenas'
        dados_obtidos['dados_servidor'] = dados_servidor_no_athenas
        if not dados_obtidos['dados_servidor']['username'] and dados_obtidos['dados_servidor']['nome']:
            username_athenas_gerado = True  # noqa
            dados_obtidos['dados_servidor']['username'] = criar_username_de_nome(
                dados_obtidos['dados_servidor']['nome'])
        if dados_obtidos['dados_servidor']['cpf']:
            dados_obtidos['dados_servidor']['cpf'] = CARACTERES_NUMERICOS.sub('',
                                                                              dados_obtidos['dados_servidor']['cpf'])
    elif dados_servidor_ldap:
        dados_obtidos['origem'] = 'ldap'
        dados_obtidos['dados_servidor'] = dados_servidor_ldap
    if dados_servidor_no_athenas and dados_servidor_ldap:
        if not dados_obtidos['dados_servidor']['username']:
            dados_obtidos['origem'] = 'athenas+ldap'
            dados_obtidos['dados_servidor']['username'] = dados_servidor_ldap['username']
        if not dados_obtidos['dados_servidor']['email']:
            dados_obtidos['origem'] = 'athenas+ldap'
            dados_obtidos['dados_servidor']['email'] = dados_servidor_ldap['email']

    if config.USAR_API_LDAP and config.USAR_API_ATHENAS:
        if athenas_online and ldap_online and not dados_servidor_no_athenas and not dados_servidor_ldap and not servidor:  # noqa: E501
            errors.append(
                'SOLAR: Servidor não pode ser cadastrado, pois já deve possuir usuário na rede. Por favor, solicite a criação do usuario da rede com o Departamento de Redes')  # noqa: E501

    if not config.USAR_API_LDAP and not config.USAR_API_ATHENAS and not servidor:
        username_gerado = criar_username_de_nome(nome_completo)
        dados_obtidos['dados_servidor'] = {
            'cpf': cpf,
            'first_name': None,
            'nome': nome_completo,
            'matricula': None,
            'email': None,
            'username': username_gerado,
            'sexo': None,
            'foto': None,
            'defensor_supervisor': None,
            'esta_ativo': True
        }

    editaveis = {}
    for key, value in six.iteritems(dados_obtidos['dados_servidor']):
        if value:
            editaveis[key] = False
        else:
            editaveis[key] = True
    dados_obtidos['errors'] = {'__all__': errors}
    dados_obtidos['editaveis'] = editaveis
    dados_obtidos['botoes'] = botoes
    return dados_obtidos


numeros_re = re.compile('\d+')  # noqa: W605


def envia_sms(mensagem, numero):

    logger.info("DPERR >> Enviando SMS para o numero {} ".format(numero))

    # verifica se a flag envio pelo facilita sms
    if (config.FACILITA_SMS_AUTH):
        facilita_sms_api_url = config.FACILITA_SMS_API_URL
        facilita_sms_auth_user = config.FACILITA_SMS_AUTH_USER
        facilita_sms_auth_token = config.FACILITA_SMS_AUTH_TOKEN

        montar_url = "?user=" + facilita_sms_auth_user + "&password=" + \
            facilita_sms_auth_token + "&destinatario=" + numero + "&msg=" + mensagem
        try:
            r = requests.post(facilita_sms_api_url + montar_url)
            return r
        except ValidationError:
            logger.error("DPE >> Não foi possível se conectar ao servidor de envio de sms")
        return 500
    else:
        movile_auth_token = settings.MOVILE_AUTH_TOKEN
        movile_auth_user = settings.MOVILE_AUTH_USER
        movile_api_url = settings.MOVILE_API_URL

        headers = {'authenticationtoken': movile_auth_token, 'username': movile_auth_user}
        r = requests.post(movile_api_url, headers=headers, json={"destination": numero, "messageText": mensagem})
        return r


def envia_email(mensagem, email_destino, assunto):

    logger.info("DPEAc >> Enviando Email para  {} ".format(email_destino))

    try:
        r = send_mail(
            assunto,
            '',
            settings.EMAIL_HOST_USER,
            [email_destino],
            html_message=mensagem,
            fail_silently=False,
        )
        return r
    except BadHeaderError:
        logger.error("DPE >> Não foi possivel enviar o e-mail")


def dict_list_search(lista, chave, valor):
    return next((item for item in lista if item[chave] == valor), None)


class CartorioService:

    def importar(self):
        for estado in Estado.objects.all():
            self.importar_por_estado(estado.uf)

    def importar_por_estado(self, estado_uf):

        url_api = 'https://api-rc.registrocivil.org.br/api/cartorios/'
        municipios = {}

        # Obtém lista de municípios do estado
        url = '{}uf/{}/cidade'.format(url_api, estado_uf)
        response = requests.get(url)

        if response.status_code == 200:

            estado_data = response.json()

            # Cria dicionário com correspondência de códigos de município
            for item in estado_data['cidades']:

                # Cidades do DF são o mesmo município IBGE
                if estado_uf == 'DF':
                    item['ibge_id'] = '5300108'

                # Municípios com nome antigo na API do Registro Civil
                if item['cidade_id'] == 2580:  # Tacima - PB
                    item['ibge_id'] = '2516409'
                elif item['cidade_id'] == 2405:  # Joca Claudino - PB
                    item['ibge_id'] = '2513653'

                municipios[item['id']] = item['ibge_id']

            # Obtém lista de cartórios do estado
            url = '{}geolocalizacao?estado={}'.format(url_api, estado_uf)
            response = requests.get(url)

            if response.status_code == 200:
                cartorios_data = response.json()

                for cartorio_data in cartorios_data:

                    municipio_id = None
                    if cartorio_data['cidade_id'] in municipios:
                        municipio_id = municipios[cartorio_data['cidade_id']]
                    else:
                        municipio = Municipio.objects.get(
                            nome=cartorio_data['cidade'],
                            estado__uf=cartorio_data['estado']
                        )
                        municipio_id = municipio.id

                    # Cria/Atualiza registro do cartório
                    Cartorio.objects.update_or_create(
                        cns=cartorio_data['cnj'],
                        defaults={
                            'nome': cartorio_data['nome'],
                            'municipio_id': municipio_id,
                            'desativado_em': None if cartorio_data['ativo'] == 'S' else timezone.now()
                        }
                    )

                return len(cartorios_data)


class PapelService(object):

    def criar_grupos(self, remover_permissoes_anteriores=True):

        with open('initial_data_files/permissions.json') as file:

            groups = json.load(file)

            for group in groups:

                dj_group, _ = Group.objects.update_or_create(
                    name__iexact=group['name'],
                    defaults={
                        'name': group['name']
                    }
                )

                if remover_permissoes_anteriores:
                    dj_group.permissions.clear()

                for perm in group['permissions']:

                    dj_perm = Permission.objects.get(
                        codename=perm['codename'],
                        content_type__app_label=perm['app_label'],
                        content_type__model=perm['model'],
                    )

                    dj_group.permissions.add(dj_perm)

                    print(u'Permissão "{}_{}.{}"" adicionada ao grupo "{}"'.format(
                        perm['app_label'],
                        perm['model'],
                        perm['codename'],
                        group['name'],
                    ))

        print(u'Concluído!')

    def criar_papeis(self):

        with open('initial_data_files/papeis.json') as file:

            papeis = json.load(file)

            for papel in papeis:

                dj_papel, _ = Papel.objects.update_or_create(
                    nome__iexact=papel['name'],
                    defaults={
                        'nome': papel['name'],
                        'marcar_usuario_como_defensor': papel['marcar_usuario_como_defensor']
                    }
                )

                dj_papel.grupos.clear()

                for group in papel['groups']:

                    dj_group = Group.objects.get(
                        name=group,
                    )

                    dj_papel.grupos.add(dj_group)

                    print(u'Grupo "{}" adicionado ao Papel "{}"'.format(
                        group,
                        papel['name'],
                    ))

        print(u'Concluído!')


class FileConversorService(object):
    valid_extensions = []
    valid_mimetypes = []
    destination_format = None

    doc_object = None
    field_file_name = None

    file_name = None
    file_path = None

    doc_mimetype = None
    doc_encoding = None

    def __init__(self, doc_object=None, field_file_name='arquivo'):

        if doc_object:

            self.doc_object = doc_object
            self.field_file_name = field_file_name

            # Nome do arquivo origem
            field_file = getattr(doc_object, field_file_name)
            self.file_name = field_file.name
            try:
                self.file_path = field_file.path
            # Fallback para o Minio Storage, visto que ele não implementa o metodo path
            except NotImplementedError:
                self.file_path = field_file.name

            # Obtém mimetype do arquivo
            self.doc_mimetype, self.doc_encoding = mimetypes.guess_type(self.file_path, strict=True)

    def is_valid(self) -> bool:
        return self.is_extension_valid() or self.is_format_valid()

    def is_extension_valid(self) -> bool:
        # Verifica se formato do arquivo é um formato válidos
        if pathlib.Path(self.file_path).suffix in self.valid_extensions:
            return True
        else:
            return False

    def is_format_valid(self, mimetype=None) -> bool:

        if mimetype is None:
            mimetype = self.doc_mimetype

        # Verifica se formato do arquivo é um formato válido
        if mimetype in self.valid_mimetypes:
            return True
        else:
            return False

    def export_and_replace(self):

        if self.is_valid():

            # Implementação sem o MINIO
            if not settings.MINIO_STORAGE_MEDIA_BUCKET_NAME:

                self.export('{}.{}'.format(
                    self.file_path, self.destination_format
                ), self.file_path)

                self.doc_mimetype, self.doc_encoding = mimetypes.guess_type(
                    self.file_path, strict=True
                )

                # Atualiza referência no registro do banco
                setattr(self.doc_object, self.field_file_name, '{}.{}'.format(
                    self.file_name,
                    self.destination_format
                ))
            # Implementação com o MINIO
            else:
                import urllib.request
                # faz download temporário
                arquivo_original_temporario = pathlib.Path(
                    '/tmp/{}{}'.format(
                        uuid.uuid4(), pathlib.Path(
                            self.doc_object.arquivo.name
                        ).suffix
                    )
                )
                arquivo_convertido_temporario = pathlib.Path(
                    '/tmp/{}.{}'.format(uuid.uuid4(), self.destination_format)
                )

                urllib.request.urlretrieve(
                    self.doc_object.arquivo.url, arquivo_original_temporario
                )

                self.export(
                    str(arquivo_convertido_temporario), arquivo_original_temporario
                )

                self.doc_object.arquivo.save(
                    name=arquivo_convertido_temporario.name,
                    content=File(open(arquivo_convertido_temporario, 'rb'))
                )

                self.doc_mimetype, self.doc_encoding = mimetypes.guess_type(
                    str(arquivo_convertido_temporario), strict=True
                )

                arquivo_original_temporario.unlink()
                arquivo_convertido_temporario.unlink()

            self.doc_object.save()

            return True, self.doc_mimetype

        return False, self.doc_mimetype


class AudioToMP3Service(FileConversorService):
    valid_extensions = ['.ogg', '.wav']
    destination_format = 'mp3'

    def export(self, destination_file, source_file):
        sound = AudioSegment.from_file(source_file)
        sound.export(destination_file, format='mp3')


class VideoConvertService(FileConversorService):
    valid_extensions = ['.mp4', '.mov', '.avi']
    destination_format = None
    params = None

    # Sobrecarga de metodo
    def export_and_replace(self, return_object=False):

        if self.is_valid():
            arquivo_temporario = pathlib.Path(
                '/tmp/{}.{}'.format(uuid.uuid4(), self.destination_format)
            )

            path = None

            if not settings.MINIO_STORAGE_MEDIA_BUCKET_NAME:
                path = self.doc_object.arquivo.path
            else:
                path = self.doc_object.arquivo.url

            # Converte arquivo em MP4 codificação V2
            ffmpeg.input(
                path
            ).output(
                str(arquivo_temporario), **self.params
            ).run()

            # Obtem arquivo convertido em memória
            video_convertido = File(open(arquivo_temporario, 'rb'))

            # Salva novo vídeo convertido no objeto
            self.doc_object.arquivo.save(
                name=arquivo_temporario.name,
                content=video_convertido
            )

            # Atualiza novo mimetype do arquivo
            self.doc_mimetype, self.doc_encoding = mimetypes.guess_type(
                str(arquivo_temporario), strict=True
            )

            # Deleta arquivo temporário do disco
            arquivo_temporario.unlink()

            if return_object:
                return_object = self.doc_object

            return True, self.doc_mimetype, return_object

        return False, self.doc_mimetype, return_object


class ConvertToMP4Service(VideoConvertService):
    destination_format = 'mp4'
    params = {
        'brand': 'mp42'
    }


class ConvertToWEBMService(VideoConvertService):
    destination_format = 'webm'
    params = {
        'f': 'webm',
        'c:v': 'libvpx',
        'b:v': '512k',
        'crf': '40',
        'acodec': 'libvorbis',
        'ac': '2',
        'strict': 'experimental',
        'vf': 'scale=\'-1:min(ih,320)\'',
    }


class ImageToPDFService(FileConversorService):
    valid_extensions = ['.jfif']
    valid_mimetypes = ['image/jpeg', 'image/gif', 'image/png']
    destination_format = 'pdf'

    def to_http_response(self, filename, images):

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="{}.pdf"'.format(filename)

        self.export(response, images)

        return response

    def download_images_and_export(self, filename, filedir, urls):

        # se diretório não existe, cria
        if not os.path.exists(filedir):
            os.makedirs(filedir)

        images = []

        # Necessário quando este método for usado para baixar arquivo que precise de certificado
        verify_certfile = True
        if settings.VERIFY_CERTFILE != '':
            verify_certfile = False if settings.VERIFY_CERTFILE == 'False' else settings.VERIFY_CERTFILE

        for url in urls:

            # baixa conteúdo do arquivo
            try:
                response = requests.get(url, verify=verify_certfile)
            except Exception as err:
                raise Exception(err)

            content_type = response.headers['content-type']
            # valida se conteúdo do arquivo baixado é uma imagem
            if not self.is_format_valid(content_type):
                # remove imagens baixadas para gerar PDF
                self.remove_downloaded_images(images)
                # gera mensagem de erro
                raise Exception('O endereço "{}" não contém um conteúdo de imagem válido: "{}"'.format(
                    url, content_type
                ))

            # gera nome do arquivo
            ext = content_type.split('/')[-1]
            imagefile = '{}.{}'.format(uuid.uuid4(), ext)
            # gera caminho completo do arquivo
            filepath = os.path.join(filedir, imagefile)

            # salva arquivo no disco
            with open(filepath, 'wb') as image:
                image.write(response.content)

            # gera lista de imagens pra conversão
            images.append(filepath)

        # gera caminho completo do arquivo PDF
        filepath = os.path.join(filedir, filename)

        # gera arquivo pdf
        self.export(filepath, images)

        # remove imagens baixadas para gerar PDF
        self.remove_downloaded_images(images)

    def remove_downloaded_images(self, paths):
        # remove imagens baixadas para gerar PDF
        for path in paths:
            os.remove(path)

    def export(self, response, paths, rotate=False):

        # https://gist.github.com/bradleyayers/1480017
        # https://gist.github.com/dangtrinhnt/a577ece4cbe5364aad28
        # https://stackoverflow.com/questions/26128462/how-do-i-use-reportlabs-drawimage-with-an-image-url

        canvas = Canvas(response)
        page_width, page_height = canvas._pagesize
        margin_size = 10

        if not isinstance(paths, list):
            paths = [paths]

        for path in paths:

            with Image.open(path) as image:

                image_width, image_height = image.size

                # Se a imagem estiver em paisagem, vira e salva como retrato
                if rotate and image_width > image_height:
                    image_width, image_height = image_height, image_width
                    image = image.rotate(90, expand=True)
                    image.save(path)

                # Reduz imagens grandes para o tamanho da página A4
                if image_width > page_width:
                    draw_width, draw_height = page_width, page_height
                else:
                    draw_width, draw_height = image_width, image_height

                canvas.drawImage(
                    path,
                    margin_size,  # x
                    page_height - draw_height - margin_size,  # y
                    width=draw_width - margin_size * 2,
                    height=draw_height - margin_size * 2,
                    preserveAspectRatio=True
                )

                canvas.showPage()

        canvas.save()

        return response


class GedToPDFService(PrintPDFConfiguracaoMixin, SimpleTemplateResponse):
    def __init__(self, documento_ged):
        self.object = documento_ged
        super(GedToPDFService, self).__init__(
            template=None,
            context=None,
            content_type=None,
            status=None,
            charset=None,
            using=None
        )

    def get_cmd_options(self):

        cmd_options = self.cmd_options

        if self.object.page_margin_top:
            cmd_options['margin-top'] = '{}mm'.format(self.object.page_margin_top)
        if self.object.page_margin_bottom:
            cmd_options['margin-bottom'] = '{}mm'.format(self.object.page_margin_bottom)
        if self.object.page_margin_left:
            cmd_options['margin-left'] = '{}mm'.format(self.object.page_margin_left)
        if self.object.page_margin_right:
            cmd_options['margin-right'] = '{}mm'.format(self.object.page_margin_right)

        return cmd_options

    def get_context(self):
        return {
            'is_pdf': True,
            'object': self.object
        }

    def export(self):

        return render_pdf_from_template(
            input_template=self.resolve_template(self.pdf_template_name),
            header_template=self.resolve_template(self.pdf_header_template),
            footer_template=self.resolve_template(self.pdf_footer_template),
            context=self.get_context(),
            request=None,
            cmd_options=self.get_cmd_options()
        )

    def export_to_file(self, filename):
        fp = open(filename, 'wb')
        fp.write(self.export())
        fp.close()


def get_extensao_arquivo(nome_arquivo: str) -> str:
    partes_nome_arquivo = nome_arquivo.split(".")
    return partes_nome_arquivo[-1] if len(partes_nome_arquivo) > 1 else ""
