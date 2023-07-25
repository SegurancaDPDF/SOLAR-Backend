# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

# Biblioteca Padrao
import logging
from datetime import datetime, timedelta
import re
from assistido.exceptions import DadosPessoaInsuficientesException

# Bibliotecas de terceiros
from constance import config
from django.db import connection
from django.db.models import Q, Case, When, BooleanField
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.cache import cache
import reversion

# Solar
from contrib.models import CPF, CNPJ, Defensoria, DefensoriaVara, Municipio, Bairro, Endereco, Comarca, Util
from assistido.models import PessoaAssistida, Filiacao as PessoaFiliacao
from contrib import constantes

from defensor.models import Atuacao, Defensor
from procapi_client.models import Competencia
from procapi_client.services import APIAviso, APIProcesso

from atendimento.atendimento.models import (
    Defensor as AtendimentoDefensor,
    Pessoa as AtendimentoPessoa,
    Qualificacao,
    Atendimento,
    Acesso,
    Tarefa
)

# Modulos locais
from .models import (
    Acao,
    Assunto,
    DocumentoFase,
    DocumentoTipo,
    Fase,
    FaseTipo,
    Manifestacao,
    Parte,
    Prioridade,
    Processo,
    ProcessoAssunto,
    Distribuicao,
    Redistribuicao
)
from processo.honorarios.services import HonorarioService
from .forms import (
    AtendimentoForm,
    ProcessoForm,
    ProcessoParteForm)

logger = logging.getLogger(__name__)


class AvisoService(object):

    parte_processo = None

    def get_grau(self, aviso):
        """
        Identifica o grau do processo do aviso
        """
        return aviso['sistema_webservice'][aviso['sistema_webservice'].index('G-')-1]

    def get_comarca(self, aviso):
        return Comarca.objects.filter(
            vara__orgaojulgador__sistema_webservice__nome=aviso['sistema_webservice'],
            vara__orgaojulgador__codigo_mni=aviso['processo']['orgaoJulgador']['codigoOrgao']
        ).first()

    def get_defensoria(self, aviso, defensoria=None):
        if defensoria is None and aviso['distribuido_defensoria']:
            defensoria = Defensoria.objects.get(id=aviso['distribuido_defensoria'])
        return defensoria

    def get_paridade(self, aviso):
        """
        Identifica a paridade do processo do aviso
        """

        if aviso['processo']['numero'][6] in '13579':
            return DefensoriaVara.PARIDADE_IMPARES
        else:
            return DefensoriaVara.PARIDADE_PARES

    def get_polo(self, aviso):

        sigla = None
        tipo = Parte.TIPO_AUTOR

        if 'polo_destinatario' in aviso:
            sigla = aviso['polo_destinatario']
        else:
            sigla = self.get_parte_processo_procapi(aviso)['tipo']

        if sigla == 'PA':
            tipo = Parte.TIPO_REU
        elif sigla == 'TC':
            tipo = Parte.TIPO_TERCEIRO
        elif sigla == 'VI':
            tipo = Parte.TIPO_VITIMA
        elif sigla == 'AD':
            tipo = Parte.TIPO_ASSISTENTE

        return tipo

    def get_parte_processo_procapi(self, aviso):

        if not self.parte_processo:

            pessoa_aviso = aviso['destinatario']['pessoa']

            # Realiza a consulta geral antes de consultar_partes
            # por algum motivo foi verificado que pode influênciar no retorno de consultar_partes.
            api_processo = APIProcesso(numero=aviso['processo']['numero'])
            api_processo.consultar()
            _, resposta = api_processo.consultar_partes()

            # Verifica a existência de results visto que a resposta pode não conter results em caso de erro.
            if 'results' in resposta:
                for parte in resposta['results']:
                    pessoa_processo = parte['pessoa']
                    if pessoa_processo['nome'] == pessoa_aviso['nome'] or (pessoa_processo['documento_principal'] == pessoa_aviso['numeroDocumentoPrincipal'] and pessoa_aviso['numeroDocumentoPrincipal']):  # noqa: E501
                        self.parte_processo = parte
                        break

        return self.parte_processo

    def get_pessoa_processo(self, aviso):
        parte_processo = self.get_parte_processo_procapi(aviso)
        return parte_processo['pessoa'] if parte_processo else None

    def get_destinatario(self, aviso):

        pessoa_aviso = aviso['destinatario']['pessoa']
        cpf = Util.cpf_cnpj_valido(pessoa_aviso['numeroDocumentoPrincipal'])

        if cpf:
            return PessoaAssistida.objects.ativos().filter(cpf=cpf)
        else:
            pessoa_processo = self.get_pessoa_processo(aviso)
            if pessoa_processo is not None:
                pessoa_aviso = pessoa_processo

        assistidos = []
        data_nascimento = None

        if pessoa_aviso:

            data_nascimento = Util.string_to_date(pessoa_aviso.get('data_nascimento'), '%Y-%m-%dT%H:%M:%S')
            assistidos = PessoaAssistida.objects.ativos().filter(
                nome_norm=Util.normalize(pessoa_aviso.get('nome')),
                data_nascimento=data_nascimento,
                filiacoes__nome_norm__in=[
                    Util.normalize(pessoa_aviso.get('nome_genitor')),
                    Util.normalize(pessoa_aviso.get('nome_genitora'))
                ]
            )

        return assistidos

    def get_pessoa_assistida(self, aviso):

        assistido = self.get_destinatario(aviso)

        if assistido.exists():

            return assistido.first()

        else:

            pessoa = self.get_pessoa_processo(aviso)
            cpf = Util.cpf_cnpj_valido(pessoa.get('documento_principal', ''))
            data_nascimento = pessoa.get('data_nascimento')
            nome_genitor = pessoa.get('nome_genitor')
            nome_genitora = pessoa.get('nome_genitora')
            nome = pessoa.get('nome')

            # Verificar se existe dados suficientes para castrar a pessoa do aviso ou processo
            # Para não correr o risco de cadastrar a mesma pessoa repetidamente
            if not (cpf
                    or data_nascimento
                    or nome_genitor
                    or nome_genitora):
                raise DadosPessoaInsuficientesException()

            data_nascimento = Util.string_to_date(data_nascimento, '%Y-%m-%dT%H:%M:%S')

            assistido = PessoaAssistida.objects.create(
                cpf=cpf,
                nome=Util.normalize(nome),
                data_nascimento=data_nascimento,
                sexo=PessoaAssistida.SEXO_FEMININO if pessoa['sexo'] == 'F' else PessoaAssistida.SEXO_MASCULINO,
            )

            if nome_genitor:
                PessoaFiliacao.objects.create(
                    pessoa_assistida=assistido,
                    nome=nome_genitor,
                    tipo=PessoaFiliacao.TIPO_PAI)

            if nome_genitora:
                PessoaFiliacao.objects.create(
                    pessoa_assistida=assistido,
                    nome=nome_genitora,
                    tipo=PessoaFiliacao.TIPO_MAE)

            # Dados do endereço
            if pessoa['enderecos']:

                endereco = pessoa['enderecos'][0]

                municipio = Municipio.objects.filter(
                    nome__iexact=endereco['cidade'],
                    estado__uf__iexact=endereco['estado']
                ).first()

                if municipio:

                    bairro = Bairro.objects.filter(
                        nome__iexact=endereco['bairro'],
                        municipio=municipio
                    ).first()

                    endereco = Endereco.objects.create(
                        principal=True,
                        logradouro=endereco['logradouro'],
                        numero=endereco['numero'],
                        complemento=endereco['complemento'],
                        cep=endereco['cep'],
                        bairro=bairro,
                        municipio=municipio,
                    )

                    assistido.enderecos.add(endereco)

            return assistido

    def get_processo(self, aviso):
        """
        Identifica processo a partir do aviso
        """

        return Processo.objects.filter(
            ativo=True,
            numero_puro=aviso['processo']['numero'],
            grau=self.get_grau(aviso)
        ).first()

    def get_parte_processo(self, aviso):
        """
        Identifica parte processual a partir do aviso
        """

        # Caso o atendimento seja inicial basta buscar pela parte no proprio atendimento
        parte_inicial = Parte.objects.filter(
            ativo=True,
            defensoria__isnull=False,
            processo__numero_puro=aviso['processo']['numero'],
            processo__grau=self.get_grau(aviso),
            processo__ativo=True,
            atendimento__partes__tipo=AtendimentoPessoa.TIPO_REQUERENTE,
            atendimento__partes__pessoa__in=self.get_destinatario(aviso),
        ).first()

        parte_retorno = None
        if not parte_inicial:
            # Caso o atendimento seja de retorno devera buscar a parte no atendimento inicial
            parte_retorno = Parte.objects.filter(
                ativo=True,
                defensoria__isnull=False,
                processo__numero_puro=aviso['processo']['numero'],
                processo__grau=self.get_grau(aviso),
                processo__ativo=True,
                atendimento__inicial__partes__tipo=AtendimentoPessoa.TIPO_REQUERENTE,
                atendimento__inicial__partes__pessoa__in=self.get_destinatario(aviso),
            ).first()

        return parte_inicial if parte_inicial else parte_retorno

    def distribuir(self, aviso, defensorias_varas=None, salvar=False):
        """
        Distribui aviso para defensoria/defensor a partir das regras de distribuição
        """

        defensoria = self.identificar_defensoria(aviso, defensorias_varas)
        defensor = None

        # Se existe associação, sugere defensor ou defensoria responsavel
        if defensoria:

            if config.VINCULAR_NA_DISTRIBUICAO_AVISO_A_DEFENSORIA_AUTOMATICAMENTE:
                aviso['distribuido_defensoria'] = defensoria.id

            if config.VINCULAR_NA_DISTRIBUICAO_AVISO_A_DEFENSOR_AUTOMATICAMENTE:

                defensor = self.identificar_defensor(aviso, defensoria)

                if defensor:
                    aviso['distribuido_cpf'] = defensor.servidor.cpf

            if salvar:
                # Verifica se há divergência entre a Defensoria Responsável e a Defensoria sugerida pelas demais regras
                # Se houver, não distribui automaticamente e mostra o aviso para a tela de distribuição manual.
                if config.VINCULAR_NA_DISTRIBUICAO_AVISO_A_PROCESSO_CADASTRADO:
                    parte = AvisoService().get_parte_processo(aviso)
                    defensoria = self.identificar_defensoria(aviso, defensorias_varas, salvar)
                    if parte and parte.defensoria:
                        if defensoria != parte.defensoria:
                            return False, None
                return self.salvar_distribuicao(aviso['numero'], defensoria, defensor)

        return False, None

    def identificar_peticao_inicial(self, aviso):
        """
        Identifica a manifestação que originou o processo (petição inicial)
        """
        return Manifestacao.objects.ativos().filter(
            parte__processo__numero_puro=aviso['processo']['numero'],
            tipo=Manifestacao.TIPO_PETICAO_INICIAL,
            situacao=Manifestacao.SITUACAO_PROTOCOLADO
        ).first()

    def identificar_defensoria(self, aviso, defensorias_varas=None, salvar=False):
        """
        Identifica a defensoria responsável pelo aviso a partir das regras de distribuição
        """

        # REGRA 1: Distribuição por parte processual cadastrada
        # Se deve usar a defensoria responsável pela parte processual, ignora as regras de distribuição
        if config.VINCULAR_NA_DISTRIBUICAO_AVISO_A_PROCESSO_CADASTRADO and not salvar:
            parte = AvisoService().get_parte_processo(aviso)
            if parte and parte.defensoria:
                return parte.defensoria

        # REGRA 2: Distribuição por tipo de documento "emenda à inicial"
        if aviso.get('tipo_documento') and aviso.get('tipo_documento') in config.LISTA_TIPOS_DOCUMENTOS_EMENDA_INICIAL.split():  # noqa: E501
            peticao_inicial = self.identificar_peticao_inicial(aviso)
            if peticao_inicial:
                return peticao_inicial.defensoria

        # Se nenhuma lista de regras informadas, utiliza filtro base
        if defensorias_varas is None:
            # Filtro base das regras de distribuição
            defensorias_varas = DefensoriaVara.objects.ativos().filter(
                vara__orgaojulgador__codigo_mni=aviso['processo']['orgaoJulgador']['codigoOrgao'],
                vara__orgaojulgador__sistema_webservice__nome=aviso['sistema_webservice'],
                paridade__in=[DefensoriaVara.PARIDADE_QUALQUER, self.get_paridade(aviso)]
            )

        defensorias_varas = defensorias_varas.filter(
            (
                Q(usuario_webservice=aviso.get('usuario_webservice')) |
                Q(usuario_webservice='') |
                Q(usuario_webservice=None)
            )
        )

        # REGRA 3: Distribuição por regex
        for defensoria_vara in defensorias_varas.exclude(regex=None):
            if re.findall(defensoria_vara.regex, aviso['processo']['numero']):
                return defensoria_vara.defensoria

        for defensoria_vara in defensorias_varas.filter(regex=None):

            # Obtem um array com as siglas dos polos selecionados para DefensoriaVara. Exemplo: [AT, PA]
            polos = list(defensoria_vara.distribuir_por_polo.all().values_list('sigla_sistema_webservice', flat=True))
            # Obtem um array com os códigos MNI das competências para DefensoriaVara. Exemplo: [10, 12, 15]
            competencias = list(defensoria_vara.distribuir_por_competencia.all().values_list('codigo_mni', flat=True))
            deve_distribuir_por_polo = len(polos)
            deve_distribuir_por_competencia = len(competencias)

            # REGRA 4: Distribuição por Polo x Competência
            if deve_distribuir_por_polo and deve_distribuir_por_competencia:
                if (aviso.get('polo_destinatario') in polos or aviso.get('polo_destinatario') is None) and (aviso.get('processo').get('competencia') in competencias):  # noqa: E501
                    return defensoria_vara.defensoria

            # REGRA 5: Distribuição por Polo
            # Senão verifica se deve distribuir por polo apenas
            elif deve_distribuir_por_polo:
                if aviso.get('polo_destinatario') in polos or aviso.get('polo_destinatario') is None:
                    return defensoria_vara.defensoria

            # REGRA 6: Distribuião por Competência
            # Senão verifica se deve distribuir por competencia apenas
            elif deve_distribuir_por_competencia:
                if aviso.get('processo').get('competencia') in competencias:
                    return defensoria_vara.defensoria

            # REGRA 7: Distribuição por Vara/Paridade
            else:
                return defensoria_vara.defensoria

    def identificar_defensor(self, aviso, defensoria=None):

        if aviso['distribuido_cpf']:
            return Defensor.objects.get(servidor__cpf=aviso['distribuido_cpf'], eh_defensor=True)

        defensoria = self.get_defensoria(aviso, defensoria)

        if defensoria:
            # Procura pela atuação vigente mais recente de um defensor
            atuacao = Atuacao.objects.vigentes(ajustar_horario=False).nao_lotacoes().filter(
                defensoria=defensoria
            ).order_by(
                '-data_inicial',
                'tipo'
            ).first()

            if atuacao:
                return atuacao.defensor

    def salvar_distribuicao(self, aviso_numero, defensoria, defensor, eh_redistribuicao=False):
        """
        Salvar distribuição
        """
        from processo.processo.tasks import procapi_cadastrar_preanalise_honorario_aviso

        params = {'numero': aviso_numero}

        if defensoria:
            params['distribuido_defensoria'] = defensoria.id

        if defensor:
            params['distribuido_cpf'] = defensor.servidor.cpf

        sucesso, resposta = APIAviso().atualizar(**params)

        if sucesso:

            # verificar se o aviso está sendo redistirbuido
            if eh_redistribuicao:
                self.registrar_redistribuicao(defensoria, defensor, resposta)
            else:
                self.registrar_distribuicao(defensoria, defensor, resposta)

            self.vincula_parte_a_defensoria_do_aviso(resposta)

            procapi_cadastrar_preanalise_honorario_aviso.apply_async(kwargs={
                'aviso': aviso_numero
            }, queue='geral')

        return sucesso, resposta

    def registrar_distribuicao(self, defensoria, defensor, aviso):
        """ registrar distribuição no solar """

        distribuicao = Distribuicao(
            numero_aviso=aviso['numero'],
            numero_processo=aviso['processo']['numero'],
            distribuido_defensor=defensor,
            distribuido_defensoria=defensoria
        )

        processo = self.get_processo(aviso)
        distribuicao.processo = processo
        distribuicao.save()

    def registrar_redistribuicao(self, defensoria, defensor, aviso):
        """ registrar redistribuição no solar """

        # verificar se não está redistribuindo para
        # o mesmo defensor ou defensoria
        # se foi, ele não registrará.
        eh_distribuicao_repetida = Distribuicao.objects.ativos().filter(
            numero_aviso=aviso['numero'],
            numero_processo=aviso['processo']['numero'],
            distribuido_defensoria=defensoria,
            distribuido_defensor=defensor,
            foi_redistribuido=False
        ).exists()

        eh_redistribuicao_repetida = Redistribuicao.objects.ativos().filter(
            distribuicao_origem__numero_aviso=aviso['numero'],
            distribuicao_origem__numero_processo=aviso['processo']['numero'],
            redistribuido_defensoria=defensoria,
            redistribuido_defensor=defensor,
            foi_redistribuido=False
        ).exists()

        # não registrar distribuição duplicada
        if eh_distribuicao_repetida or eh_redistribuicao_repetida:
            return

        redistribuicao = Redistribuicao(
            redistribuido_defensoria=defensoria,
            redistribuido_defensor=defensor
        )

        # identificar como distribuido a última redistribuição do aviso
        # Se o aviso já foi redistirbuido
        ultima_redistribuicao = Redistribuicao.objects.ativos().filter(
            distribuicao_origem__numero_aviso=aviso['numero'],
            distribuicao_origem__numero_processo=aviso['processo']['numero'],
            foi_redistribuido=False,
        ).first()

        if ultima_redistribuicao:
            ultima_redistribuicao.foi_redistribuido = True
            ultima_redistribuicao.save()

        distribuicao_origem = Distribuicao.objects.ativos().filter(
            numero_aviso=aviso['numero'],
            numero_processo=aviso['processo']['numero'],
        ).first()

        # Não salvar redistribiução de avisos
        # cujo a distrbuição não foi registrada no solar
        # para evitar inconsistência de registro.
        if distribuicao_origem:
            distribuicao_origem.foi_redistribuido = True
            distribuicao_origem.save()

            redistribuicao.distribuicao_origem = distribuicao_origem
            redistribuicao.save()

    def vincula_parte_a_defensoria_do_aviso(self, aviso):
        """
        Vincula parte processual à defensoria do aviso
        """

        if aviso['distribuido_defensoria']:

            parte = self.get_parte_processo(aviso)

            if parte:
                parte.defensoria_id = int(aviso['distribuido_defensoria'])
                parte.save()


class ProcessoService(object):
    _partes = []
    _eventos = []

    api = None
    processo = None
    numero = None
    sistema_webservice = None

    sucesso = None
    resposta = None

    def __init__(self, processo, request=None):
        self.processo = processo
        self.api = APIProcesso(self.processo.numero_procapi, request)

    @property
    def partes(self):
        if len(self._partes) == 0:
            self.consultar_partes()
        return self._partes

    @property
    def eventos(self):
        if len(self._eventos) == 0:
            self.consultar_eventos()
        return self._eventos

    def consultar(self):
        self.sucesso, self.resposta = self.api.consultar()

        if self.sucesso:
            self.sistema_webservice = self.resposta['sistema_webservice']

        return self.sucesso

    def atualizar(self):

        if self.consultar():
            self.atualizar_eventos()
            self.atualizar_defensor()
            self.atualizar_honorarios()
            self.atualizar_cabecalho(self.resposta)
        elif self.resposta and self.resposta == 'Não encontrado.':
            # Baixa se processo não foi encontrado
            self.processo.atualizado = True
            self.processo.atualizando = False
            self.processo.situacao = Processo.SITUACAO_BAIXADO
            if config.PROCAPI_PERMITE_CADASTRAR_PROCESSO_SIGILOSO:
                self.processo.tipo = Processo.TIPO_EPROC
                self.api.criar_processo_sigiloso(self.processo, self.sistema_webservice)

            self.processo.save()

        return self.sucesso

    def atualizar_data_ultima_consulta(self):
        """
        Atualiza data da última consulta no MNI
        """
        if self.resposta['data_ultima_atualizacao']:
            self.processo.ultima_consulta = self.api.to_datetime(self.resposta['data_ultima_atualizacao'])

    def atualizar_nivel_sigilo(self):
        """
        Atualiza nível de sigilo do processo
        """

        self.processo.sigiloso = self.resposta['sigiloso']

        if self.resposta['nivel_sigilo']:
            self.processo.nivel_sigilo = self.resposta['nivel_sigilo']

    def atualizar_prioridades(self):
        """
        Atualiza prioridades do processo
        """

        self.processo.prioridades.clear()

        for codigo_mni_prioridade in self.resposta['prioridades']:
            prioridade, _ = Prioridade.objects.get_or_create(
                codigo_mni=codigo_mni_prioridade,
                defaults={
                    'nome': codigo_mni_prioridade,
                }
            )
            self.processo.prioridades.add(prioridade)

    def atualizar_competencia(self):
        """
        Identifica Competência Judicial
        """
        if self.resposta['competencia']:
            self.processo.competencia_mni = self.resposta['competencia'].get('codigo')

    def atualizar_comarca(self):
        """
        Identifica Comarca
        """
        if self.processo.comarca is None and self.resposta['localidade']:

            if self.resposta['localidade'].get('comarca'):
                # Se localidade possui comarca, a usa como indentificador
                codigo_cnj = self.resposta['localidade'].get('comarca')
            else:
                # Senão, usa o codigo como indentificador
                codigo_cnj = self.resposta['localidade'].get('codigo')

            if codigo_cnj is not None:
                # procura comarca a partir do codigo ProcAPI
                self.processo.comarca = Comarca.objects.filter(codigo_eproc=codigo_cnj).first()

    def atualizar_vara(self):
        """
        Identifica Vara
        """
        from contrib.models import Vara

        if self.resposta['orgao_julgador'] and self.resposta['orgao_julgador'].get('codigo'):

            codigo_cnj = self.resposta['orgao_julgador'].get('codigo')

            # procura vara a partir do codigo ProcAPI
            self.processo.vara = Vara.objects.filter(
                orgaojulgador__sistema_webservice__nome=self.resposta['sistema_webservice'],
                orgaojulgador__codigo_mni=codigo_cnj,
                grau=self.processo.grau
            ).first()

    def atualizar_acao(self):
        """
        Identifica Ação (Classe)
        """

        # Identifica Classe (Ação)
        if self.resposta['classe'] and self.resposta['classe'].get('codigo'):

            # armazena código cnj da ação
            if not self.processo.acao_cnj:
                self.processo.acao_cnj = self.resposta['classe'].get('codigo')

            if self.processo.acao is None or self.processo.acao.area is None:

                # procura ação a partir do código cnj
                acao = Acao.objects.filter(
                    codigo_cnj=self.processo.acao_cnj
                ).first()

                # procura competência a partir do código cnj
                competencia = None
                if self.resposta['competencia'] is not None:
                    competencia = Competencia.objects.filter(
                        codigo_mni=self.resposta['competencia'].get('codigo'),
                        sistema_webservice__nome=self.sistema_webservice
                    ).first()

                # se a ação não existir, cria a partir dos dados do procapi
                if acao is None:

                    nome_cnj = self.resposta['classe'].get('nome')

                    acao = Acao.objects.create(
                        codigo_cnj=self.processo.acao_cnj,
                        nome=nome_cnj if nome_cnj else '',
                        area=competencia.area if competencia else None
                    )

                # senão, se ação não tem área, atualiza a partir dos dados do procapi
                elif acao.area is None and competencia:

                    acao.area = competencia.area
                    acao.save()

                self.processo.acao = acao  # vincula acao ao processo

            # vincula atendimentos à qualificação correspondente à classe processual
            self.atualizar_atendimentos_para_processo()

    def atualizar_assuntos(self):
        """
        Identifica Assuntos
        """
        for item in self.resposta['assuntos']:

            # se flag 'nacional' não existe ou true, assume código nacional
            if item['nacional']:
                params = {'codigo_cnj': item['codigo']}
            else:
                params = {'codigo_eproc': item['codigo']}

            if not self.processo.assuntos.filter(**params).exists():

                # procura assunto a partir do codigo cnj/eproc
                assunto = Assunto.objects.filter(**params).first()

                nome_cnj = item.get('nome')

                # se o assunto não existir, cria um novo a partir do ProcAPI
                if not assunto:
                    params['nome'] = nome_cnj if nome_cnj else ''
                    assunto = Assunto.objects.create(**params)

                # vincula assunto ao processo
                ProcessoAssunto.objects.update_or_create(
                    processo=self.processo,
                    assunto=assunto,
                    defaults={
                        'principal': item.get('principal')
                    }
                )

    def atualizar_cabecalho(self, resposta):

        self.atualizar_data_ultima_consulta()
        self.atualizar_nivel_sigilo()
        self.atualizar_prioridades()
        self.atualizar_competencia()
        self.atualizar_comarca()
        self.atualizar_vara()
        self.atualizar_acao()

        self.processo.tipo = Processo.TIPO_EPROC
        self.processo.atualizando = False
        self.processo.atualizado = True
        self.processo.save()

        self.atualizar_assuntos()

    def atualizar_defensor(self):

        if not self.processo.pre_cadastro or not self.partes:
            return False

        for parte in self.partes:

            for advogado in parte['advogados']:

                if advogado['tipo_representante'] == 'D':

                    defensor = Defensor.objects.filter(
                        usuario_eproc__iexact=advogado['identidade_principal'],
                        eh_defensor=True).first()

                    if defensor:

                        Parte.objects.filter(
                            processo=self.processo,
                            atendimento=None
                        ).exclude(
                            defensor=defensor
                        ).update(
                            defensor=defensor
                        )

                        return True

        return False

    def consultar_partes(self) -> bool:
        """
        Consulta partes (pessoas) vinculadas ao processo
        """

        partes = []
        sucesso = False

        pagina = 1
        while pagina > 0:
            sucesso, resposta_partes = self.api.consultar_partes(pagina=pagina)
            if sucesso:
                partes += resposta_partes['results']
                pagina = pagina + 1 if resposta_partes['next'] else 0
            else:
                pagina = 0

        self._partes = partes
        return sucesso

    def atualizar_partes_atendimento(self, atendimento, sigla_polo):

        self.atualizar()

        if not atendimento or not self.partes:
            return False

        for parte in self.partes:

            assistido = parte['pessoa']

            possui_representante_defensor = False
            for advogado in parte['advogados']:
                if advogado['tipo_representante'] == 'D':
                    possui_representante_defensor = True

            # Se parte possui representante do tipo D (Defensor) ou o polo seja do tipo solicitado e não exista advogado definido  # noqa: E501
            if possui_representante_defensor or (self.sistema_webservice == 'SEEU-1G-BR' and parte['tipo'] == 'PA' and parte['tipo'] == sigla_polo):  # noqa: E501

                # Verifica se documento principal é um CPF/CNPJ válido
                possui_cpf_valido = assistido['documento_principal'] and (CPF.is_cpf(assistido['documento_principal']) or CNPJ.is_cnpj(assistido['documento_principal']))  # noqa: E501

                # Verifica se parte possui nome da mãe
                possui_nome_da_mae = not assistido['nome_genitora'] is None and len(assistido['nome_genitora']) > 0

                pessoa = None

                # Se possui CPF/CNPJ válido, verifica se já possui cadastro
                if possui_cpf_valido:

                    pessoa = PessoaAssistida.objects.ativos().filter(
                        cpf=assistido['documento_principal'],
                    ).first()

                # Senão, se parte possui nome da mãe, verifica se já possui cadastro
                elif possui_nome_da_mae:

                    pessoa = PessoaAssistida.objects.ativos().filter(
                        nome__iexact=assistido['nome'],
                        filiacoes__nome__iexact=assistido['nome_genitora'],
                    ).first()

                # Se não existe, mas possui informações suficientes, prossegue com novo cadastro
                if not pessoa and (possui_cpf_valido or possui_nome_da_mae):

                    # Dados básicos
                    pessoa = PessoaAssistida.objects.create(
                        cpf=assistido['documento_principal'] if possui_cpf_valido else None,
                        nome=assistido['nome'],
                        data_nascimento=datetime.strptime(assistido['data_nascimento'], '%Y-%m-%dT%H:%M:%S') if assistido['data_nascimento'] else None,  # noqa: E501
                        sexo=PessoaAssistida.SEXO_MASCULINO if assistido['sexo'] == 'M' else PessoaAssistida.SEXO_FEMININO,  # noqa: E501
                        tipo=constantes.TIPO_PESSOA_FISICA if assistido['tipo'] == 'fisica' else constantes.TIPO_PESSOA_JURIDICA,  # noqa: E501
                        automatico=True,
                    )

                    # Dados do pai
                    if assistido['nome_genitor']:
                        PessoaFiliacao.objects.create(
                            pessoa_assistida=pessoa,
                            nome=assistido['nome_genitor'],
                            tipo=PessoaFiliacao.TIPO_PAI
                        )

                    # Dados da mãe
                    if assistido['nome_genitora']:
                        PessoaFiliacao.objects.create(
                            pessoa_assistida=pessoa,
                            nome=assistido['nome_genitora'],
                            tipo=PessoaFiliacao.TIPO_MAE
                        )

                    # Dados do endereço
                    if assistido['enderecos']:

                        endereco = assistido['enderecos'][0]

                        municipio = Municipio.objects.filter(
                            nome__iexact=endereco['cidade'],
                            estado__uf__iexact=endereco['estado']
                        ).first()

                        if municipio:

                            bairro = Bairro.objects.filter(
                                nome__iexact=endereco['bairro'],
                                municipio=municipio
                            ).first()

                            endereco = Endereco(
                                logradouro=endereco['logradouro'],
                                numero=endereco['numero'],
                                complemento=endereco['complemento'],
                                cep=endereco['cep'],
                                bairro=bairro,
                                municipio=municipio,
                            )

                            endereco.save()
                            pessoa.enderecos.add(endereco)

                # Se encontrou/cadastrou pessoa, vincula ao atendimento como requerente
                if pessoa:
                    atendimento.add_requerente(pessoa.id)

        # Se recuperou requerentes, define primeiro como responsavel
        requerente = atendimento.requerentes.first()
        if requerente:
            atendimento.set_requerente(requerente.pessoa)

    def consultar_eventos(self) -> bool:
        """
        Consulta eventos vinculados ao processo
        """

        eventos = []
        sucesso = False

        pagina = 1
        while pagina > 0:
            sucesso, resposta_eventos = self.api.consultar_eventos(pagina=pagina)
            if sucesso:
                eventos += resposta_eventos['results']
                pagina = pagina + 1 if resposta_eventos['next'] else 0
            else:
                pagina = 0

        self._eventos = eventos
        return sucesso

    def atualizar_eventos(self):
        """
        Atualiza dados dos eventos vinculados ao processo
        """
        for evento in self.eventos:
            ProcessoEventoService(self, evento).atualizar()

    def identificar_defensor_pela_parte(self) -> Defensor:
        """
        Identifica defensor pela parte processual
        """
        for parte in self.partes:
            for advogado in parte['advogados']:
                if advogado['tipo_representante'] == 'D':
                    defensor = Defensor.objects.filter(
                        servidor__cpf=advogado['documento_principal'],
                        eh_defensor=True).first()
                    if defensor:
                        return defensor

    def atualizar_honorarios(self):
        """
        Cria alerta de movimentação para honorário vinculado ao processo
        """
        if self.eventos:
            if config.VERIFICA_ATUALIZACAO_HONORARIOS:
                honorario = HonorarioService()
                honorario_id = honorario.valida_processo_id_cache(self.processo.id)
                if honorario_id:
                    honorario.cria_alerta_honorario(honorario_id)

    def atualizar_atendimentos_para_processo(self):
        """
        Atualiza qualificação dos atendimentos para processo vinculados ao processo
        """
        from atendimento.atendimento.models import Defensor as Atendimento, Qualificacao

        if self.processo.acao and self.processo.acao.area_id and self.processo.acao.nome_norm:

            # Procura/Cria qualificação correspondente à classe processual
            qualificacao = Qualificacao.objects.get_or_create_by_acao(
                acao=self.processo.acao,
                exibir_em_atendimentos=False
            )

            # Procura por todos atendimentos para processo vinculados
            atendimentos = Atendimento.objects.filter(
                parte__processo=self.processo,
                tipo=Atendimento.TIPO_PROCESSO,
            )

            # Atualiza qualificação dos atendimentos para correspondente à classe processual
            for atendimento in atendimentos:
                atendimento.qualificacao = qualificacao
                atendimento.save()

    def existe_documento_sentenca(self):
        """
        Verifica se um dos documentos do processo é uma sentença
        """
        DOCUMENTOS_SENTENCA = ['CUMPRIMENTO DE SENTENÇA', 'SENTENÇA']

        for evento in self.eventos:
            for documento in evento['documentos']:
                if documento['nome'].upper() in DOCUMENTOS_SENTENCA:
                    return True, evento

        return False, None


class ProcessoEventoService:
    sistema_webservice = None
    processo_service: ProcessoService = None
    processo = None
    evento = None

    def __init__(self, servico_processo: ProcessoService, evento: dict) -> None:
        self.sistema_webservice = servico_processo.sistema_webservice
        self.processo_service = servico_processo
        self.processo = servico_processo.processo
        self.evento = evento

    def identificar_tipo(self) -> FaseTipo:
        """
        Identifica tipo do evento
        """

        # Valor padrão para o tipo de fase
        tipo = None

        # Se tipo local, procura por tipo de fase a partir da associação com os tipos de eventos
        if self.evento.get('tipo_local'):

            codigo_tipo = self.evento.get('tipo_local')

            # Normaliza código do tipo de evento
            if codigo_tipo.strip().isdigit():
                codigo_tipo = str(int(codigo_tipo.strip()))

            # Procura por tipo de fase a partir do tipo de evento e sistema relacionado
            tipo = FaseTipo.objects.filter(
                tipos_de_evento__codigo_mni=codigo_tipo,
                tipos_de_evento__sistema_webservice__nome=self.sistema_webservice
            ).first()

            # Se não econtrou pelo tipo de evento e não tem tipo nacional, procura por tipo local (depreciado)
            if tipo is None and self.evento.get('tipo_nacional') is None:
                tipo = FaseTipo.objects.filter(codigo_eproc=codigo_tipo).order_by('-desativado_em').first()

        # Se não encontrou pelo tipo local e possui tipo nacional, procura a partir do campo "codigo_cnj"
        if tipo is None and self.evento.get('tipo_nacional'):

            codigo_tipo = self.evento.get('tipo_nacional')

            # Normaliza código do tipo de evento
            if codigo_tipo.strip().isdigit():
                codigo_tipo = str(int(codigo_tipo.strip()))

            # Recupera primeiro tipo de fase encontrado ativo ou não (preferencialmente apenas nacional e ativo)
            tipo = FaseTipo.objects.annotate(
                apenas_nacional=Case(
                    When(codigo_eproc=None, then=True),
                    output_field=BooleanField()
                )
            ).filter(
                codigo_cnj=codigo_tipo
            ).order_by(
                'apenas_nacional',
                '-desativado_em'
            ).first()

        return tipo

    def identificar_servidor(self) -> tuple[Defensor, Defensor]:
        """
        Identifica servidor que protocolou o evento
        """

        cadastrado_por = None
        assessor = None

        if self.evento['usuario']:

            # remove excesso de espaços
            self.evento['usuario'] = ' '.join(self.evento['usuario'].strip().split())
            # normaliza texto
            self.evento['usuario'] = Util.normalize(self.evento['usuario'])

            # Recupera usuarios(s) - formato "id_cadastrante" ou "id_cadastrante (id_defensor)"
            usuarios = re.split('(.+?)\((.+?)\)', self.evento['usuario'])  # noqa: W605
            usuarios = [x for x in usuarios if x]

            # Identifica cadastrante pelo usuario na primera posição do array de usários da movimentação
            if len(usuarios[0]) > 3:
                cadastrado_por = Defensor.objects.filter(
                    usuario_eproc__icontains=usuarios[0]
                ).first()

            # Identifica assessor/defensor pelo usuario na última posição do array de usários da movimentação
            if len(usuarios) > 1 and len(usuarios[-1]) > 3:
                assessor = Defensor.objects.filter(
                    usuario_eproc__icontains=usuarios[-1]
                ).first()
            else:
                assessor = cadastrado_por

        return cadastrado_por, assessor

    def atualizar(self, aviso=None) -> Fase:

        _fase = None
        tipo = self.identificar_tipo()

        if tipo:

            defensoria = None
            defensor = None
            cadastrado_por, assessor = self.identificar_servidor()
            data_protocolo = APIProcesso.to_datetime(self.evento['data_protocolo'])

            if aviso is not None:
                defensoria = AvisoService().get_defensoria(aviso)

            if assessor:
                # Se é um defensor, vincula evento a ele
                if assessor.eh_defensor:
                    defensor = assessor
                # Senão se petição inicial (evento 1), verifica que defensor atuou na defensoria cadastro da parte autora no dia do evento # noqa: E501
                elif self.evento['numero'] == 1:

                    parte = self.processo.parte.filter(parte=Parte.TIPO_AUTOR, ativo=True).first()

                    if parte:
                        atuacao = Atuacao.objects.filter(
                            Q(defensoria=parte.defensoria_cadastro) &
                            ~Q(tipo=Atuacao.TIPO_LOTACAO) &
                            Q(data_inicial__lte=data_protocolo) &
                            (
                                Q(data_final__gte=data_protocolo) |
                                Q(data_final=None)
                            )
                        ).order_by(
                            '-data_inicial',
                            'tipo'
                        ).first()

                        if atuacao:
                            defensor = atuacao.defensor

            if defensor is None:
                # Se aviso informado, identifica defensor pelo aviso
                if aviso is not None:
                    cadastrado_por = defensor = AvisoService().identificar_defensor(aviso, defensoria)
                # Se evento é sentença, identica defensor pelas partes do processo
                elif tipo.sentenca and self.processo_service.partes:
                    cadastrado_por = defensor = self.processo_service.identificar_defensor_pela_parte()

            # Cadastra a movimentação se encontrou algum defensor vinculado ou é de defensoria
            if defensor or self.evento['defensoria']:

                # Procura por fase processual com mesma data ou evento
                _fase = Fase.objects.filter(
                    Q(processo=self.processo) &
                    Q(ativo=True) &
                    Q(data_protocolo=data_protocolo) &
                    (
                        Q(evento_eproc=self.evento['numero']) |
                        Q(evento_eproc=None)
                    )
                ).first()

                if _fase:
                    if _fase.defensor_cadastro is None and defensor is not None:
                        _fase.defensor_cadastro = defensor
                        _fase.cadastrado_por = cadastrado_por.servidor if cadastrado_por else None
                        _fase.evento_eproc = self.evento['numero']
                        _fase.usuario_eproc = self.evento['usuario']
                        _fase.save()
                    if _fase.defensoria is None and defensoria is not None:
                        _fase.defensoria = defensoria
                        _fase.save()

                # Procura por fase processual gerada a partir do peticionamento
                # OBS: a verificação anterior não encontra a fase porque a data de protocolo dela possui uma
                # diferença de alguns segundos comparado com a data de confirmação de entrega da manifestação
                # No EPROC a data da confirmação é menor que a data do movimento
                # No SEEU a data de confirmação é manor que a data do movimento
                # Por isso, procura com margem de erro de 30 segundos pra mais ou pra menos
                if not _fase:

                    _fase = Fase.objects.filter(
                        Q(processo=self.processo) &
                        Q(ativo=True) &
                        Q(manifestacao__isnull=False) &
                        Q(data_protocolo__range=[
                            data_protocolo - timedelta(seconds=60),
                            data_protocolo + timedelta(seconds=60)
                        ]) &
                        (
                            Q(evento_eproc=self.evento['numero']) |
                            Q(evento_eproc=None)
                        )
                    ).first()

                    # Completa preenchimento da fase processual com dados obtidos via MNI
                    if _fase and not _fase.evento_eproc:
                        _fase.evento_eproc = self.evento['numero']
                        _fase.usuario_eproc = self.evento['usuario']
                        _fase.save()

                # Se não encontrou pelos dois métodos acima, cria uma nova fase a partir dos dados do MNI
                if not _fase:

                    _fase = Fase(
                        tipo=tipo,
                        processo=self.processo,
                        descricao=self.evento['descricao'].encode('utf-8'),
                        defensoria=defensoria,
                        defensor_cadastro=defensor,
                        cadastrado_por=cadastrado_por.servidor if cadastrado_por else None,
                        data_protocolo=data_protocolo,
                        evento_eproc=self.evento['numero'],
                        usuario_eproc=self.evento['usuario'],
                        automatico=True)

                    _fase.save()

                self.atualizar_documentos(_fase)

        return _fase

    def atualizar_documentos(self, _fase):
        for documento in self.evento['documentos']:

            tipo_documento = DocumentoTipo.objects.filter(
                grau=self.processo.get_grau(),
                eproc=documento['tipo']
            ).first()

            # Se nome não informado, tenta descobrir pelo tipo do documento
            if documento['nome'] is None:

                if tipo_documento:
                    _documento_nome = tipo_documento.nome
                else:
                    _documento_nome = documento['tipo']

            else:

                _documento_nome = documento['nome']

            _documento = DocumentoFase.objects.filter(
                eproc=int(documento['documento']),
                ativo=True
            ).first()

            if _documento:
                _documento.tipo = tipo_documento
                _documento.fase = _fase
                _documento.nome = _documento_nome
                _documento.save()
            else:
                _documento = DocumentoFase.objects.create(
                    eproc=documento['documento'],
                    ativo=True,
                    fase=_fase,
                    nome=_documento_nome
                )

            # Se primeiro evento e documento é uma petição inicial define no processo
            if _fase.evento_eproc == 1 and _documento_nome == u'PETIÇÃO INICIAL':
                self.processo.peticao_inicial = _fase


class FaseService(object):

    def set_plantao(self, ano=datetime.now().year, mes=datetime.now().month, dia=datetime.now().day, dias=1):
        """
        Marca como plantao fases processuais criadas no periodo de plantao.
        :param ano: Ano de referencia (padrao: ano atual)
        :param mes: Mes de referencia (padrao: mes atual)
        :param dia: Dia de referencia (padrao: dia atual)
        :return: None
        """
        data_hoje = datetime(year=ano, month=mes, day=dia)
        data_referencia = data_hoje - timedelta(days=dias)

        for atuacao in Atuacao.objects.filter(
                defensoria__nucleo__plantao=True,
                data_final__gte=data_referencia,
                data_inicial__lte=data_hoje):

            Fase.objects.filter(
                Q(defensor_cadastro=atuacao.defensor) &
                Q(data_protocolo__gte=atuacao.data_inicial) &
                Q(data_protocolo__lte=atuacao.data_final) &
                (
                    Q(processo__parte__defensoria_cadastro__nucleo__plantao=True) |
                    ~Q(processo__parte__defensor=atuacao.defensor)
                ) &
                Q(plantao=False)
            ).update(plantao=True)

    def set_tipo_fase_processual(self):

        resposta = {}

        # Audiencia
        resposta['audiencia'] = Fase.objects.filter(
            tipo__audiencia=True,
            tipo__juri=False,
            ativo=True
        ).exclude(
            atividade=Fase.ATIVIDADE_AUDIENCIA
        ).update(
            atividade=Fase.ATIVIDADE_AUDIENCIA
        )

        # Juri
        resposta['jur'] = Fase.objects.filter(
            tipo__juri=True,
            ativo=True
        ).exclude(
            atividade=Fase.ATIVIDADE_JURI
        ).update(
            atividade=Fase.ATIVIDADE_JURI
        )

        # Sentenca
        resposta['sentenca'] = Fase.objects.filter(
            tipo__sentenca=True,
            ativo=True
        ).exclude(
            atividade=Fase.ATIVIDADE_SENTENCA
        ).update(
            atividade=Fase.ATIVIDADE_SENTENCA
        )

        recursos = DocumentoTipo.objects.filter(
            recurso=True,
            ativo=True
        ).order_by(
            'nome'
        ).distinct(
            'nome'
        ).values_list('nome', flat=True)

        # Recurso
        resposta['recurso'] = Fase.objects.filter(
            Q(ativo=True),
            Q(documentofase__nome__in=set(recursos)),
            ~Q(atividade=Fase.ATIVIDADE_RECURSO),
        ).update(
            atividade=Fase.ATIVIDADE_RECURSO
        )

        return resposta

    def corrigir_data_cadastro(self):
        sql = """
        UPDATE processo_fase AS pf
                SET data_cadastro = data_protocolo
                FROM processo_processo AS pp, processo_parte AS ppa
                WHERE (
                    date_part('YEAR',pf.data_cadastro) != date_part('YEAR', pf.data_protocolo)
                    OR date_part('MONTH',pf.data_cadastro) != date_part('MONTH', pf.data_protocolo))
                AND pf.data_protocolo >= now()::DATE - INTERVAL '1 month' - INTERVAL '1 day' * (date_part('day', now()::DATE - INTERVAL '1 month') - 1)
                AND pf.automatico = TRUE
                AND pf.ativo=TRUE
                AND ppa.data_cadastro <= pf.data_protocolo
                AND ppa.ativo=TRUE
                AND pp.ativo=TRUE
                AND pp.pre_cadastro=FALSE
                AND pp.id = pf.processo_id
                AND ppa.processo_id = pp.id
        """  # noqa: E501,W291
        if datetime.now().day <= config.DIA_LIMITE_CADASTRO_FASE:
            cursor = connection.cursor()
            cursor.execute(sql)


def salvar_processo(dados, servidor=None, usuario=None):

    sucesso = False
    processo = None
    parte = None
    atendimento = None

    if 'numero' in dados:
        numero = re.sub('[^0-9]', '', dados['numero'])

    if numero:

        # o atendimento para processo fica em nome do cadastrante
        dados_atendimento = {
            'defensor': dados.get('defensor_cadastro'),
            'defensoria': dados.get('defensoria_cadastro'),
            'nucleo': dados.get('nucleo'),
            'modificado_por': servidor,
        }

        # Procura/Cria qualificação correspondente à classe processual
        if dados.get('acao'):

            acao = Acao.objects.get(id=dados.get('acao'))
            qualificacao = None

            if acao.area and acao.nome_norm:
                qualificacao = Qualificacao.objects.get_or_create_by_acao(acao=acao)

            if qualificacao:
                dados_atendimento['qualificacao'] = qualificacao.id

        if 'atendimento_numero' in dados:

            atendimento = get_object_or_404(AtendimentoDefensor, numero=dados['atendimento_numero'])

            if atendimento.tipo == Atendimento.TIPO_PROCESSO:

                form = AtendimentoForm(dados_atendimento, instance=atendimento)

                if form.is_valid():
                    atendimento = form.save()

        else:

            atendimento = AtendimentoDefensor(tipo=Atendimento.TIPO_PROCESSO, cadastrado_por=servidor)
            form = AtendimentoForm(dados_atendimento, instance=atendimento)

            if form.is_valid():
                atendimento = form.save()
                Acesso.conceder_publico(atendimento, None)

        if 'requerente' in dados:
            atendimento.set_requerente(dados['requerente'])

        agora = datetime.now()

        processo, processo_new = Processo.objects.get_or_create(
            numero_puro=numero,
            grau=dados['grau'],
            defaults={
                'numero': dados.get('numero'),
                'cadastrado_por': servidor,
                'ativo': True
            })

        # Guarda situação original de processo pré-cadastrado
        pre_cadastro = processo.pre_cadastro

        if (not processo_new and (not processo.ativo or processo.pre_cadastro)):
            processo.pre_cadastro = False
            processo.ativo = True
            processo.data_cadastro = agora
            processo.cadastrado_por = servidor
            processo.data_exclusao = None
            processo.excluido_por = None

            # Atualiza data de cadastro das fases para agora
            processo.fases.filter(ativo=True).update(data_cadastro=agora, cadastrado_por=servidor)

        parte_new = False
        defensor_pre_cadastro = None

        atendimentos = list(atendimento.at_inicial.retornos.values_list('id', flat=True))
        atendimentos.append(atendimento.at_inicial.id)

        if pre_cadastro:

            # Vincula atendimento para processo a parte
            parte = Parte.objects.filter(processo=processo, ativo=True).first()

            if not parte:
                parte = Parte(processo=processo)

            parte.data_cadastro = agora
            parte.atendimento = atendimento
            parte.save()

            defensor_pre_cadastro = parte.defensor

            # Atualiza data de cadastro das fases para agora
            processo.fases.update(data_cadastro=agora)

        else:

            parte = Parte.objects.filter(processo=processo, atendimento__in=atendimentos, ativo=True).first()
            parte_new = parte is None

            if not parte:

                dados_iniciais = {
                    'processo': processo,
                    'atendimento': atendimento,
                    'cadastrado_por': servidor,
                    'ativo': True
                }

                if config.ATIVAR_ESAJ:
                    dados_iniciais['defensoria'] = atendimento.defensoria

                parte = Parte.objects.create(**dados_iniciais)

        if usuario is not None:
            reversion.set_user(usuario)
            reversion.set_comment(Util.get_comment_save(usuario, parte, parte_new))

        form = ProcessoForm(dados, instance=processo)

        if form.is_valid():

            processo = form.save()
            form_parte = ProcessoParteForm(dados, instance=parte)

            if form_parte.is_valid():

                sucesso = True

                parte.cadastrado_por = servidor
                form_parte.save()

                if defensor_pre_cadastro:
                    # Gera lista de todos os caches de defensores/assessores afetados
                    defensores = list(defensor_pre_cadastro.lista_assessores.values_list('id', flat=True))
                    defensores.append(defensor_pre_cadastro.id)

                    for defensor in defensores:
                        cache.delete('processo_pendentes_defensor:{0}'.format(defensor))

                if parte_new and parte.defensoria_cadastro.nucleo and parte.defensoria_cadastro.nucleo.plantao:
                    Tarefa.objects.create(
                        atendimento=atendimento,
                        responsavel=parte.defensor.servidor if parte.defensor else None,
                        resposta_para=parte.defensoria_cadastro,
                        setor_responsavel=parte.defensoria,
                        prioridade=Tarefa.PRIORIDADE_ALERTA,
                        titulo=u'PROCESSO CADASTRADO NO PLANTÃO',
                        descricao=u'Processo {} cadastrado no plantão por {}'.format(
                            processo.numero,
                            parte.cadastrado_por
                        )
                    )

                if usuario is not None:  # Usuário foi definido, indicando que o método foi acionado pela View
                    if atendimento.tipo == Atendimento.TIPO_PROCESSO and processo.tipo == Processo.TIPO_EPROC:
                        servico = ProcessoService(processo)
                        servico.atualizar_partes_atendimento(atendimento, parte.sigla_parte)
                        if config.PROCAPI_ATIVAR_INFORMAR_PERFIL_PROJUDI and processo.credencial_mni_cadastro is None:
                            processo.credencial_mni_cadastro = usuario.servidor.defensor.usuario_eproc
                            processo.save()

                    if config.ATIVAR_PROCAPI and processo.get_tipo() == Processo.TIPO_EPROC:
                        from .tasks import procapi_atualizar_processo
                        params = {
                                    'numero': processo.numero_inteiro,
                                    'grau': processo.grau,
                                }
                        if config.PROCAPI_PERMITE_CADASTRAR_PROCESSO_SIGILOSO:
                            params['sistema_webservice'] = dados['sistema_webservice']

                        if settings.DEBUG:
                            procapi_atualizar_processo(**params)
                        else:
                            procapi_atualizar_processo.apply_async(
                                kwargs=params,
                                queue='sobdemanda'
                            )

                else:  # Usuáio não foi definido, indicando que método foi acionado pela Task

                    servico = ProcessoService(processo)
                    servico.atualizar_partes_atendimento(atendimento, parte.sigla_parte)
                    from .tasks import procapi_atualizar_processo
                    procapi_atualizar_processo.apply_async(kwargs={
                                'numero': processo.numero_inteiro,
                                'grau': processo.grau,
                            }, queue='sobdemanda')

    return sucesso, processo, parte, atendimento
