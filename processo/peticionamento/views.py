# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import base64
import json
import uuid
from datetime import datetime, time, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import BooleanField, Case, Count, Q, Value, When
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView, TemplateView, View

# Bibliotecas de terceiros
from constance import config
from djdocuments.models import NaoPodeAssinarException
from djdocuments.views.mixins import DocumentoFinalizarMixin

# Solar
from assistido.models import Documento as DocumentoAssistido
from atendimento.atendimento.models import Defensor as Atendimento
from atendimento.atendimento.models import Documento as DocumentoAtendimento
from atendimento.atendimento.models import Pessoa as PessoaAtendimento
from atendimento.precadastro.forms import EnderecoForm
from contrib import constantes
from contrib.models import Estado, Util, Vara
from contrib.services import AudioToMP3Service, ImageToPDFService
from core.views import SoftDeleteView
from defensor.models import Atuacao
# Signo
from notificacoes.tasks import notificar_manifestacao_em_analise
from procapi_client.services import (
    APIAviso,
    APIManifestacao,
    APIManifestante,
    APIOrgaoJulgador,
    APIProcesso,
    APISistema,
    APITipoDocumento
)
# Modulos locais
from processo.processo import models
from processo.processo.forms import (
    BuscarManifestacaoForm,
    ProcessoPeticionamentoForm
)
from processo.processo.models import (
    Assunto,
    Manifestacao,
    ManifestacaoAviso,
    ManifestacaoDocumento,
    ManifestacaoParte,
    OutroParametro,
    Parte,
    Processo,
    ProcessoAssunto,
    ProcessoOutroParametro
)
from processo.processo.tasks import (
    procapi_atualizar_manifestacao,
    procapi_enviar_manifestacao
)


class AtendimentoProcessoListView(TemplateView):
    template_name = 'processo/peticionamento/atendimento_processos.html'

    def get_context_data(self, **kwargs):

        dados = self.request.GET

        # Consulta dados do atendimento
        atendimento = Atendimento.objects.get(
            numero=self.kwargs.get('atendimento_numero'),
            ativo=True,
            remarcado=None
        )

        partes = atendimento.get_processo_partes().filter(
            processo__tipo=Processo.TIPO_EPROC,
            processo__pre_cadastro=False
        )

        # Envia sinal para o procapi consultar os avisos
        if partes.exists():
            # Se é defensor, usa cpf do usuário
            if self.request.user.servidor.defensor.eh_defensor:
                cpfs_supervisores = [self.request.user.servidor.cpf]
            # Se é assessor, obtém cpf dos defensores vinculados
            else:
                cpfs_supervisores = self.request.user.servidor.defensor.lista_supervisores.values_list('servidor__cpf', flat=True)  # noqa: E501

            for cpf_supervisor in cpfs_supervisores:
                if Util.cpf_cnpj_valido(cpf_supervisor):
                    APIManifestante().consultar_avisos(cpf=cpf_supervisor)

        # Consulta dados dos sistemas no ProcAPI
        api = APISistema()
        sucesso, sistemas_resposta = api.listar()

        # Guarda dados consultados dos sistemas
        sistemas = {}

        if sucesso:
            for item in sistemas_resposta['results']:
                sistemas[item['nome']] = item
        else:
            messages.error(self.request, sistemas_resposta)

        # Verifica disponibilidade geral dos sistemas
        pode_entregar_peticao = False

        for key in sistemas:
            if sistemas[key]['pode_entregar_peticao']:
                pode_entregar_peticao = True

        # Consulta dados no ProcAPI relacionados aos processos
        for parte in partes:

            # Consulta ProcAPI
            processo = APIProcesso(parte.processo.numero_procapi, self.request)
            sucesso, resposta = processo.consultar()

            if sucesso:
                # Guarda dados consultados na parte
                parte.procapi = resposta
                # Verifica que o sistema onde está o processo pode entregar manifestação
                parte.pode_entregar_peticao = sistemas[resposta['sistema_webservice']]['pode_entregar_peticao']
            else:
                messages.error(self.request, resposta)

        # Consulta dados dos documentos a partir da lista de ids
        documentos_atendimento = DocumentoAtendimento.objects.filter(id__in=dados.getlist('doc_atendimento'))
        documentos_pessoais = DocumentoAssistido.objects.filter(id__in=dados.getlist('doc_pessoal'))

        # Recupera lista de documentos ordenada
        documentos = dados.get('documentos')

        # Se lista não foi fornecida, gera a partir do documento enviado
        if not documentos:
            documentos = ','.join(dados.getlist('doc_atendimento'))

        context = super(AtendimentoProcessoListView, self).get_context_data(**kwargs)

        # Atualiza variáveis de contexto (visíveis no template)
        context.update({
            'atendimento': atendimento,
            'documentos': documentos,
            'documentos_atendimento': documentos_atendimento,
            'documentos_pessoais': documentos_pessoais,
            'partes': partes,
            'sistemas': sistemas_resposta['results'] if 'results' in sistemas_resposta else None,
            'pode_entregar_peticao': pode_entregar_peticao,
        })

        return context


class SalvarManifestacaoMixin:
    '''
    Obtém dados da manifestação e documentos vinculados a partir da requisição e salva no banco de dados
    '''

    def post(self, request, *args, **kwargs):

        # Obtém dados da requisição
        dados = request.POST.copy()
        parte = None
        tipo = Manifestacao.TIPO_PETICAO
        manifestacao = None

        # Obtém dados da parte processual
        if dados.get('parte_id'):
            parte = Parte.objects.get(id=dados.get('parte_id'), ativo=True)
            processo = parte.processo
        # Cria processo/parte (petição inicial)
        else:
            processo = Processo(
                numero=str(uuid.uuid4()),  # gera um número aleatório para gravar no banco
                tipo=Processo.TIPO_EPROC,
                pre_cadastro=True,
                ativo=True
            )

        defensoria_id = None
        usuario_defensor_id = None

        # Obtém dados da atuação ou defensoria
        if dados.get('atuacao_id'):
            atuacao = Atuacao.objects.get(id=dados.get('atuacao_id'))
            defensoria_id = atuacao.defensoria_id
            usuario_defensor_id = atuacao.defensor.servidor.usuario_id
        elif dados.get('defensoria_id'):
            defensoria_id = dados.get('defensoria_id')

        # Se petição em processo pré-cadastro, então é petição inicial
        if processo.pre_cadastro:
            tipo = Manifestacao.TIPO_PETICAO_INICIAL

        # Se petição inicial, atualiza dados do processo e partes do atendimento
        if tipo == Manifestacao.TIPO_PETICAO_INICIAL:

            atendimento_numero = None

            if 'atendimento_numero' in self.kwargs:
                atendimento_numero = self.kwargs.get('atendimento_numero')
            else:
                atendimento_numero = dados.get('atendimento_numero')

            # Consulta dados do atendimento
            atendimento = Atendimento.objects.get(numero=atendimento_numero)

            # Atualiza dados das partes do atendimento incluído/removendo relacionamentos
            for parte in atendimento.pessoas:

                representante = dados.get('representante_{}'.format(parte.id))
                representacao = dados.get('representacao_{}'.format(parte.id))

                if representacao and representante:
                    parte.representante_id = representante
                    parte.representante_modalidade = representacao
                else:
                    parte.representante_id = None
                    parte.representante_modalidade = None

                parte.save()

            # Atualiza dados do processo
            form_processo = ProcessoPeticionamentoForm(
                atendimento=atendimento,
                editavel=False,
                sistema_webservice=dados.get('sistema_webservice'),
                data=dados,
                instance=processo,
                initial={}
            )

            if form_processo.is_valid():

                processo = form_processo.save()

                # Obtem ação salva no SOLAR através do Codigo CNJ do frontend enviado pelo PROCAPI
                processo.acao = models.Acao.objects.filter(
                    codigo_cnj=form_processo.cleaned_data['acao_form']
                ).first()

                processo.acao_cnj = form_processo.cleaned_data['acao_form']

                varas_codigos = APIOrgaoJulgador().obter_codigos_vara_por_sistema_webservice(
                    sistema=dados.get('sistema_webservice')
                )

                # Se existir processo originário, usa a vara desse processo
                # Senão, obtém a primeira vara vinculada à Comarca
                if (
                    processo.originario and
                    processo.originario.tipo in [Processo.TIPO_EPROC, Processo.TIPO_FISICO] and
                    processo.originario.vara and
                    processo.originario.vara.codigo_eproc in varas_codigos  # previne que seja selecionado vara de um processo de outro sistema # noqa: E501
                ):
                    processo.vara = processo.originario.vara
                else:
                    processo.vara = Vara.objects.filter(
                        ativo=True,
                        comarca=processo.comarca,
                        codigo_eproc__isnull=False,
                        codigo_eproc__in=varas_codigos
                    ).exclude(codigo_eproc__exact='').first()

                # Limpa assuntos antigos antes de vincular os novos
                processo.assuntos.clear()

                assunto_principal = form_processo.cleaned_data['assunto_principal_form']
                assuntos_secundarios = form_processo.cleaned_data['assuntos_secundarios_form']
                assuntos = [assunto_principal] + assuntos_secundarios

                for assunto in Assunto.objects.filter(codigo_cnj__in=assuntos):

                    principal = (assunto.codigo_cnj == assunto_principal)

                    ProcessoAssunto.objects.create(
                        processo=processo,
                        assunto=assunto,
                        principal=principal
                    )

                # Limpa outros parâmetros antigos antes de vincular os novos
                processo.outros_parametros.clear()

                # Adiciona os assuntos secundários
                for outro_parametro in form_processo.cleaned_data['outros_parametros_form']:
                    outro_param, novo = ProcessoOutroParametro.objects.get_or_create(
                        processo=processo,
                        outro_parametro=outro_parametro,
                        defaults={
                            'valor': 'true'
                        }
                    )

                    # Atendimento em prioridade de plantão para petição inicial.
                    # Aqui será tratado o parâmetro do tipo texto
                    # Para ser enviado nos outros parâmetro do processo na manifestação.
                    # Como no form os 'outros parâmetros' são tratados apenas como booleano.
                    # Os parâmetros com texto colocou-se um texto obtido do campo lista do objeto "OurtroParometro"
                    # Por enquanto, isto está restrito a nossa a UF, do Pará
                    # TODO: Até a elaboração de uma solução mais abrangente para lidar com petcionamento em plantão.
                    if settings.SIGLA_UF == 'PA':
                        if outro_param.outro_parametro.tipo == OutroParametro.TIPO_TEXTO:
                            outro_param.valor = outro_param.outro_parametro.lista
                            outro_param.save()

                        # No peticionamento em plantão no PJE, é necessário adicionar o atributo atendimentoPlantao e situacaoProcesso  # noqa: E501
                        # Forçar a adicição do atributo situacaoProcesso em outros parâmetros quando o peticinamento for em plantão  # noqa: E501
                        eh_plantao = outro_param.outro_parametro.codigo_mni.find('Plantao') > -1
                        if eh_plantao:

                            situacao_processo_outro_parametro = OutroParametro.objects.filter(
                                codigo_mni__contains='situacaoProcesso'
                            ).first()

                            if situacao_processo_outro_parametro:
                                ProcessoOutroParametro.objects.update_or_create(
                                    processo=processo,
                                    outro_parametro=situacao_processo_outro_parametro,
                                    defaults={
                                        'valor': situacao_processo_outro_parametro.lista
                                    }
                                )

                            else:
                                raise Exception('Para o peticionamento em plantão no PJE, também é necessário haver o parâmetro situacaoProcesso.')  # noqa: E501

            else:
                raise Exception(form_processo.errors)

            # Cria/Atualiza dados da parte processual
            parte, _ = Parte.objects.update_or_create(
                processo=processo,
                atendimento=atendimento,
                defaults={
                    'defensoria_id': defensoria_id,
                    'defensoria_cadastro_id': defensoria_id,
                    'ativo': True
                })

        if dados.get('pk'):
            manifestacao = Manifestacao.objects.get(id=dados.get('pk'))
        else:
            manifestacao = Manifestacao.objects.create(
                parte=parte,
                situacao=Manifestacao.SITUACAO_ANALISE,
                desativado_em=None,
                tipo=tipo,
                defensoria_id=defensoria_id,
                defensor_id=usuario_defensor_id,
                sistema_webservice=dados.get('sistema_webservice')
            )

        # Se ainda não existe, cria fase processual vinculada à manifestação
        if not manifestacao.fase:

            manifestacao.fase = models.Fase.objects.create(
                processo=processo,
                parte=parte,
                tipo_id=dados.get('tipo_fase'),
                data_cadastro=manifestacao.cadastrado_em,
                cadastrado_por=manifestacao.cadastrado_por.servidor,
                automatico=True,
                ativo=False  # Só é ativado quando houver a confirmação do protocolo
            )
            manifestacao.save()

        # Se é uma petição inicial, vincula a campo específico no processo
        if manifestacao.tipo == models.Manifestacao.TIPO_PETICAO_INICIAL:
            processo.peticao_inicial = manifestacao.fase
            processo.save()

        # Atualiza informações da fase processual vinculada à manifestação
        manifestacao.fase.tipo_id = dados.get('tipo_fase')
        manifestacao.fase.save()

        # Desativa partes (pessoas) vinculadas anteriormente ao novo processo
        manifestacao.partes.all().update(
            desativado_por=self.request.user,
            desativado_em=datetime.now()
        )

        # Adiciona partes (pessoas) que serão vinculadas ao novo processo
        for parte in dados.getlist('partes'):
            ManifestacaoParte.objects.update_or_create(
                manifestacao=manifestacao,
                parte_id=parte,
                defaults={
                    'desativado_por': None,
                    'desativado_em': None
                }
            )

        # Adiciona dados dos documentos do atendimento
        for doc in dados.getlist('docs_atendimento'):

            documento, novo = ManifestacaoDocumento.objects.update_or_create(
                manifestacao=manifestacao,
                origem=ManifestacaoDocumento.ORIGEM_ATENDIMENTO,
                origem_id=doc,
                defaults={
                    'posicao': dados.get('pos_atendimento_{}'.format(doc)),
                    'tipo_mni': dados.get('doc_atendimento_{}'.format(doc)),
                    'nivel_sigilo': dados.get('sig_atendimento_{}'.format(doc))
                }
            )

            # Marca GED como pronto para assinar caso o assessor tenha esquecido de fazer antes
            # (replicado da view "DocumentoMarcarDesmarcarProntoParaAssinar")
            if hasattr(documento.get_origem, 'documento_online') and documento.get_origem.documento_online:
                documento_ged = documento.get_origem.documento_online
                # Verifica se documento não está assinado e não está pronto para assinar
                if not documento_ged.esta_assinado and not documento_ged.esta_pronto_para_assinar:
                    documento_ged.esta_pronto_para_assinar = True
                    documento_ged._desabilitar_temporiariamente_versao_numero = True
                    documento_ged.save()

            else:

                # TODO: Mover esse código para outro lugar (task) que execute antes da assinatura com token
                # Converte arquivo para formato válido
                if AudioToMP3Service(documento.get_origem).is_valid():
                    AudioToMP3Service(documento.get_origem).export_and_replace()
                elif ImageToPDFService(documento.get_origem).is_valid():
                    ImageToPDFService(documento.get_origem).export_and_replace()

        # Adiciona dados dos documentos pessoais
        for doc in dados.getlist('docs_pessoal'):

            documento, novo = ManifestacaoDocumento.objects.update_or_create(
                manifestacao=manifestacao,
                origem=ManifestacaoDocumento.ORIGEM_PESSOA,
                origem_id=doc,
                defaults={
                    'posicao': dados.get('pos_pessoal_{}'.format(doc)),
                    'tipo_mni': dados.get('doc_pessoal_{}'.format(doc)),
                    'nivel_sigilo': dados.get('sig_pessoal_{}'.format(doc))
                }
            )

            # TODO: Mover esse código para outro lugar (task) que execute antes da assinatura com token
            # Converte arquivo para formato válido
            if AudioToMP3Service(documento.get_origem).is_valid():
                AudioToMP3Service(documento.get_origem).export_and_replace()
            elif ImageToPDFService(documento.get_origem).is_valid():
                ImageToPDFService(documento.get_origem).export_and_replace()

        # Desativa avisos vinculados anteriormente
        manifestacao.avisos.all().update(
            desativado_por=self.request.user,
            desativado_em=datetime.now()
        )

        # Adiciona avisos que terão o prazo fechado
        for prazo in dados.getlist('prazos'):
            ManifestacaoAviso.objects.update_or_create(
                manifestacao=manifestacao,
                numero=prazo,
                defaults={
                    'desativado_por': None,
                    'desativado_em': None
                }
            )

        return manifestacao


class EnviarParaAnaliseView(View, SalvarManifestacaoMixin):
    '''
    Envia dados da manifestação para análise do defensor
    '''

    def post(self, request, *args, **kwargs):

        manifestacao = super(EnviarParaAnaliseView, self).post(request, *args, **kwargs)

        messages.success(request, u'Manifestação nº {:04d} enviada para análise!'.format(manifestacao.id))

        if config.NOTIFICAR_MANIFESTACAO_EM_ANALISE:
            notificar_manifestacao_em_analise.apply_async(kwargs={
                'manifestacao_id': manifestacao.id
            }, queue='sobdemanda')

        return redirect('peticionamento:visualizar', pk=manifestacao.pk)


class IndexView(TemplateView, SalvarManifestacaoMixin):

    template_name = 'processo/peticionamento/manifestacao.html'

    def get_context_data(self, **kwargs):

        dados = self.request.GET
        documentos = []
        assuntos = []
        recibo = None
        parte = None
        tipos_documento = None
        documentos_para_assinatura = False
        possui_autor = True
        possui_reu = True
        requerente_tem_endereco = []
        requerido_tem_endereco = []
        pessoas = []
        pessoas_sem_documento = False
        prazos = []

        # Filtro base para exibir manifestações potencialmente duplicadas
        outras_manifestacoes = Manifestacao.objects.ativos().exclude(
            situacao=Manifestacao.SITUACAO_PROTOCOLADO
        )

        # Se pk da manifestação foi informado, obtém dados a partir do banco de dados, senão, obtém dados da requisição
        if self.kwargs.get('pk'):

            manifestacao = Manifestacao.objects.get(pk=self.kwargs.get('pk'))
            documentos = manifestacao.documentos.ativos().order_by('posicao')

            # Verifica se existem documentos pendentes de assinatura
            documentos_para_assinatura = DocumentoAtendimento.objects.filter(
                id__in=documentos.filter(origem=ManifestacaoDocumento.ORIGEM_ATENDIMENTO).values('origem_id'),
                documento_online__esta_assinado=False
            ).exists()

            # Conta quantos documentos ged estão na petição
            total_documentos_ged = DocumentoAtendimento.objects.filter(
                id__in=documentos.filter(origem=ManifestacaoDocumento.ORIGEM_ATENDIMENTO).values('origem_id'),
            ).exclude(
                documento_online=None
            ).count()

            # Pode excluir documento se tem mais de um ged ou se o documento é um anexo
            for documento in documentos:
                documento.pode_excluir = total_documentos_ged > 1 or not (hasattr(documento.get_origem, 'documento_online') and documento.get_origem.documento_online)  # noqa: E501

            parte = manifestacao.parte
            atendimento = parte.atendimento

            # Remove manifestação da lista de outras manifestações
            outras_manifestacoes = outras_manifestacoes.exclude(id=manifestacao.id)

        else:

            # Consulta dados do atendimento
            atendimento = Atendimento.objects.get(numero=self.kwargs.get('atendimento_numero'))

            # destino_id -> se numérico é o id da parte processual, senão é o id do sistema webservice
            parte_id, sistema_webservice = dados.get('destino_id').split(',')

            # Consulta dados da parte processual
            if parte_id:

                parte = Parte.objects.get(id=parte_id, ativo=True)

                # Gera manifestação virtual para obter dados já disponíveis a partir da parte
                manifestacao = Manifestacao(
                    tipo=Manifestacao.TIPO_PETICAO,
                    sistema_webservice=sistema_webservice,
                    defensoria=parte.defensoria
                )

            else:

                # Gera manifestação virtual para obter dados já disponíveis a partir do atendimento (novo processo)
                manifestacao = Manifestacao(
                    tipo=Manifestacao.TIPO_PETICAO_INICIAL,
                    sistema_webservice=sistema_webservice,
                    defensoria=atendimento.defensoria
                )

            # Consulta documentos do atendimento ou pessoa de acordo com a lista ordenada
            for posicao, documento_id in enumerate(dados.get('documentos').split(',')):
                origem = ManifestacaoDocumento.ORIGEM_ATENDIMENTO if int(documento_id) > 0 else ManifestacaoDocumento.ORIGEM_PESSOA  # noqa: E501
                documentos.append(ManifestacaoDocumento(
                    origem=origem,
                    origem_id=abs(int(documento_id)),
                    posicao=posicao
                ))

        # identifica defensorias onde o usuario está lotado
        defensorias = self.request.user.servidor.defensor.defensorias

        # identifica atuações dos supervisores do usuário lotado
        atuacoes_para_analise = Atuacao.objects.select_related(
            'defensor__servidor',
        ).vigentes(ajustar_horario=False).filter(
            defensor__eh_defensor=True,
            defensoria__in=defensorias,
            defensoria__pode_vincular_processo_judicial=True
        )

        # identifica atuações dos supervisores da defensoria selecionada
        atuacoes_para_protocolo = Atuacao.objects.select_related(
            'defensor__servidor',
        ).vigentes(ajustar_horario=False).filter(
            defensor__eh_defensor=True,
            defensoria=manifestacao.defensoria,
            defensoria__pode_vincular_processo_judicial=True
        )

        # Se usuário logado é um defensor, mostra apenas atuações dele
        if self.request.user.servidor.defensor.eh_defensor:
            atuacoes_para_analise = atuacoes_para_analise.filter(
                defensor=self.request.user.servidor.defensor
            )
            atuacoes_para_protocolo = atuacoes_para_protocolo.filter(
                defensor=self.request.user.servidor.defensor
            )

        if parte and not parte.processo.pre_cadastro:

            # Consulta dados do processo no ProcAPI
            processo = APIProcesso(parte.processo.numero_procapi, self.request)
            sucesso, resposta = processo.consultar()

            # Guarda dados consultados na parte
            parte.procapi = resposta

            avisos = []
            # Parametros gerais de consulta
            params = {
                'processo_numero': parte.processo.numero_puro,
                'sistema_webservice': manifestacao.sistema_webservice,
                'ativo': True,
            }

            # Consulta no ProcAPI a lista de avisos vinculados ao processo e defensor
            if config.VINCULAR_NA_DISTRIBUICAO_AVISO_A_DEFENSOR_AUTOMATICAMENTE:
                # Só deve filtrar caso não esteja superusuário ou defensoria de plantão
                if not self.request.user.is_superuser and not defensorias.filter(nucleo__plantao=True).exists():
                    cpfs_defensores = set(atuacoes_para_analise.values_list('defensor__servidor__cpf', flat=True))
                    params['distribuido_cpf'] = ','.join(cpfs_defensores)
                    params['distribuido_defensoria'] = None

                avisos = APIAviso().listar_todos(params=params)

            # Consulta no ProcAPI a lista de avisos vinculados ao processo e defensoria
            if config.VINCULAR_NA_DISTRIBUICAO_AVISO_A_DEFENSORIA_AUTOMATICAMENTE:
                # Só deve filtrar caso não esteja superusuário ou defensoria de plantão
                if not self.request.user.is_superuser and not defensorias.filter(nucleo__plantao=True).exists():
                    ids_defensorias = map(str, set(atuacoes_para_analise.values_list('defensoria_id', flat=True)))
                    params['distribuido_defensoria'] = ','.join(ids_defensorias)
                    if config.AVISOS_FILTER_DISTRIBUIDO_OPERADOR_LOGICO == 'OR':
                        cpfs_defensores = set(atuacoes_para_analise.values_list('defensor__servidor__cpf', flat=True))
                        params['distribuido_cpf'] = ','.join(cpfs_defensores)
                        params['distribuido_operador_logico'] = 'OR'
                    else:
                        params['distribuido_cpf'] = None

                avisos += APIAviso().listar_todos(params=params)

            # Verifica quais prazos podem ser exibidos na manifestação
            for posicao, aviso in enumerate(avisos):

                aviso['selecionado'] = False

                # Lista de números relacionados ao mesmo aviso
                numeros_aviso = [aviso['numero'], aviso['aviso_original']]

                # Remove ocorrências em duplicidade do mesmo aviso por conta das duas consultas
                for aviso_anterior in avisos[:posicao]:
                    if aviso_anterior['numero'] == aviso['numero']:
                        aviso['esta_fechado'] = True

                if not aviso['esta_fechado'] or manifestacao.situacao == Manifestacao.SITUACAO_PROTOCOLADO:
                    # Verifica se prazo está vinculado à manifestação
                    aviso['selecionado'] = manifestacao.avisos.ativos().filter(numero__in=numeros_aviso).exists()
                # Verifica se prazo está vinculado à outra manifestação
                if not aviso['esta_fechado'] and not aviso['selecionado']:
                    aviso['esta_fechado'] = ManifestacaoAviso.objects.ativos().filter(
                        Q(numero__in=numeros_aviso) &
                        (
                            ~Q(manifestacao__situacao=Manifestacao.SITUACAO_ERRO) &
                            Q(manifestacao__desativado_em=None) &
                            Q(manifestacao__sistema_webservice=manifestacao.sistema_webservice)
                        )
                    ).exists()
                # Se está selecionado ou não está encerrado, adiciona à lista de prazos disponíveis
                if aviso['selecionado'] or not aviso['esta_fechado']:
                    prazos.append(aviso)

        # Consulta no ProcAPI a lista de tipos de documento válidos para sistema onde está o processo
        api = APITipoDocumento()
        tipos_documento = api.listar_todos(params={
            'sistema_webservice': manifestacao.sistema_webservice,
            'disponivel_em_peticao': True,
        })

        # Identifica tipo de documento pelo nome ou título normalizados
        for index, documento in enumerate(documentos):
            if not documento.tipo_mni:
                # Vincula primeiro documento de novo processo como petição inicial
                if index == 0 and manifestacao.tipo == Manifestacao.TIPO_PETICAO_INICIAL:
                    for tipo_documento in tipos_documento:
                        if tipo_documento['nome_norm'] == 'PETICAO INICIAL':
                            documento.tipo_mni = tipo_documento['codigo']
                            break
                else:
                    for tipo_documento in tipos_documento:
                        if tipo_documento['nome_norm'] == documento.get_origem.nome_norm:
                            documento.tipo_mni = tipo_documento['codigo']
                            break
                        elif hasattr(documento.get_origem, 'documento') and documento.get_origem.documento and tipo_documento['nome_norm'] == documento.get_origem.documento.nome_norm:  # noqa: E501
                            documento.tipo_mni = tipo_documento['codigo']
                            break
                        elif hasattr(documento.get_origem, 'documento_online') and documento.get_origem.documento_online and tipo_documento['nome_norm'] == Util.normalize(documento.get_origem.documento_online.tipo_documento.titulo):  # noqa: E501
                            documento.tipo_mni = tipo_documento['codigo']
                            break

        # Se protocolado, obtém dados da manifestação no ProcAPI
        if manifestacao.situacao == Manifestacao.SITUACAO_PROTOCOLADO:

            servico = APIManifestacao(numero=None, sistema_webservice=manifestacao.sistema_webservice)
            sucesso, resposta = servico.consultar(pk=manifestacao.codigo_procapi)

            # Obtém conteúdo do recibo da manifestação no ProcAPI
            if sucesso and len(resposta['recibos']):
                recibo = resposta['recibos'][0]['conteudo']
                if recibo is not None:
                    recibo = recibo.encode('latin1')
                    recibo = base64.b64encode(recibo)
                    recibo = recibo.decode('ascii')

        api_sistema = APISistema().get(manifestacao.sistema_webservice)

        if api_sistema.get('deve_enviar_manifestante'):
            # identifica credenciais de acesso do usuário no sistema_webservice
            api = APIManifestante()
            credenciais = api.listar_todos(params={
                'sistema_webservice': manifestacao.sistema_webservice,
                'cpf': self.request.user.servidor.cpf
            })

        # Se petição inicial, verifica quais pessoas estão sem documento obrigatório
        if manifestacao.tipo == Manifestacao.TIPO_PETICAO_INICIAL:

            selecionar_todas_pessoas = not manifestacao.partes.ativos().filter(parte__ativo=True).exists()

            possui_autor = False
            possui_reu = False

            for pessoa_atendimento in atendimento.todas_pessoas:

                # Seleciona pessoas do atendimento que também estão vinculadas à manifestação
                pessoa_atendimento.selecionado = (
                    pessoa_atendimento.ativo and (
                        selecionar_todas_pessoas or
                        manifestacao.id is None
                    ) or
                    manifestacao.partes.ativos().filter(parte=pessoa_atendimento.id).exists()
                )

                if pessoa_atendimento.ativo or pessoa_atendimento.selecionado:

                    endereco = pessoa_atendimento.pessoa.enderecos.principais().filter(desativado_em=None).first()

                    # Verifica se possue pelo menos um requerente (autor) e um requerido (réu)
                    if pessoa_atendimento.tipo == PessoaAtendimento.TIPO_REQUERENTE:
                        possui_autor = True

                        # Verifica se o sistema exige preenchimento de endereço
                        if api_sistema.get('parte_autora_exige_endereco_peticao_inicial'):
                            # Verifica se autor possui endereço devidamente preenchido
                            if (endereco and endereco.esta_completo):  # noqa: E501
                                requerente_tem_endereco.append(True)
                            else:
                                requerente_tem_endereco.append(False)

                    elif pessoa_atendimento.tipo == PessoaAtendimento.TIPO_REQUERIDO:
                        possui_reu = True

                        # Requerido tem uma lógica diferente # noqa: E501
                        # Se possui endereço cadastrado no SOLAR, então valida # noqa: E501
                        # Visto que, é bem comum o reú ter endereço desconhecido # noqa: E501
                        # Logo nos sistemas dos tribunais é um campo opcional para esta parte # noqa: E501
                        # No caso do sistema PJe (pode ser que outro sistema tenha a mesma lógica), não é possivel enviar endereço parcial, ou manda tudo completo, ou não manda informação # noqa: E501
                        if (endereco and api_sistema.get('parte_re_exige_endereco_peticao_inicial')):
                            if endereco.esta_completo:
                                requerido_tem_endereco.append(True)
                            else:
                                requerido_tem_endereco.append(False)

                    # Em Pessoa Jurídica o CNPJ sempre é obrigatório
                    if pessoa_atendimento.pessoa.tipo == constantes.TIPO_PESSOA_JURIDICA and not pessoa_atendimento.pessoa.cpf:  # noqa: E501
                        pessoa_atendimento.sem_documento = True
                        pessoas_sem_documento = True
                    # Em Pessoa Física um documento é obrigatório apenas quando é requerente
                    elif pessoa_atendimento.tipo == PessoaAtendimento.TIPO_REQUERENTE and not pessoa_atendimento.pessoa.possui_documentos:  # noqa: E501
                        pessoa_atendimento.sem_documento = True
                        pessoas_sem_documento = True

                    pessoas.append(pessoa_atendimento)

            # Considera apenas manifestações para criar novos processos
            outras_manifestacoes = outras_manifestacoes.filter(
                parte__atendimento=atendimento,
                parte__processo__pre_cadastro=True
            )

        else:

            # Considera apenas manifestações para mesmo processo
            outras_manifestacoes = outras_manifestacoes.filter(
                parte=parte
            )

        context = super(IndexView, self).get_context_data(**kwargs)

        # Valores iniciais para o carregamento do formulário
        form_initial = {}

        # Se processo já cadastrado, recupera lista de assuntos relacionados ao processo
        if parte and parte.processo:

            assuntos = parte.processo.processoassunto_set.all().values_list('assunto__codigo_cnj', flat=True)
            outros_parametros = parte.processo.outros_parametros.all().values_list('id', flat=True)

            form_initial['competencia'] = parte.processo.competencia_mni
            form_initial['assunto_principal'] = assuntos[0] if len(assuntos) else None  # noqa: E501
            form_initial['assuntos_secundarios'] = assuntos[1:]
            form_initial['outros_parametros_form'] = outros_parametros
            form_initial['tipo_fase'] = manifestacao.fase.tipo_id if manifestacao.fase else None
            form_initial['acao'] = parte.processo.acao.codigo_cnj if hasattr(parte.processo.acao, 'codigo_cnj') else None  # noqa: E501

        else:

            form_initial['comarca'] = atendimento.defensoria.comarca

            # Se atendimento possui qualificação, carrega informações sugeridas
            if atendimento.qualificacao:

                # Competência sugerida
                competencia_sugerida = atendimento.qualificacao.area.competencia_set.filter(
                    sistema_webservice__nome=manifestacao.sistema_webservice
                ).first()

                if competencia_sugerida and hasattr(competencia_sugerida, 'codigo_mni'):
                    form_initial['competencia'] = competencia_sugerida.codigo_mni

                # Classe sugerida
                classe_sugerida = atendimento.qualificacao.acao

                if classe_sugerida and hasattr(classe_sugerida, 'codigo_cnj'):
                    form_initial['acao'] = classe_sugerida.codigo_cnj

                # Assuntos sugeridos
                assuntos_sugeridos = atendimento.qualificacao.qualificacaoassunto_set.ativos().values_list('assunto__codigo_cnj', flat=True)  # noqa: E501

                if assuntos_sugeridos:
                    form_initial['assunto_principal'] = assuntos_sugeridos[0] if len(assuntos_sugeridos) else None,
                    form_initial['assuntos_secundarios'] = assuntos_sugeridos[1:] if len(assuntos_sugeridos) else None

        # Pode editar se situação análise ou erro
        pode_editar = manifestacao.situacao in [Manifestacao.SITUACAO_ANALISE, Manifestacao.SITUACAO_ERRO]

        # Pode peticionar se pode editar e documentos estão ok
        pode_peticionar = (
            pode_editar and
            possui_autor and
            not pessoas_sem_documento and
            False not in requerente_tem_endereco and
            False not in requerido_tem_endereco and
            (
                not documentos_para_assinatura or
                api_sistema.get('deve_enviar_manifestante') or
                (
                    api_sistema.get('metodo_assinatura_documentos') == APISistema.METODO_ASSINATURA_POR_CERTIFICADO_A1 and
                    self.request.user.servidor.defensor.eh_defensor
                )
            )
        )

        # Atualiza variáveis de contexto (visíveis no template)
        context.update({
            'parte': parte,
            'processo': parte.processo if parte else None,
            'atendimento': atendimento,
            'atendimento_para_upload': atendimento,
            'possui_autor': possui_autor,
            'possui_reu': possui_reu,
            'requerente_tem_endereco': False not in requerente_tem_endereco,
            'requerido_tem_endereco': False not in requerido_tem_endereco,
            'pessoas': pessoas,
            'pessoas_sem_documento': pessoas_sem_documento,
            'atuacoes_para_analise': atuacoes_para_analise,
            'atuacoes_para_protocolo': atuacoes_para_protocolo,
            'outras_manifestacoes': outras_manifestacoes,
            'credenciais': credenciais[0] if (api_sistema.get('deve_enviar_manifestante') and len(credenciais)) else None,  # noqa: E501
            'documentos': documentos,
            'documentos_para_assinatura': documentos_para_assinatura,
            'prazos': prazos,
            'recibo': recibo,
            'tipos_documento': tipos_documento,
            'lista_sigilo': Processo.LISTA_SIGILO[:3],
            'manifestacao': manifestacao,
            'Manifestacao': Manifestacao,
            'ManifestacaoDocumento': ManifestacaoDocumento,
            'PessoaAtendimento': PessoaAtendimento,
            'form': ProcessoPeticionamentoForm(
                atendimento=atendimento,
                editavel=pode_editar,
                sistema_webservice=manifestacao.sistema_webservice,
                instance=parte.processo if parte else None,
                initial=form_initial
            ),
            'PROCAPI_URL': settings.PROCAPI_URL,
            'PROCESSO_CALCULADORA_CALCULO_URL': config.PROCESSO_CALCULADORA_CALCULO_URL,
            'URL_PROCESSO_TJ': config.URL_PROCESSO_TJ,
            'NOME_PROCESSO_TJ': config.NOME_PROCESSO_TJ,
            'erro_validar_credenciais': self.request.session.pop('erro_validar_credenciais', False),
            'deve_enviar_manifestante': api_sistema.get('deve_enviar_manifestante'),
            'metodo_assinatura_documentos': api_sistema.get('metodo_assinatura_documentos'),
            'pode_editar': pode_editar,
            'pode_peticionar': pode_peticionar,
            'form_inicial': json.dumps({
                'sistema_webservice': manifestacao.sistema_webservice,
                'competencia': form_initial.get('competencia'),
                'assunto_principal': form_initial.get('assunto_principal'),
                'assuntos_secundarios': form_initial.get('assuntos_secundarios'),
                'acao': form_initial.get('acao'),
                'possui_reu': possui_reu,
                'pode_editar': pode_editar,
                'pode_filtrar_classe_assunto_competencia': api_sistema.get('pode_filtrar_classe_assunto_competencia'),
            }) if form_initial else json.dumps({}),
            'angular': 'PeticionamentoCtrl',
            'endereco_form': EnderecoForm(initial={
                'estado': Estado.objects.get(uf__iexact=settings.SIGLA_UF)
            }),
            'endereco_form_initial': {
                'estado': Estado.objects.get(uf__iexact=settings.SIGLA_UF)
            }
        })

        return context

    def post(self, request, *args, **kwargs):

        # Obtém dados da requisição
        dados = request.POST

        manifestacao = super(IndexView, self).post(request, *args, **kwargs)

        # Obtém dados do servidor selecionado (manifestante)
        manifestante = self.request.user.servidor
        # Obtém dados do defensor selecionado
        defensor = User.objects.get(id=dados.get('defensor_usuario_id'))

        # Inicia serviço de manifestante ProcAPI
        servico = APIManifestante()
        sucesso = True

        # Obtém informações do sistema a partir do ProcAPI
        try:
            sistema = APISistema().get(manifestacao.sistema_webservice)
            deve_enviar_manifestante = sistema.get('deve_enviar_manifestante')
            deve_enviar_documento_assinado = sistema.get('metodo_assinatura_documentos') == APISistema.METODO_ASSINATURA_POR_TOKEN  # noqa: E501
        except AttributeError:
            messages.error(self.request, "O Peticionamento está indisponível no momento.")

        # Cria/Atualiza credenciais do manifestante no ProcAPI
        if deve_enviar_manifestante:

            numero_processo = None

            if not manifestacao.parte.processo.pre_cadastro:
                numero_processo = manifestacao.parte.processo.numero_puro

            if not defensor.servidor.defensor.credenciais_expiradas():

                # Verifica se manifestante existe e é válido
                resposta = servico.listar_todos(params={
                    'sistema_webservice': manifestacao.sistema_webservice,
                    'cpf': defensor.servidor.cpf
                })

                if len(resposta) > 0 and resposta[0]['ativo']:
                    manifestacao.usuario_webservice = resposta[0]['usuario']
                else:
                    # Se manifestante não é válido, antecipa data de expiração das credenciais e força nova solicitação
                    defensor.servidor.defensor.data_expiracao_credenciais_mni = datetime.now()
                    defensor.servidor.defensor.save()
                    sucesso = False

            else:

                # Valida credenciais informadas pelo manifestante
                sucesso, resposta = servico.validar_credenciais(
                    sistema_webservice=manifestacao.sistema_webservice,
                    usuario=dados.get('usuario'),
                    senha=dados.get('senha'),
                    cpf=defensor.servidor.cpf,
                    processo=numero_processo
                )

                if sucesso:

                    # Armazena usário que será usado no peticionamento
                    manifestacao.usuario_webservice = dados.get('usuario')

                    # Se solicitado, salva credenciais por 30 dias
                    if dados.get('salvar_credenciais'):
                        defensor.servidor.defensor.data_expiracao_credenciais_mni = datetime.now() + timedelta(days=30)
                        defensor.servidor.defensor.save()

            # Se crendenciais são válidas, armazena usuário e assina geds não assinados
            if sucesso:

                try:
                    self._assinar_documentos_ged_manifestacao_automaticamente(manifestacao, manifestante)
                except Exception as e:
                    messages.error(self.request, str(e))
                    sucesso = False

            else:

                request.session['erro_validar_credenciais'] = True
                messages.error(request, resposta)

        elif (sistema.get('metodo_assinatura_documentos') == APISistema.METODO_ASSINATURA_POR_CERTIFICADO_A1 and
              self.request.user.servidor.defensor.eh_defensor):

            try:
                self._assinar_documentos_ged_manifestacao_automaticamente(manifestacao, manifestante)
            except Exception as e:
                messages.error(self.request, str(e))
                sucesso = False

        # Se deve enviar documentos assinados, confirma se o assinador realmente assinou todos antes de enviar para fila
        if deve_enviar_documento_assinado:
            for documento in manifestacao.documentos.ativos():
                if documento.get_origem.documento_assinado is None:
                    sucesso = False
                    messages.error(request, 'Falha na assinatura dos documentos! Por favor, reinicie o assinador e \
                                             tente novamente. Se o problema persistir, contate o suporte técnico.')
                    break

        # Se manifestação estiver desativada (excluída), impede o envio
        if manifestacao.desativado_em:
            sucesso = False
            messages.error(request, 'Essa manifestação foi excluída, impossível enviá-la.')

        if sucesso:

            # Registra defensor responsável pela manifestação
            manifestacao.defensor = defensor
            # Registra usuário responsável pela manifestação
            manifestacao.manifestante = manifestante.usuario
            # Registra usuário que enviou a manifestação
            manifestacao.enviado_por = self.request.user
            manifestacao.enviado_em = datetime.now()
            # Registra dados da resposta na manifestação
            manifestacao.enviando = True
            manifestacao.enviado = False
            manifestacao.situacao = Manifestacao.SITUACAO_NAFILA
            manifestacao.save()

            # Criar task para envio imediato da manifestação sem passar pela fila
            procapi_enviar_manifestacao.apply_async(kwargs={'id': manifestacao.id}, queue='manifestacao')

            messages.success(request, 'Edição concluída! A manifestação entrará na fila para protocolo.')

        return redirect('peticionamento:visualizar', pk=manifestacao.pk)

    def _assinar_documentos_ged_manifestacao_automaticamente(self, manifestacao, manifestante):

        for documento in manifestacao.documentos.ativos():

            # Se documento ainda não finalizado, força assinar e finalizar
            if hasattr(documento.get_origem, 'documento_online') and documento.get_origem.documento_online and not documento.get_origem.documento_online.esta_finalizado:  # noqa: E501

                documento_ged = documento.get_origem.documento_online

                # Verifica quantas assinaturas faltam
                assinaturas_pendentes = documento_ged.assinaturas.filter(
                    esta_assinado=False,
                    ativo=True
                ).count()

                if assinaturas_pendentes > 1:
                    raise NaoPodeAssinarException('Impossível assinar! Existe mais de uma assinatura pendente!')  # noqa: E501

                # Verifica se falta assinatura do dono do documento
                falta_assinatura_do_dono = documento_ged.assinaturas.filter(
                    grupo_assinante=documento_ged.grupo_dono,
                    esta_assinado=False,
                    ativo=True
                ).exists()

                # Verifica se a defensoria manifestante já assinou o documento
                possui_assinatura_do_manifestante = documento_ged.assinaturas.filter(
                    grupo_assinante=manifestacao.defensoria,
                    esta_assinado=True,
                    ativo=True
                ).exists()

                # Cancela se falta assinatura do dono mas manifestante já assinou
                if falta_assinatura_do_dono and possui_assinatura_do_manifestante:

                    raise NaoPodeAssinarException('Impossível assinar novamente! Solicite ao proprietário que efetue a assinatura!')  # noqa: E501

                elif falta_assinatura_do_dono:

                    # Se a defensoria dona do documento não é a mesma da manifestação, força alteração de propriedade
                    if documento_ged.grupo_dono_id != manifestacao.defensoria_id:

                        # Troca grupo assinante da assinatura
                        documento_ged.assinaturas.filter(
                            grupo_assinante=documento_ged.grupo_dono
                        ).update(
                            grupo_assinante=manifestacao.defensoria,
                            grupo_assinante_nome=manifestacao.defensoria.nome
                        )

                        # Troca grupo dono do documento
                        documento_ged.grupo_dono = manifestacao.defensoria
                        documento_ged.save()

                    # Assina com as credenciais do manifestante
                    documento_ged.assinar(
                        grupo_assinante=documento_ged.grupo_dono,
                        usuario_assinante=manifestante.usuario,
                        senha=manifestante.usuario.password,
                        check_password=False
                    )

                # Finaliza com as credenciais do manifestante
                DocumentoFinalizarMixin().finalizar_documento(
                    request=self.request,
                    documento=documento_ged,
                    finalizado_por=manifestante.usuario,
                    notificar=False
                )


class BuscarListView(ListView):
    model = models.Manifestacao
    queryset = models.Manifestacao.objects.annotate(
        erro_no_protocolo=Case(When(situacao=Manifestacao.SITUACAO_ERRO, then=Value(True)), default=Value(False),
                               output_field=BooleanField()),
    ).select_related(
        'defensoria',
        'parte__atendimento',
        'parte__processo__acao',
        'parte__processo__area',
        'parte__processo__comarca',
        'parte__processo__vara',
    ).ativos().order_by(
        '-erro_no_protocolo',
        'situacao',
        '-respondido_em',
        'enviado_em',
        'cadastrado_em'
    )
    paginate_by = 50
    template_name = "processo/peticionamento/buscar.html"

    def get_context_data(self, **kwargs):

        context = super(BuscarListView, self).get_context_data(**kwargs)
        situacao = self.request.GET.get('situacao')

        # Obtém total de registros relacionados às lotações do usuário agrupados por situação
        queryset = self.queryset.filter(
            self.get_filter_defensorias()
        ).order_by(
            'situacao'
        ).values(
            'situacao'
        ).annotate(
            total=Count('id')
        )

        # Transforma resultado em formato compatível com painel de totais
        totais = {}
        for total in queryset:
            totais[total['situacao']] = total['total']

        # Dados do painel de totais
        dados_painel_totais = [
            {
                'texto': 'Erro no protocolo',
                'valor': totais.get(Manifestacao.SITUACAO_ERRO, 0),
                'icone': 'fas fa-times-circle',
                'cor': 'bg-red',
                'url': '{}?situacao={}'.format(reverse('peticionamento:buscar'), Manifestacao.SITUACAO_ERRO),
                'selecionado': situacao == str(Manifestacao.SITUACAO_ERRO),
            },
            {
                'texto': 'Aguardando análise',
                'valor': totais.get(Manifestacao.SITUACAO_ANALISE, 0),
                'icone': 'fas fa-exclamation-circle',
                'cor': 'bg-yellow',
                'url': '{}?situacao={}'.format(reverse('peticionamento:buscar'), Manifestacao.SITUACAO_ANALISE),
                'selecionado': situacao == str(Manifestacao.SITUACAO_ANALISE),
            },
            {
                'texto': 'Na fila para protocolo',
                'valor': totais.get(Manifestacao.SITUACAO_NAFILA, 0),
                'icone': 'fas fa-clock',
                'cor': 'bg-blue',
                'url': '{}?situacao={}'.format(reverse('peticionamento:buscar'), Manifestacao.SITUACAO_NAFILA),
                'selecionado': situacao == str(Manifestacao.SITUACAO_NAFILA),
            },
            {
                'texto': 'Protocoladas',
                'valor': totais.get(Manifestacao.SITUACAO_PROTOCOLADO, 0),
                'icone': 'fas fa-check-circle',
                'cor': 'bg-green',
                'url': '{}?situacao={}'.format(reverse('peticionamento:buscar'), Manifestacao.SITUACAO_PROTOCOLADO),
                'selecionado': situacao == str(Manifestacao.SITUACAO_PROTOCOLADO),
            },
        ]

        context.update({
            'totais': dados_painel_totais,
            'form': BuscarManifestacaoForm(self.request.GET, usuario=self.request.user),
            'Manifestacao': models.Manifestacao,
        })

        return context

    def get_filter_defensorias(self):

        q = Q()

        # Obtém lista de defensorias das atuações vigentes do usuário
        defensorias = set(
            self.request.user.servidor.defensor.atuacoes_vigentes().values_list('defensoria_id', flat=True)
        )

        # Se usuário não tem permissão para ver todos atendimentos, restringe informações de acordo com suas lotações
        if not self.request.user.has_perm(perm='atendimento.view_all_atendimentos'):
            q &= Q(defensoria__in=defensorias)

        return q

    def get_queryset(self):

        queryset = super(BuscarListView, self).get_queryset()
        q = self.get_filter_defensorias()

        form = BuscarManifestacaoForm(self.request.GET, usuario=self.request.user)

        # Só filtra se valores de busca forem válidos
        if form.is_valid():

            data = form.cleaned_data

            # Filtro por prazo maior ou igual a data inicial
            if data.get('data_inicial'):
                q &= Q(cadastrado_em__gte=data.get('data_inicial'))

            # Filtro por prazo menor ou igual a data final
            if data.get('data_final'):
                q &= Q(cadastrado_em__lte=datetime.combine(data.get('data_final'), time.max))

            # Filtro por setor responsável (defensoria)
            if data.get('setor_responsavel'):
                q &= Q(defensoria=data.get('setor_responsavel'))

            # Filtro por servidor responsável
            if config.VINCULAR_NA_DISTRIBUICAO_AVISO_A_DEFENSOR_AUTOMATICAMENTE:
                if data.get('responsavel'):
                    q &= Q(cadastrado_por__servidor__defensor=data.get('responsavel'))
            else:
                if data.get('responsavel'):
                    q &= Q(
                        Q(cadastrado_por__servidor__defensor=data.get('responsavel')) |
                        Q(cadastrado_por__servidor__defensor__supervisor=data.get('responsavel')) |
                        Q(defensor=data.get('responsavel').servidor.usuario)
                    )

            # Filtro por situação
            if data.get('situacao') is not None:
                q &= Q(situacao=data.get('situacao'))

        return queryset.filter(q)


class DocumentoDeleteView(SoftDeleteView):
    model = ManifestacaoDocumento


class ManifestacaoDeleteView(SoftDeleteView):
    model = Manifestacao


class PeticionarEmMassaView(View):
    '''
    Protocola manifestações selecionadas em massa
    '''

    def post(self, request, *args, **kwargs):

        ids_manifestacoes = request.POST.getlist('sel')
        total = (len(ids_manifestacoes))

        for id in ids_manifestacoes:
            self.reenviar(id)

        if total == 0:
            messages.error(request, 'Nenhuma manifestação foi selecionada!')
        else:
            messages.success(request, '{} manifestações foram reenviadas para a fila de protocolo!'.format(total))

        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', '/'))

    def reenviar(self, manifestacao_id):

        manifestacao = Manifestacao.objects.get(id=manifestacao_id)

        if manifestacao.situacao == Manifestacao.SITUACAO_ERRO:

            manifestacao.situacao = Manifestacao.SITUACAO_NAFILA
            manifestacao.enviando = False
            manifestacao.enviado = False
            manifestacao.save()

            procapi_enviar_manifestacao.apply_async(kwargs={'id': manifestacao.id}, queue='manifestacao')

        elif manifestacao.envio_expirado:

            if manifestacao.codigo_procapi:
                procapi_atualizar_manifestacao.apply_async(kwargs={
                    'id': manifestacao.id,
                    'forcar_protocolo': True
                }, queue='manifestacao')
            else:
                procapi_enviar_manifestacao.apply_async(kwargs={
                    'id': manifestacao.id
                }, queue='manifestacao')
