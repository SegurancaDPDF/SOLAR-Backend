# -*- coding: utf-8 -*-

# Biblioteca Padrao
import coreapi
import os

# Bibliotecas de terceiros
from constance import config
from coreapi.codecs import JSONCodec
from coreapi.transports.http import HTTPTransport
from django.conf import settings
from openapi_codec import OpenAPICodec
from packaging import version
from clients.base.services import APIBase
from requests.exceptions import ConnectionError, ConnectTimeout, HTTPError

# Solar
from contrib import constantes
from contrib.services import GedToPDFService
from contrib.utils import ip_visitante
from processo.processo.models import Aviso, Processo

from . import models
from .exceptions import ManifestacaoServiceUnavailable, ManifestacaoTotalDocumentosInvalid, ManifestacaoRequestFailed


class APIProcapi(APIBase):
    api_url = settings.PROCAPI_URL
    api_token = settings.PROCAPI_TOKEN
    request = None

    def esta_ativado(self):
        return config.ATIVAR_PROCAPI

    def get_mensagem_conexao_indisponivel(self):
        return 'Conexão com {} temporariamente indisponível!'.format(config.NOME_PROCESSO_TJ)

    def get_page_size(self):
        return APIConfig().get('REST_FRAMEWORK_PAGE_SIZE')


class APIConfig(APIProcapi):
    listar_action = 'config'

    def get(self, key=None):
        sucesso, resposta = self.listar(pagina=0, params={})
        if sucesso:
            return resposta.get(key) if key else resposta
        else:
            return {}

    def versao_compativel(self):

        versao = self.get('VERSAO')

        if versao and version.parse(versao) >= version.parse(settings.PROCAPI_VERSAO_MIN):
            return True
        else:
            return False


class APIAssunto(APIProcapi):
    listar_action = 'assuntos'


class APIClasse(APIProcapi):
    listar_action = 'classes'


class APICompetencia(APIProcapi):
    listar_action = 'competencias'


class APIListaProcessos(APIProcapi):
    listar_action = 'processos'

    def listar(self, pagina=1, data_inicial=None, data_final=None):

        params = {}

        if data_inicial:
            params['dtinicial'] = data_inicial.strftime("%Y-%m-%d %H:%M:%S")

        if data_final:
            params['dtfinal'] = data_final.strftime("%Y-%m-%d %H:%M:%S")

        return super(APIListaProcessos, self).listar(pagina, params)


class APILocalidade(APIProcapi):
    listar_action = 'localidades'


class APIOrgaoJulgador(APIProcapi):
    listar_action = 'orgaos_julgadores'

    def obter_codigos_vara_por_sistema_webservice(self, sistema: str):

        varas_webservice = self.listar_todos(params={'sistema_webservice': sistema})

        varas_codigos = []

        for vara in varas_webservice:
            if vara.get('codigo') not in varas_codigos:
                varas_codigos.append(vara.get('codigo'))

        return varas_codigos


class APIProcesso(APIProcapi):
    listar_action = 'processos'
    create_encoding = 'application/json'
    read_field = 'numero'

    def __init__(self, numero, request=None):
        self.request = request
        self.numero = numero
        super(APIProcesso, self).__init__()

    def get_numero(self):
        return self.numero[:20]

    def get_grau(self):
        grau = self.numero[20:]

        if grau.isdigit():
            return int(grau)
        else:
            return Processo.GRAU_0

    def consultar(self, usuario_requisicao=None):
        if config.PROCAPI_ATIVAR_INFORMAR_PERFIL_PROJUDI:
            processo = models.Processo.objects.filter(numero_puro=self.get_numero()).first()
            if processo is not None and processo.credencial_mni_cadastro is not None:
                usuario_requisicao = processo.credencial_mni_cadastro

        sucesso, resposta = self.action(
            ['processos', 'read'],
            params={'numero': self.numero, 'usuario_requisicao': usuario_requisicao}, validate=False)

        # Registra quem acessou o processo
        models.HistoricoConsultaProcesso.objects.create(
            processo=self.get_numero(),
            grau=self.get_grau(),
            sucesso=sucesso,
            ip=ip_visitante(self.request)
        )

        return sucesso, resposta

    def consultar_partes(self, pagina=1):
        return self.action(
            ['processos', 'partes_list'],
            params={'parent_lookup_processo': self.numero, 'page': pagina})

    def consultar_eventos(self, pagina=1):
        return self.action(
            ['processos', 'eventos_list'],
            params={'parent_lookup_processo': self.numero, 'page': pagina})

    def consultar_evento(self, numero_evento):
        return self.action(
            ['processos', 'eventos_read'],
            params={'parent_lookup_processo': self.numero, 'numero': numero_evento})

    def consultar_documento(self, numero_documento, atualizar_documento=False):
        usuario_requisicao = None
        if config.PROCAPI_ATIVAR_INFORMAR_PERFIL_PROJUDI:
            processo = models.Processo.objects.filter(numero_puro=self.get_numero()).first()
            if processo is not None and processo.credencial_mni_cadastro is not None:
                usuario_requisicao = processo.credencial_mni_cadastro
            else:
                usuario_requisicao = self.request.user.servidor.defensor.usuario_eproc

        params = {
                'parent_lookup_processo': self.numero,
                'numero': numero_documento,
                'usuario_requisicao': usuario_requisicao
            }

        if atualizar_documento:
            params['atualizar_documento'] = atualizar_documento

        sucesso, resposta = self.action(
            ['processos', 'documentos_read'],
            params=params,
            validate=False
        )

        # Registra quem acessou o documento
        models.HistoricoConsultaDocumento.objects.create(
            processo=self.get_numero(),
            grau=self.get_grau(),
            documento=numero_documento,
            sucesso=sucesso,
            ip=ip_visitante(self.request)
        )

        return sucesso, resposta

    def criar(self, processo, manifestacao):

        outros_parametros = {}
        for outro_parametro in processo.processooutroparametro_set.all():
            outros_parametros[outro_parametro.outro_parametro.codigo_mni] = outro_parametro.valor

        if processo.calculo_judicial:
            outros_parametros['codCalculoJudicial'] = processo.calculo_judicial

        # Transforma dados do processo em formato válido para o ProcAPI
        params = {
            'numero_temporario': processo.numero,
            'nivel_sigilo': processo.nivel_sigilo,
            'competencia': {'codigo': processo.competencia_mni} if processo.competencia_mni else None,
            'classe': {'codigo': processo.acao.codigo_cnj},
            'localidade': {'codigo': processo.comarca.codigo_eproc},
            'orgao_julgador': {'codigo': processo.vara.codigo_eproc},
            'vinculados': [{
                'numero': processo.originario.numero_puro,
                'vinculo': 'OG'
            }] if processo.originario else [],
            'intervencao_mp': processo.intervencao_mp,
            'valor_causa': processo.valor_causa,
            'assuntos': [{
                # TODO: Diferenciar 'codigo_eproc' para cada sistema webservice disponível
                # Usar o 'codigo_eproc' para permitir usar assuntos locais
                'codigo': item.assunto.codigo_eproc if item.assunto.codigo_eproc else item.assunto.codigo_cnj,
                'codigo_pai_nacional': item.assunto.codigo_cnj if item.assunto.codigo_eproc else None,
                'nacional': False if item.assunto.codigo_eproc else True,
                'nome': item.assunto.nome,
                'principal': item.principal
            } for item in processo.processoassunto_set.all()],
            'prioridades': [
                prioridade.codigo_mni for prioridade in processo.prioridades.all()
            ],
            'parametros': outros_parametros,
            'sistema_webservice': manifestacao.sistema_webservice,
            'sistemas_webservice': [manifestacao.sistema_webservice],
            'manifestacao': manifestacao.codigo_procapi
        }

        params = self.clear_params(params)

        return super(APIProcesso, self).criar(**params)

    def criar_processo_sigiloso(self, processo, sistema_webservice):
        params = {
            'classe': {'codigo': processo.acao.codigo_cnj},
            'localidade': {'codigo': processo.comarca.codigo_eproc},
            'orgao_julgador': {'codigo': processo.vara.codigo_eproc},
            'numero_temporario': processo.numero_procapi,
            'valor_causa': processo.valor_causa,
            'grau': 1,
            'sistema_webservice': sistema_webservice,
            'sistemas_webservice': [sistema_webservice],
            'competencia': {'codigo': 1},
            'nivel_sigilo': 1,
            'intervencao_mp': False,
            'assuntos': [],
            'prioridades': [],
            'vinculados': [],
            'atualizado': False,
            'na_fila_para_execucao': False,
            'sigiloso': False,
            'parametros': {

            },
            'arquivado': False,
            'total_erros': 0
        }
        params = self.clear_params(params)

        return super(APIProcesso, self).criar(**params)


class APIProcessoParte(APIProcapi):
    listar_action = 'processos'
    create_encoding = 'application/json'

    def criar(self, processo, parte, defensor):

        endereco = None
        predio_comarca = processo.comarca.predios.filter(ativo=True).first()

        if predio_comarca:

            endereco = {
                    "cep": predio_comarca.endereco.cep,
                    "logradouro": predio_comarca.endereco.logradouro,
                    "numero": predio_comarca.endereco.numero,
                    "complemento": predio_comarca.endereco.complemento,
                    "bairro": predio_comarca.endereco.bairro.nome,
                    "cidade": predio_comarca.endereco.municipio.nome,
                    "estado": predio_comarca.endereco.municipio.estado.uf,
                    "pais": "BR"
                }

        # Transforma dados do processo em formato válido para o ProcAPI
        params = {
            "parent_lookup_processo": processo.numero,
            "tipo": "AT" if parte.tipo == 0 else "PA",
            "advogados": [{
                "nome": defensor.nome,
                "documento_principal": defensor.cpf,
                "identidade_principal": None,
                "tipo_representante": "D",
                "endereco": endereco
            }] if parte.tipo == 0 else None,
            "pessoa": self.pessoa_to_dict(parte.pessoa)
        }

        params = self.clear_params(params)

        return self.action(['processos', 'partes_create'], params=params, encoding=self.create_encoding)

    def criar_pessoa_relacionada(self, processo, parte, parte_codigo_procapi):
        # Transforma dados da parte relacionada em formato válido para o ProcAPI
        params = {
            "parent_lookup_processo": processo.numero,
            "parte": parte_codigo_procapi,
            "relacionamento": parte.representante_modalidade,
            "pessoa": self.pessoa_to_dict(parte.representante.pessoa)
        }

        params = self.clear_params(params)

        return self.action(
            ['processos', 'partes-pessoas-relacionadas_create'],
            params=params,
            encoding=self.create_encoding
        )

    def pessoa_to_dict(self, pessoa):
        params = {
            "tipo": "juridica" if pessoa.tipo == 1 else 'fisica',
            "documento_principal": pessoa.cpf if pessoa.cpf else "",
            "nome": pessoa.nome_norm,
            'outro_nome': pessoa.nome_social,
            "nome_genitor": pessoa.pai.nome_norm if pessoa.pai else None,
            "nome_genitora": pessoa.mae.nome_norm if pessoa.mae else None,
            "data_nascimento": pessoa.data_nascimento.strftime(self.FORMATO_DATAHORA) if pessoa.data_nascimento else None,  # noqa: E501
            "data_obito": None,
            "sexo": "F" if pessoa.sexo == 1 else "M",
            "cidade_natural": pessoa.naturalidade,
            # "estado_natural": pessoa.naturalidade_estado,
            "nacionalidade": pessoa.nacionalidade if pessoa.nacionalidade else "BR",
            "enderecos": [{
                "cep": endereco.cep,
                "logradouro": endereco.logradouro,
                "numero": endereco.numero,
                "complemento": endereco.complemento,
                "bairro": endereco.bairro.nome if endereco.bairro else None,
                "cidade": endereco.municipio.nome if endereco.municipio else None,
                "estado": endereco.municipio.estado.uf if endereco.municipio else None,
                "pais": "BR"
            } for endereco in pessoa.enderecos.ativos()]
        }

        # Documentos da pessoa
        documentos = []

        # Se PJ, adiciona CNPJ
        if pessoa.tipo == constantes.TIPO_PESSOA_JURIDICA:
            if pessoa.cnpj:
                documentos.append({
                    'numero': pessoa.cnpj,
                    'emissor': 'RFB',  # Receita Federal do Brasil
                    'tipo': 'CMF'
                })
        # Senão (PF), adiciona CPF, RG e Certidão
        else:
            if pessoa.cpf:
                documentos.append({
                    'numero': pessoa.cpf,
                    'emissor': 'RFB',  # Receita Federal do Brasil
                    'tipo': 'CMF'
                })

            # TODO: Identificar motivo de salvar RG como None
            if pessoa.rg_numero and pessoa.rg_numero.lower() != 'none':
                documentos.append({
                    'numero': pessoa.rg_numero,
                    'emissor': 'SSP',  # Secretaria de Segurança
                    'tipo': 'CI'
                })

            if pessoa.certidao_numero and '000000' not in pessoa.certidao_numero:
                documentos.append({
                    'numero': pessoa.certidao_numero,
                    'emissor': 'CRC',  # Cartório de Registro Civil
                    'tipo': pessoa.certidao_tipo
                })

        if len(documentos):
            params['documentos'] = documentos

        return params


class APISistema(APIProcapi):
    listar_action = 'sistemas'
    read_field = 'nome'

    METODO_ASSINATURA_POR_TOKEN = 2
    METODO_ASSINATURA_POR_CERTIFICADO_A1 = 3


class APITipoDocumento(APIProcapi):
    listar_action = 'tipos_documento'


class APITipoEvento(APIProcapi):
    listar_action = 'tipos_evento'


class APIManifestacao(APIProcapi):
    listar_action = 'manifestacoes'
    read_field = 'id'
    sistema_webservice = None
    identificador = None
    manifestante = None
    evento = None
    documentos = []
    avisos = []

    def __init__(self, numero, sistema_webservice):
        self.numero = numero
        self.sistema_webservice = sistema_webservice

        authorization = {'Authorization': 'Token {}'.format(settings.PROCAPI_TOKEN)}
        headers = dict(authorization)
        transport = HTTPTransport(credentials=authorization, headers=headers)

        try:
            self.client = coreapi.Client(decoders=[OpenAPICodec(), JSONCodec()], transports=[transport])
            self.schema = self.client.get(settings.PROCAPI_URL)
        except (ConnectionError, ConnectTimeout, HTTPError) as e:
            mensagem_de_error = """Devido a instabilidade de conexão
                                 o serviço de enviar manifestção está insdisponível no momento."""
            raise ManifestacaoServiceUnavailable(e, message=mensagem_de_error)

        self.manifestante = None
        self.documentos = []

    def add_manifestante(self, cpf, usuario=None, senha=None):
        self.manifestante = {
            'cpf': cpf,
            'usuario': usuario,
            'senha': senha
        }

    def add_evento(self, tipo):
        self.evento = {
            'tipo': tipo
        }

    def add_documento(self, nome, tipo, nivel_sigilo, arquivo, ged=None, url=None, mimetype=None):

        upload = None

        # Se ged, obtém conteúdo gravado em banco no formato pdf
        if ged:

            # Obtém conteúdo do ged em formato pdf
            servico = GedToPDFService(ged)
            content = servico.export()

            upload = coreapi.utils.File(u'{}.pdf'.format(nome), content)

            # Adiciona dados do documento na lista de envio
            dados = {
                'nome': nome,
                'tipo': tipo,
                'nivel_sigilo': nivel_sigilo,
                'upload': upload,
                'url': url
            }

            if mimetype:
                dados['mimetype'] = mimetype

            self.documentos.append(dados)

        # Se url, envia link para download via ProcAPI (não recomendado)
        if url:

            # Adiciona dados do documento na lista de envio
            self.documentos.append({
                'nome': nome,
                'tipo': tipo,
                'nivel_sigilo': nivel_sigilo,
                'upload': None,
                'url': url
            })

        # Se arquivo, obtém conteúdo gravado em disco
        if arquivo:
            # Obtém extensão do arquivo e gera novo nome com extensão
            name, extension = os.path.splitext(arquivo.name)
            name = u'{}{}'.format(nome, extension)
            try:
                # Obtém conteúdo do arquivo
                with open(arquivo.path, 'rb') as file:
                    content = file.read()
            # fallback MINIO storage
            except NotImplementedError:
                content = arquivo.read()

            upload = coreapi.utils.File(name, content)

            # Adiciona dados do documento na lista de envio
            dados = {
                'nome': nome,
                'tipo': tipo,
                'nivel_sigilo': nivel_sigilo,
                'upload': upload,
                'url': None
            }

            if mimetype:
                dados['mimetype'] = mimetype

            self.documentos.append(dados)

    def enviar(self):

        total = len(self.documentos)
        deve_enviar_manifestante = APISistema().get(self.sistema_webservice).get('deve_enviar_manifestante')

        for posicao, documento in enumerate(self.documentos):

            ultimo_documento = (posicao == total - 1)

            # Se é o último documento da manifestação, verifica se os anteriores foram enviados
            # A verificação é feita antes do envio do último documento por causa da flag "finalizar"
            # A flag "finalizar" indica ao procapi que a manifestação já pode ser protocolada
            if self.identificador and ultimo_documento:

                servico = APIManifestacao(numero=self.numero, sistema_webservice=self.sistema_webservice)
                sucesso_manifestacao, resposta_manifestacao = servico.consultar(pk=self.identificador)

                if (not sucesso_manifestacao):
                    raise ManifestacaoRequestFailed(
                        self.messages if self.messages else "Falha ao consultar manifestação."
                    )

                # Realiza validação da quantidade de documentos adicionados na manifestação (no lado do procapi)
                if resposta_manifestacao['total_documentos'] != len(self.documentos) - 1:
                    raise ManifestacaoTotalDocumentosInvalid(
                        'O total de documentos da manifestação não corresponde ao total enviado!'
                    )

            params = {
                'parent_lookup_processo': self.numero,
                'manifestante_cpf': self.manifestante['cpf'],
                'manifestante_usuario': self.manifestante['usuario'] if deve_enviar_manifestante else None,
                'evento_tipo': self.evento['tipo'],
                'documento_nome': documento['nome'],
                'documento_tipo': documento['tipo'],
                'documento_nivel_sigilo': documento['nivel_sigilo'],
                'documento_url': documento['url'],
                'documento_upload': documento['upload'],
                'avisos': self.avisos,
                'identificador': self.identificador,
                'finalizar': ultimo_documento
            }

            # mimetype é opcional, sendo informado apenas quando é certificado A1
            if 'mimetype' in documento:
                params['documento_mimetype'] = documento['mimetype']

            sucesso, resposta = self.action(['processos', 'peticionamento_create'], params=params)

            if sucesso and resposta.get('identificador'):
                self.identificador = resposta.get('identificador')

        return sucesso, resposta


class APIManifestante(APIProcapi):
    listar_action = 'consultantes'

    def validar_credenciais(self, **kwargs):
        return self.action([self.listar_action, 'validar_credenciais_create'], kwargs)

    def consultar_avisos(self, **kwargs):
        return self.action([self.listar_action, 'consultar_avisos_list'], kwargs)


class APIAviso(APIProcapi):
    listar_action = 'avisos'
    read_field = 'numero'
    create_encoding = 'application/json'

    def consultar_totais(self, params={}):

        # Remove parâmetros nulos
        clean_params = {}
        for key in params:
            if params[key] is not None:
                clean_params[key] = params[key]

        return self.action([self.listar_action, 'totais_list'], clean_params)

    def consultar_total(self, params={}):

        total_geral = 0

        sucesso, totais = self.consultar_totais(params)

        if sucesso:
            for total in totais:
                total_geral += total['count']

        return total_geral

    def consultar_total_abertos(self, params={}):
        from processo.processo.models import Aviso

        total_geral = 0

        sucesso, totais = self.consultar_totais(params)

        if sucesso:
            for total in totais:
                if total['_id']['situacao'] in [Aviso.SITUACAO_PENDENTE, Aviso.SITUACAO_ABERTO]:
                    total_geral += total['count']

        return total_geral


class APIComunicacao(APIProcapi):
    create_encoding = 'application/json'
    listar_action = 'comunicacoes'
    read_field = 'numero'


class PrateleiraAvisosService():

    sistema = None
    defensoria = None
    defensor = None
    usuario = None

    def __init__(self, sistema, defensoria, defensor, usuario) -> None:

        self.sistema = sistema
        self.defensoria = defensoria
        self.usuario = usuario

        if config.VINCULAR_NA_DISTRIBUICAO_AVISO_A_DEFENSOR_AUTOMATICAMENTE and not defensor and usuario.servidor.defensor.eh_defensor:  # noqa: E501
            self.defensor = self.usuario.servidor.defensor
        else:
            self.defensor = defensor

    @property
    def distribuido_cpf(self):
        """Obtém valor para filtro 'distribuido_cpf'"""

        if self.defensor and (config.VINCULAR_NA_DISTRIBUICAO_AVISO_A_DEFENSOR_AUTOMATICAMENTE or config.AVISOS_FILTER_DISTRIBUIDO_OPERADOR_LOGICO == 'OR'):  # noqa: E501
            return self.defensor.servidor.cpf

    @property
    def distribuido_defensoria(self):
        """Obtém valor para filtro 'distribuido_defensoria'"""

        if self.defensoria:
            return self.defensoria.id
        elif self.defensor and not config.VINCULAR_NA_DISTRIBUICAO_AVISO_A_DEFENSOR_AUTOMATICAMENTE:
            return ','.join(map(str, list(self.defensor.defensorias.values_list('id', flat=True))))

    def consultar(self) -> dict:
        """Consulta totais de avisos filtrados"""

        totais = {}

        # Só consulta se defensor/defensoria foi informado ou o usuário é superusuário
        if self.defensor or self.defensoria or self.usuario.is_superuser:
            _, totais = APIAviso().consultar_totais(params={
                'sistema_webservice': self.sistema.nome if self.sistema else None,
                'distribuido': True,
                'distribuido_cpf': self.distribuido_cpf,
                'distribuido_defensoria': self.distribuido_defensoria,
                'distribuido_operador_logico': config.AVISOS_FILTER_DISTRIBUIDO_OPERADOR_LOGICO,
                'ativo': True
            })

        return totais

    def gerar(self) -> tuple[int, list]:
        """Gera lista de totais de avisos categorizados por prateleira"""

        total_geral = 0
        prateleiras = []
        totais = self.consultar()

        for tipo_id, tipo_nome in Aviso.LISTA_TIPO:

            total_tipo = 0
            itens = []

            for situacao_id, situacao_nome in Aviso.LISTA_SITUACAO:

                # Procura por total de itens vinculados ao tipo e situação
                total_situacao = 0
                for total in totais:
                    if total['_id']['tipo'] == tipo_id and total['_id']['situacao'] == situacao_id:
                        total_situacao = total['count']
                        break

                itens.append({
                    'id': situacao_id,
                    'nome': situacao_nome,
                    'total': total_situacao
                })

                # Não somar avisos fechados ou expirados
                if situacao_id not in [Aviso.SITUACAO_FECHADO, Aviso.SITUACAO_EXPIRADO]:
                    total_tipo += total_situacao

            prateleiras.append({
                'id': tipo_id,
                'nome': tipo_nome,
                'total': total_tipo,
                'itens': itens
            })

            total_geral += total_tipo

        return total_geral, prateleiras
