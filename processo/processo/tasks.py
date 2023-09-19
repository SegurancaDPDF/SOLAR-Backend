# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import base64
# Biblioteca Padrao
import logging
import time
from datetime import datetime, timedelta

from django.core.cache import cache
from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.db.models.functions import Length

# Bibliotecas de terceiros
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from constance import config
from djdocuments.models import Documento as DocumentoGED

from assistido.exceptions import DadosPessoaInsuficientesException
from assistido.models import Documento as DocumentoOriginalAssistido
from assistido.models import DocumentoAssinado as DocumentoAssinadoAssistido
from atendimento.atendimento.models import \
    Documento as DocumentoOriginalAtendimento
from atendimento.atendimento.models import \
    DocumentoAssinado as DocumentoAssinadoAtendimento
from contrib.models import Comarca, DefensoriaVara, Util
from contrib.services import (
    ConvertToMP4Service,
    ConvertToWEBMService,
    GedToPDFService
)
from defensor.models import Atuacao, Defensor
# Signo
from notificacoes.tasks import notificar_manifestacao_protocolada
from procapi_client.exceptions import (
    ExceptionBase,
    ManifestacaoServiceUnavailable,
    PJEAvisoJaFechadoException,
    PROCAPIConsultaTeorComunicacaoError
)
from procapi_client.models import (
    Competencia,
    HistoricoConsultaAvisos,
    HistoricoConsultaProcessos,
    OrgaoJulgador,
    SistemaWebService
)
from procapi_client.services import (
    APIAssunto,
    APIAviso,
    APIClasse,
    APICompetencia,
    APIComunicacao,
    APIListaProcessos,
    APIManifestacao,
    APIProcesso,
    APIProcessoParte,
    APISistema
)
from processo.honorarios.models import Honorario
from processo.peticionamento.tasks import enviar_email_confirmacao_protocolo
from thothsigner_client.exceptions import (
    ThothsignerFailed,
    ThothsignerUnavailable
)
from thothsigner_client.services import Assinador

from .exceptions import DocumentOriginNotFound
# Solar
from .models import (
    Acao,
    Assunto,
    Aviso,
    Fase,
    Manifestacao,
    ManifestacaoDocumento,
    Parte,
    Processo
)
from .services import (
    AvisoService,
    FaseService,
    ProcessoEventoService,
    ProcessoService,
    salvar_processo
)

__author__ = 'amx-dev'
logger = logging.getLogger(__name__)


@shared_task
def procapi_atualizar_processos(limite: int = 100, repetida_a_cada: int = 50.0, qnt_workers: int = 2):

    # Consulta base de processos desatualizados
    processos = Processo.objects.annotate(
        numero_len=Length('numero_puro')
    ).filter(
        tipo=Processo.TIPO_EPROC,
        numero_len=20,
        atualizado=False,
        ativo=True
    ).order_by(
        'modificado_em'
    )

    # Verifica quantos processos ainda estão na fila para atualizar
    total_na_fila = processos.filter(
        atualizando=True
    ).count()

    novo_limite = int(limite) - total_na_fila

    if novo_limite <= 0:
        return '{} processos já estão na fila, excedendo o limite: {}'.format(total_na_fila, limite)

    # Obtém lista dos processos desatualizados mais antigos
    processos = processos.filter(
        atualizando=False
    ).order_by(
        'ultima_modificacao'
    ).values(
        'numero_puro',
        'grau'
    )[:novo_limite]

    lancar_nova_task_a_cada = None

    try:
        lancar_nova_task_a_cada = float(repetida_a_cada) * qnt_workers / float(novo_limite)
    except:  # noqa
        logger.log(
            level=logging.CRITICAL,
            msg='erro ao converter para float',
            extra={'params': {
                'limite': limite,
                'novo_limite': novo_limite,
                'repetida_a_cada': repetida_a_cada,
                'qnt_workers': qnt_workers}
            }
        )

    contador = 0
    t_inicio = datetime.now()

    for processo in processos:

        # marca o processo como atualizando
        Processo.objects.filter(
            numero_puro=processo['numero_puro'],
            grau=processo['grau']
        ).update(
            atualizando=True
        )

        # inicia nova task para efetivamente atualizar o processo.
        procapi_atualizar_processo.apply_async(kwargs={
            'numero': processo['numero_puro'],
            'grau': processo['grau']
        }, queue='default')

        if lancar_nova_task_a_cada and contador == qnt_workers:
            time.sleep(lancar_nova_task_a_cada)
            contador = 0

        contador += 1

    t_final = datetime.now()

    if lancar_nova_task_a_cada:
        t_total = t_final - t_inicio
        msg = '{} proc. serão atualizados. {} a cada {:.2f}s durante {:.2f}s. t_inicio: {}, t_final: {}'.format(
            len(processos),
            qnt_workers,
            lancar_nova_task_a_cada,
            t_total.total_seconds(),
            datetime.strftime(t_inicio, "%Y-%m-%d %H:%M:%S.%f"),
            datetime.strftime(t_final, "%Y-%m-%d %H:%M:%S.%f")
        )
    else:
        msg = '{} processos serão atualizados'.format(len(processos))
    return msg


@shared_task
def procapi_verificar_processos(minutos: int = None):

    MINIMO_MINUTOS = 10
    agora = datetime.now()
    data_final = datetime(agora.year, agora.month, agora.day, agora.hour, agora.minute)
    data_inicial = data_final - timedelta(minutes=MINIMO_MINUTOS)

    if minutos:

        data_inicial = data_final - timedelta(minutes=minutos)

    else:

        ultima_consulta = HistoricoConsultaProcessos.objects.filter(
            sucesso=True,
            registros__gt=0
        ).order_by(
            '-data_final'
        ).first()

        if ultima_consulta and ultima_consulta.data_final:

            tentativas = HistoricoConsultaProcessos.objects.filter(
                Q(sucesso=True) &
                (
                    (Q(registros__gt=0) & Q(data_final=ultima_consulta.data_final)) |
                    (Q(registros=0) & Q(data_inicial=ultima_consulta.data_final))
                )
            ).count()

            data_inicial = ultima_consulta.data_final
            data_final = data_inicial + timedelta(minutes=tentativas * MINIMO_MINUTOS)

            if data_final > agora:
                return {
                    'sucesso': False,
                    'resposta': 'A data/hora {} não pode ser superior à atual'.format(data_final)
                }

    return procapi_verificar_processos_periodo(
        data_inicial=data_inicial,
        data_final=data_final
    )


@shared_task
def procapi_verificar_processos_periodo(data_inicial, data_final):

    if not isinstance(data_inicial, datetime) and not isinstance(data_final, datetime):
        data_inicial = datetime.strptime(data_inicial, "%Y-%m-%d %H:%M:%S")
        data_final = datetime.strptime(data_final, "%Y-%m-%d %H:%M:%S")

    api = APIListaProcessos()

    pagina = 0
    processos = 0
    continuar = True
    sucesso = False
    data_ultima_atualizacao = None
    inicio_consulta = datetime.now()

    while continuar:

        pagina = pagina + 1

        sucesso, resposta = api.listar(
            pagina=pagina,
            data_inicial=data_inicial,
            data_final=data_final
        )

        if sucesso:

            processos = resposta['count']

            for processo in resposta['results']:

                # recupera data do ultimo processo atualizado
                if not data_ultima_atualizacao and processo['data_ultima_atualizacao']:
                    if len(processo['data_ultima_atualizacao']) == 19:
                        data_ultima_atualizacao = datetime.strptime(processo['data_ultima_atualizacao'], '%Y-%m-%dT%H:%M:%S')  # noqa: E501
                    else:
                        data_ultima_atualizacao = datetime.strptime(processo['data_ultima_atualizacao'], '%Y-%m-%dT%H:%M:%S.%f')  # noqa: E501

                processo, novo = Processo.objects.update_or_create(
                    numero_puro=processo['numero'],
                    grau=processo['grau'],
                    defaults={
                        'numero': Processo.formatar_numero(processo['numero']),
                        'tipo': Processo.TIPO_EPROC,
                        'ultima_modificacao': datetime.now(),
                        'atualizando': False,
                        'atualizado': False
                    }
                )

                if novo or not processo.ativo:
                    processo.pre_cadastro = True
                    processo.save()

            continuar = continuar if resposta['next'] else False

        else:

            continuar = False

    # guarda no histórico a data do último processo atualizado, se houver
    if data_ultima_atualizacao and data_ultima_atualizacao < data_final:
        data_final = datetime(
            data_ultima_atualizacao.year,
            data_ultima_atualizacao.month,
            data_ultima_atualizacao.day,
            data_ultima_atualizacao.hour,
            data_ultima_atualizacao.minute)

    HistoricoConsultaProcessos.objects.create(
        inicio_consulta=inicio_consulta,
        termino_consulta=datetime.now(),
        data_inicial=data_inicial,
        data_final=data_final,
        paginas=pagina,
        registros=processos,
        sucesso=sucesso
    )

    return {
        'sucesso': sucesso,
        'resposta': None if sucesso else resposta,
        'paginas': pagina,
        'registros': processos,
    }


@shared_task(bind=True, retry_backoff=True)
@transaction.atomic
def procapi_atualizar_processo(self, numero, grau, sistema_webservice=None):
    try:
        processo = Processo.objects.filter(numero_puro=numero, grau=grau, ativo=True).first()

        if processo:
            servico = ProcessoService(processo=processo)
            if config.PROCAPI_PERMITE_CADASTRAR_PROCESSO_SIGILOSO:
                servico.sistema_webservice = sistema_webservice
            servico.atualizar()

            return {
                'sucesso': servico.sucesso,
                'resposta': 'Processo atualizado' if servico.sucesso else servico.resposta
            }
        else:

            return {
                'sucesso': False,
                'resposta': 'Processo não encontrado'
            }

    except Exception:
        self.retry()


@shared_task
def procapi_atualizar_manifestacoes(limite: int = 100):

    manifetacoes = Manifestacao.objects.filter(
        enviado=True,
        situacao=Manifestacao.SITUACAO_NAFILA
    ).only(
        'id'
    )[:int(limite)]

    for manifestacao in manifetacoes:
        # inicia nova task para efetivamente atualizar a manifestação
        procapi_atualizar_manifestacao.apply_async(kwargs={
            'id': manifestacao.id
        }, queue='manifestacao')

    return '{} manifestações serão atualizadas'.format(len(manifetacoes))


@shared_task
def procapi_atualizar_manifestacao(id, forcar_protocolo=False):

    manifestacao = Manifestacao.objects.get(id=id)
    processo = manifestacao.parte.processo

    # Inicia serviço de manifestação processual
    servico = APIManifestacao(numero=processo.numero_procapi, sistema_webservice=manifestacao.sistema_webservice)

    _, resposta = servico.consultar(pk=manifestacao.codigo_procapi, params={'forcar_protocolo': forcar_protocolo})

    # Se manifestação foi enviada, atualiza registro com os dados da resposta
    if resposta['enviado']:

        manifestacao.situacao = Manifestacao.SITUACAO_PROTOCOLADO if resposta['sucesso'] else Manifestacao.SITUACAO_ERRO
        manifestacao.protocolo_resposta = resposta['protocolo']
        manifestacao.mensagem_resposta = resposta['mensagem']

        if resposta['data_operacao']:
            manifestacao.respondido_em = datetime.strptime(resposta['data_operacao'], '%Y-%m-%dT%H:%M:%S')

        manifestacao.save()

        if manifestacao.situacao == Manifestacao.SITUACAO_PROTOCOLADO:

            # Se petição inicial, atualiza dados do processo precadastrado:
            if processo.pre_cadastro:

                processo.numero = resposta['processo']['numero']
                processo.chave = resposta['processo']['chave']
                processo.grau = resposta['processo']['grau']
                processo.pre_cadastro = False
                processo.vara = None
                processo.save()

                # Cria a tarefa no celery atualizar dados do novo processo
                procapi_atualizar_processo.apply_async(kwargs={
                    'numero': processo.numero_inteiro,
                    'grau': processo.grau
                }, queue='sobdemanda')

            enviar_email_confirmacao_protocolo.apply_async(kwargs={
                'manifestacao_id': manifestacao.id
            }, queue='sobdemanda')

        else:

            # Se manifestante não é válido, antecipa data de expiração das credenciais e força nova solicitação
            if 'Nenhum consultante válido' in manifestacao.mensagem_resposta:
                manifestacao.defensor.servidor.defensor.data_expiracao_credenciais_mni = datetime.now()
                manifestacao.defensor.servidor.defensor.save()

        # Notifica usuário que enviou a manifestação
        if config.NOTIFICAR_MANIFESTACAO_PROTOCOLADA:
            notificar_manifestacao_protocolada.apply_async(kwargs={
                'manifestacao_id': manifestacao.id
            }, queue='sobdemanda')

        return 'Manifestação {} atualizada. Resultado: {}'.format(manifestacao.id, resposta['mensagem'])

    else:

        return 'Manifestação {} ainda não foi protocolada.'.format(manifestacao.id)


@shared_task
def procapi_enviar_manifestacoes(limite: int = 100):

    manifetacoes = Manifestacao.objects.filter(
        enviado=False,
        enviando=False,
        situacao=Manifestacao.SITUACAO_NAFILA,
    ).distinct(
        'parte'
    ).only(
        'id'
    )[:int(limite)]

    for manifestacao in manifetacoes:

        # marca a manifestação como enviando para evitar duplicidade de tasks
        manifestacao.enviando = True
        manifestacao.save()

        # inicia nova task para enviar documentos da manifestação
        procapi_enviar_manifestacao.apply_async(kwargs={
            'id': manifestacao.id
        }, queue='manifestacao')

    return '{} manifestações serão enviadas'.format(len(manifetacoes))


# max_retries é auto_incrementado caso acontecer erro de conexão
@shared_task(bind=True, retry_backoff=15, max_retries=3)
def procapi_enviar_manifestacao(self, **kwargs):

    id = kwargs.get('id')

    manifestacao = Manifestacao.objects.get(id=id)

    if manifestacao.enviado:
        return 'Manifestação {} já foi enviada por outra tarefa'.format(id)

    # Verifica se já existe manifestação na fila para parte, se sim postergar envio desta para os próximos três minutos
    # Recurso necessário porque o PJe dá erro quando tenta enviar 2 ou mais manifestações simultaneamente da mesma parte
    if Manifestacao.objects.ativos().filter(situacao=Manifestacao.SITUACAO_NAFILA, parte=manifestacao.parte).count() > 1:  # noqa: E501
        self.retry(countdown=180)

    # Recupera lista de prazos que serão fechados
    avisos = list(manifestacao.avisos.ativos().values_list('numero', flat=True))

    # Se processo pré-cadastrado, manifestação é uma petição inicial
    if manifestacao.parte.processo.pre_cadastro:

        # Cria processo no ProcAPI
        servico = APIProcesso(manifestacao.parte.processo.numero)

        # Força a exclusão do processo pré-cadastro no ProcAPI
        servico.excluir(pk=manifestacao.parte.processo.numero)

        # envia processo e manifestação em objetos para criar processo ProcAPI
        sucesso, resposta = servico.criar(manifestacao.parte.processo, manifestacao)

        if not sucesso:
            try:
                self.retry(countdown=120)
            except MaxRetriesExceededError():
                __retornar_erro_na_manifestacao(manifestacao, resposta)

        # Cria partes no ProcAPI
        for parte in manifestacao.partes.ativos():

            api = APIProcessoParte()
            sucesso, resposta = api.criar(manifestacao.parte.processo, parte.parte, manifestacao.defensor.servidor)

            if not sucesso:
                try:
                    self.retry(countdown=120)
                except MaxRetriesExceededError():
                    __retornar_erro_na_manifestacao(manifestacao, resposta)

            # Se houver representante, cria pessoa relacionada no ProcAPI
            if parte.parte.representante and parte.parte.representante_modalidade:
                sucesso, resposta = api.criar_pessoa_relacionada(manifestacao.parte.processo, parte.parte, resposta['id'])  # noqa: E501

    # Serviços do ProcAPI
    api_aviso = APIAviso()
    api_comunicacao = APIComunicacao()

    # TODO: Tratar erros na abertura dos prazos
    # Força abertura de todos os prazos vinculados
    for aviso in avisos:

        avisos_consultados = api_aviso.listar_todos({
            'numero': aviso,
            'processo_numero': manifestacao.parte.processo.numero_puro
        })

        aviso_consultado = avisos_consultados[0]

        # Se aviso já foi fechado por outros meios, desativa vínculo com a manifestação
        if aviso_consultado['esta_fechado']:
            manifestacao.avisos.get(numero=aviso).desativar(manifestacao.enviado_por)
        # Se aviso não está fechado e não tem comunicação, faz a abertura do prazo
        elif not aviso_consultado['esta_fechado'] and aviso_consultado['comunicacao'] is None:

            sucesso, resposta = api_comunicacao.criar(
                # O CPF deve ser enviado para identificar um consultante específico, caso o sistema onde está o aviso exigir  # noqa: E501
                consultante_cpf=manifestacao.defensor.servidor.cpf,
                processo=manifestacao.parte.processo.numero_puro,
                numero=aviso,
            )

            if not sucesso:

                # Se o prazo selecionado já estiver fechado no PJe então já aborta o peticionamento
                if "PJEAvisoJaFechadoException" in resposta:
                    manifestacao.avisos.get(numero=aviso).desativar(manifestacao.enviado_por)
                    mensagem_de_erro = 'Não é possível protocolar pois o aviso/prazo selecionado {} já encontra-se respondido/fechado no PJe, dúvidas favor verificar com o suporte técnico'.format(aviso)  # noqa: E501
                    __retornar_erro_na_manifestacao(
                        manifestacao=manifestacao,
                        mensagem=mensagem_de_erro
                    )
                    raise PJEAvisoJaFechadoException

                # Se for erro de conexão aumenta dinamicamente a quantidade de retrys do Celery e realiza uma nova tentativa de abertura  # noqa: E501
                # O PROCAPI retorna na mensagem algumas exceções personalizadas sendo:
                # ConnectionError = Algum problema na internet entre o PROCAPI e o Webservice (MNI)
                # RemoteDisconnected = Servidor do MNI não está recebendo requisições do Procapi.
                # HTTPError = Algum erro 500, 503, 404 etc.. está acontecendo no Webservice (MNI)
                for erro in ExceptionBase.ERROS_DE_CONEXAO:
                    if erro in resposta:
                        try:
                            self.retry(max_retries=self.max_retries + 1)
                        # Se passou da quantidade de tentativas, retorna erro ao usuário
                        except MaxRetriesExceededError:
                            mensagem_de_erro = 'Não foi possível responder o aviso/prazo: {}, por favor verifique com o suporte técnico'.format(aviso)  # noqa: E501
                            __retornar_erro_na_manifestacao(
                                manifestacao=manifestacao,
                                mensagem=mensagem_de_erro
                            )
                            raise PROCAPIConsultaTeorComunicacaoError('Não foi possível fazer consultaTeorComunicacao do aviso {}'.format(aviso))  # noqa: E501

    # Inicia serviço de manifestação processual
    try:
        servico = APIManifestacao(
            numero=manifestacao.parte.processo.numero_procapi,
            sistema_webservice=manifestacao.sistema_webservice
        )
    except ManifestacaoServiceUnavailable as e:
        try:
            self.retry(countdown=120)
        except MaxRetriesExceededError():
            # Se o erro for de conexão com procapi, retorna para fila de peticionameto.
            __retornar_erro_na_manifestacao(
                manifestacao=manifestacao,
                mensagem=e.message
            )

    # Força a exclusão da manifestação no ProcAPI
    if manifestacao.codigo_procapi:
        servico.identificador = manifestacao.codigo_procapi
        servico.excluir(pk=manifestacao.codigo_procapi)

    api_sistema = APISistema().get(manifestacao.sistema_webservice)

    # Adiciona dados do manifestante
    servico.add_manifestante(
        cpf=manifestacao.defensor.servidor.cpf,
        usuario=manifestacao.usuario_webservice
    )

    # Se manifestação possui fase processual vinculada, obtém o tipo de evento a partir do tipo da fase
    if manifestacao.fase:

        # Procura por tipo de evento correspondente ao sistema webservice
        tipo_evento = manifestacao.fase.tipo.tipos_de_evento.filter(
            Q(sistema_webservice__nome=manifestacao.sistema_webservice) &
            (
                Q(disponivel_em_peticao_avulsa=True) |
                Q(disponivel_em_peticao_com_aviso=True)
            )
        ).first()

        # TODO: Verificar se pode continuar mesmo sem encontrar correspondência
        # Se foi encontrada correspondência, adiciona codigo do tipo do evento
        if tipo_evento:
            servico.add_evento(
                tipo=tipo_evento.codigo_mni
            )
    # Adiciona dados do evento (depreciado)
    else:
        servico.add_evento(
            tipo=manifestacao.tipo_evento
        )

    # Adiciona dados dos avisos, a partir da lista atualizada (sem avisos desativados durante verificações)
    servico.avisos = list(manifestacao.avisos.ativos().values_list('numero', flat=True))

    try:

        # Adiciona dados dos documentos no serviço de manifestação
        for doc in manifestacao.documentos.ativos().order_by('posicao'):

            # Salva mimetype original para enviar ao PROCAPI
            mimetype = None
            # Obtém dados do documento de acordo com a origem (atendimento ou pessoa)
            documento = doc.get_origem
            ged = None

            if documento.arquivo:
                # TODO: Verificar motivo da importação no cabeçalho gerar erro (local variable 'mimetypes' referenced before assignment)  # noqa: E501
                import mimetypes
                try:
                    # Salva mimetype original do arquivo
                    mimetype, doc_encoding = mimetypes.guess_type(documento.arquivo.path, strict=True)
                # fallback Minio Storage
                except NotImplementedError:
                    # Salva mimetype original do arquivo
                    mimetype, doc_encoding = mimetypes.guess_type(documento.arquivo.name, strict=True)
            # Obs: Os vídeos já em MP4 são reconvertidos porque existem diferentes
            # codificações ISO possíveis, sendo que o PJe aceita apenas uma delas.
            if mimetype in ['video/mp4', 'video/quicktime', 'video/avi']:
                # Converte vídeo para WEBM (padrão aceito pelo SEEU)
                if manifestacao.sistema_webservice == 'SEEU-1G-BR':
                    _, mimetype, documento_com_arquivo_convertido = ConvertToWEBMService(
                        documento
                    ).export_and_replace(return_object=True)
                # Converte vídeos para MP4 (padrão aceito pelos demais webservices)
                else:
                    _, mimetype, documento_com_arquivo_convertido = ConvertToMP4Service(
                        documento
                    ).export_and_replace(return_object=True)

                # Atualiza referência em memoria da task
                documento = documento_com_arquivo_convertido

            # Verifica se tem ged vinculado
            if hasattr(documento, 'documento_online') and documento.documento_online:
                ged = documento.documento_online

            # Verifica no PROCAPI se o web_service do tribunal de justiça exige assinatura por token
            devo_enviar_documento_assinado = False

            if api_sistema.get('metodo_assinatura_documentos') == APISistema.METODO_ASSINATURA_POR_TOKEN:
                devo_enviar_documento_assinado = True

            # Assina o arquivo utilizando Thoth Signer
            if api_sistema.get('metodo_assinatura_documentos') == APISistema.METODO_ASSINATURA_POR_CERTIFICADO_A1:

                assinador = Assinador()
                devo_enviar_documento_assinado = True
                documento_assinado_base64 = None

                # Se o documento for GED, primeiro transforma em PDF em memoria para depois enviar ao assinador
                if hasattr(documento, 'documento_online') and documento.documento_online:

                    # GED sempre será PDF
                    mimetype = 'application/pdf'

                    documento_ged = DocumentoGED.objects.get(id=documento.documento_online_id)
                    servico_ged = GedToPDFService(documento_ged)
                    conteudo_ged_em_pdf = servico_ged.export()

                    documento_assinado_base64 = assinador.assinar(
                        documentobase64=base64.b64encode(conteudo_ged_em_pdf).decode('ascii')
                    )

                # Se for arquivo bruto lê em memoria para depois enviar ao assinador
                elif documento.arquivo:

                    # TODO: Verificar motivo da importação no cabeçalho gerar erro (local variable 'mimetypes' referenced before assignment)  # noqa: E501
                    import mimetypes
                    try:
                        # Salva mimetype original do arquivo
                        mimetype, doc_encoding = mimetypes.guess_type(documento.arquivo.path, strict=True)
                        with open(documento.arquivo.path, 'rb') as file:
                            content = file.read()
                            documento_assinado_base64 = assinador.assinar(
                                documentobase64=base64.b64encode(content).decode('ascii')
                            )

                    # fallback Minio Storage
                    except NotImplementedError:
                        # Salva mimetype original do arquivo
                        mimetype, doc_encoding = mimetypes.guess_type(documento.arquivo.name, strict=True)
                        content = documento.arquivo.read()
                        documento_assinado_base64 = assinador.assinar(
                            documentobase64=base64.b64encode(content).decode('ascii')
                        )

                # Certifica que o documento realmente está assinado antes de prosseguir
                if documento_assinado_base64 is not None:
                    arquivo_temporario_em_memoria = ContentFile(
                        base64.b64decode(documento_assinado_base64.get('signedContent'))
                    )
                    arquivo_temporario_em_memoria.name = 'nomealeatorio.p7s'
                else:
                    raise ThothsignerFailed(
                        'Atenção, o documento não foi assinado pelo Toth Signer,\
                            verifique se o assinador está online e \
                            tente enviar essa manifestação novamente'
                    )

                # Salva o documento em storage conforme origem
                if doc.origem == ManifestacaoDocumento.ORIGEM_PESSOA:
                    documento_original_assistido = DocumentoOriginalAssistido.objects.get(
                        id=doc.origem_id
                    )
                    documento_assinado_salvo_em_storage = DocumentoAssinadoAssistido.objects.create(
                        arquivo=arquivo_temporario_em_memoria
                    )
                    documento_original_assistido.documento_assinado = documento_assinado_salvo_em_storage
                    # atualiza referência do objeto já previamente criado
                    documento.documento_assinado = documento_assinado_salvo_em_storage
                    documento_original_assistido.save()
                elif doc.origem == ManifestacaoDocumento.ORIGEM_ATENDIMENTO:
                    documento_original_atendimento = DocumentoOriginalAtendimento.objects.get(
                        id=doc.origem_id
                    )
                    documento_assinado_salvo_em_storage = DocumentoAssinadoAtendimento.objects.create(
                        atendimento=documento_original_atendimento.atendimento,
                        arquivo=arquivo_temporario_em_memoria
                    )
                    documento_original_atendimento.documento_assinado = documento_assinado_salvo_em_storage
                    # atualiza referência do objeto já previamente criado
                    documento.documento_assinado = documento_assinado_salvo_em_storage
                    documento_original_atendimento.save()
                else:
                    documento_original_atendimento = DocumentoOriginalAtendimento.objects.get(
                        id=doc.origem_id
                    )
                    raise DocumentOriginNotFound(
                        f'Não foi possível determinar \
                        a origem do documento {documento_original_atendimento.nome} enviado'
                    )

            # Adiciona dados do documento ao serviço de manifestação
            servico.add_documento(
                nome=documento.nome if documento.nome else '(SEM NOME)',
                tipo=doc.tipo_mni,
                nivel_sigilo=doc.nivel_sigilo,
                arquivo=documento.documento_assinado.arquivo if devo_enviar_documento_assinado else documento.arquivo,
                ged=None if devo_enviar_documento_assinado else ged,
                mimetype=mimetype if mimetype else None
            )

        # Realiza validação da quantidade de documentos adicionados na manifestação (no lado do solar)
        if len(servico.documentos) != manifestacao.documentos.ativos().count():
            self.retry()

    except ThothsignerFailed as e:

        try:
            self.retry()
        except MaxRetriesExceededError:
            mensagem_de_erro = '''Atenção, os documetos não foram assidados
                                corretamente pelo Toth Signer.
                                Tente enviar novamente a manfiestação {}.
                                Se persistir o erro, por favor verifique
                                com o suporte técnico. Erro: {}
                            '''.format(manifestacao.id, e.message)  # noqa: E501
            __retornar_erro_na_manifestacao(
                manifestacao=manifestacao,
                mensagem=mensagem_de_erro
            )

    except DocumentOriginNotFound as e:
        mensagem_de_erro = '''Atenção, erro nos documentos. Corrija e
                            tente enviar novamente a manfiestação {}
                            com o documento anexado corretamente.
                            Se persistir o erro, por favor verifique
                            com o suporte técnico. Erro: {}
                            '''.format(manifestacao.id, e.massage)  # noqa: E501
        __retornar_erro_na_manifestacao(
            manifestacao=manifestacao,
            mensagem=mensagem_de_erro,
        )

    except ThothsignerUnavailable as e:

        mensagem_de_erro = ''' O assinador se econtra fora do Ar.
                            Tente peticionar novamento mais tarde.
                            Se persistir o erro, contate o suporte técnico. Erro: {}
                            '''.format(e.message)  # noqa: E501

        __retornar_erro_na_manifestacao(
            manifestacao=manifestacao,
            mensagem=mensagem_de_erro
        )
    # Envia manifestação processual
    try:

        sucesso, resposta = servico.enviar()

        # Registra dados da resposta na manifestação
        manifestacao.codigo_procapi = resposta['identificador']
        manifestacao.enviando = False
        manifestacao.enviado = True
        manifestacao.save()

        return resposta['mensagem']
    # Em caso de qualquer tipo de falha com PROCAPI força reenvio
    # TODO trabalhar de maneira mais especifica cada caso (404, 503 etc...)
    except Exception as e:
        try:
            raise self.retry()
            # em caso de finalizar as tentativas de reenvio forçar erro no protocolo.
        except MaxRetriesExceededError:
            mensagem_de_erro = '''Atenção, não foi possível protocolar a\
                                manifestação {} pelo serviço do Procapi. \
                                Tente novamente. Se persistir o erro, \
                                por favor verifique com o suporte técnico. Erro:{}
                                '''.format(manifestacao.id, str(e.args))  # noqa: E501

            __retornar_erro_na_manifestacao(
                manifestacao=manifestacao,
                mensagem=mensagem_de_erro
            )


def __retornar_erro_na_manifestacao(manifestacao,
                                    mensagem="""Ocorreu um erro ao enviar manifestação!
                                    Tente enviar novamente,
                                    se persistir o erro contate o suporte técnico."""):

    "Retornar o erro de protocolo na manifestação enviada."""

    # TODO: Tratmento para uso da task agendada de enviar manifestações da fila caso esteja ativa
    # Deixar a manifestação na fila se é o envio imediato.
    # if not manifestacao.enviando:
    #     return

    manifestacao.mensagem_resposta = mensagem
    manifestacao.situacao = Manifestacao.SITUACAO_ERRO
    manifestacao.enviando = False
    manifestacao.enviado = False
    manifestacao.save()


@shared_task
def procapi_distribuir_aviso(aviso_numero, sistema_webservice):

    quantidade_avisos_distribuidos = 0
    avisos = APIAviso().listar_todos(params={
        'numero': aviso_numero,
        'sistema_webservice': sistema_webservice
    })

    for aviso in avisos:
        sucesso, _ = AvisoService().distribuir(aviso, salvar=True)
        if sucesso:
            quantidade_avisos_distribuidos += 1

    return 'Quantidade de Avisos Distribuidos: {}'.format(quantidade_avisos_distribuidos)


@shared_task
def procapi_distribuir_avisos(sistema_webservice, codigo_orgao_julgador=None):

    cache_key = 'procapi_distribuir_avisos_{}_{}'.format(sistema_webservice, str(codigo_orgao_julgador))

    # Controle de fila para previnir multiplas tasks rodando simultaneamente
    # if cache.get(cache_key):
    #     return 'Distribuição já sendo feita por outra tarefa'
    # else:
    #    cache.set(cache_key, True)

    # Filtros de órgãos julgadores
    params_orgao_julgador = {
        'vara__ativo': True,
        'vara__defensoriavara__desativado_em': None,
        'vara__defensoriavara__distribuicao_automatica': True,
        'sistema_webservice__nome': sistema_webservice
    }

    orgaos_julgadores = OrgaoJulgador.objects.ativos().filter(
        **params_orgao_julgador
    ).distinct()

    if codigo_orgao_julgador:
        orgaos_julgadores = orgaos_julgadores.filter(codigo_mni=codigo_orgao_julgador)
    else:
        for codigo in orgaos_julgadores.values_list('codigo_mni', flat=True):
            print(codigo)
            procapi_distribuir_avisos.apply_async(kwargs={
                'sistema_webservice': sistema_webservice,
                'codigo_orgao_julgador': codigo
            }, queue='geral')
        cache.set(cache_key, False)
        return 'Distribuição será feita por {} sub-tarefas'.format(orgaos_julgadores.count())

    quantidade_avisos_distribuidos = 0

    # Procura pelos avisos de cada órgão julgador encontrado
    for orgao_julgador in orgaos_julgadores:

        # Identifica regras de distribuição vinculadas ao órgão julgador
        defensorias_varas = orgao_julgador.vara.defensoriavara_set.ativos().filter(distribuicao_automatica=True)

        # Filtros de avisos do órgão julgador
        params_api_avisos = {
            'sistema_webservice': sistema_webservice,
            'orgao_julgador': orgao_julgador.codigo_mni,
            'distribuido': False,
            'situacao': ','.join([str(Aviso.SITUACAO_PENDENTE), str(Aviso.SITUACAO_ABERTO)]),
            'ativo': True
        }

        avisos = APIAviso().listar_todos(params=params_api_avisos)

        # Distribui avisos vinculados ao órgão julgador, usando as regras vinculadas
        for aviso in avisos:
            sucesso, _ = AvisoService().distribuir(aviso, defensorias_varas, salvar=True)
            if sucesso:
                quantidade_avisos_distribuidos += 1

    cache.set(cache_key, False)
    return 'Quantidade de Avisos Distribuidos: {}'.format(quantidade_avisos_distribuidos)


@shared_task(bind=True, retry_backoff=True)
def procapi_cadastrar_processos_avisos(self):

    avisos = []
    api_aviso = APIAviso()

    historico_consultas_avisos = HistoricoConsultaAvisos.objects.order_by('data_consulta').last()

    if historico_consultas_avisos is None:  # caso seja primeira vez que a task rodou, consulta todos
        avisos = api_aviso.listar_todos({'distribuido': True})
    else:  # senão consulta data da última consulta
        avisos = api_aviso.listar_todos({
            'distribuido_em': historico_consultas_avisos.data_consulta.strftime('%Y-%m-%dT%H:%M:%S.%f')
        })

    data_distribuicao_mais_recente = datetime(1900, 1, 1)

    for aviso in avisos:

        aviso_distribuido_em = Util.string_to_date(aviso['distribuido_em'][:19], '%Y-%m-%dT%H:%M:%S')

        if aviso_distribuido_em > data_distribuicao_mais_recente:
            data_distribuicao_mais_recente = aviso_distribuido_em

        procapi_cadastrar_processo_aviso.apply_async(kwargs={'aviso_numero': aviso['numero']}, queue='geral')

    if data_distribuicao_mais_recente > datetime(1900, 1, 1):
        HistoricoConsultaAvisos.objects.create(data_consulta=data_distribuicao_mais_recente).save()

    return 'Quantidade de processos cadastrados a partir dos avisos: {}'.format(len(avisos))


@shared_task(bind=True, retry_backoff=True)
def procapi_cadastrar_processo_aviso(self, aviso_numero):

    servico = AvisoService()

    if type(aviso_numero) is str:
        aviso = APIAviso().get(aviso_numero)

    if not aviso['distribuido_defensoria']:
        return False, 'Não é possível cadastar processo de prazo que não foi distribuído para defensoria!'

    try:
        assistido = servico.get_pessoa_assistida(aviso)
    except DadosPessoaInsuficientesException as e:
        return f'Não foi possível cadastrar o processo. {e.message}'

    if not servico.get_parte_processo(aviso):

        sucesso, processo, parte, atendimento = salvar_processo({
            'defensor_cadastro': servico.identificar_defensor(aviso, None),
            'defensoria': aviso['distribuido_defensoria'],
            'defensoria_cadastro': aviso['distribuido_defensoria'],
            'grau': servico.get_grau(aviso),
            'comarca': servico.get_comarca(aviso),
            'tipo': Processo.TIPO_EPROC,
            'numero': aviso['processo']['numero'],
            'parte': servico.get_polo(aviso),
            'requerente': assistido.id,
        })

        if sucesso and processo:
            return True, 'Processo {} cadastrado com sucesso!'.format(processo.numero)
        else:
            return False, 'Erro ao cadastrar processo para o aviso informado!'

    return True, 'Já existe processo cadastrado para o aviso informado!'


@shared_task(bind=True, retry_backoff=True)
def procapi_cadastrar_preanalise_honorario_aviso(self, aviso: str) -> tuple[bool, str]:
    """
    Task que cadastra a pré-analise de honorário a partir de um aviso
    """

    _, aviso = APIAviso().consultar(aviso)

    defensoria = AvisoService().get_defensoria(aviso)

    if not defensoria:
        return False, 'O aviso ainda não foi distribuído!'

    if not defensoria.nucleo or not defensoria.nucleo.honorario:
        return False, 'O aviso não foi distribuído para uma defensoria do tipo honorário!'

    processo_numero = aviso['processo']['numero']
    processo_grau = aviso['grau']

    if not Processo.objects.filter(numero_puro=processo_numero, grau=processo_grau).exists():
        sucesso, _ = procapi_cadastrar_processo_aviso(aviso)
        if not sucesso:
            return False, 'Não foi possível cadastrar o processo relacionado ao aviso!'

    processo = Processo.objects.get(numero_puro=processo_numero, grau=processo_grau)

    if Honorario.objects.filter(fase__processo=processo).exists():
        return False, 'Já existe honorário vinculado ao processo do aviso!'

    servico = ProcessoService(processo)
    if not servico.consultar():
        return False, servico.resposta

    existe_documento, evento = servico.existe_documento_sentenca()
    if not existe_documento:
        return False, 'Não existe sentença vinculada ao processo do aviso!'

    fase = ProcessoEventoService(servico, evento).atualizar(aviso)
    fase.atividade = Fase.ATIVIDADE_SENTENCA
    fase.save()

    return True, 'Registro cadastrado com sucesso!'


# Esta task vai ser chamada na API do SOLAR pelo PROCAPI para cadastro de novo processo caso não existir  # noqa: E501
@shared_task(bind=True, retry_backoff=15, max_retries=3)
def procapi_cadastrar_novo_processo_signal(self, numero_processo, grau, cpf_defensor=None):

    try:
        api_processo = APIProcesso(numero=f'{numero_processo}{grau}')
        sucesso, processo = api_processo.consultar()
        sucesso, partes = api_processo.consultar_partes()
    except Exception:
        self.retry()

    for parte in partes['results']:

        # A parte deve contem ao menos documento principal ou nome da mãe para cadastro automático
        if (parte.get('pessoa').get('documento_principal') is None or
                parte.get('pessoa').get('nome_genitora') is None):
            continue

        # Tribunais Estaduais
        for advogado in parte.get('advogados'):

            if ('tipo_representante' in advogado and advogado.get('tipo_representante') == 'D'):

                filtros = {'vara__codigo_eproc': processo.get('orgao_julgador').get('codigo')}

                associacoes = DefensoriaVara.objects.ativos().filter(**filtros)

                if cpf_defensor and Defensor.objects.filter(servidor__cpf=cpf_defensor).exists():
                    id_defensor = Defensor.objects.filter(servidor__cpf=cpf_defensor).first().id
                else:
                    id_defensor = Atuacao.objects.parcialmente_vigentes().filter(
                        defensoria=associacoes.first().defensoria,
                        tipo__in=[Atuacao.TIPO_TITULARIDADE, Atuacao.TIPO_ACUMULACAO, Atuacao.TIPO_SUBSTITUICAO]
                    ).order_by('-tipo').first().defensor_id

                for associacao in associacoes:

                    codigo_parte = Parte.TIPO_AUTOR

                    partes_associacao_vara = associacao.distribuir_por_polo.all().values(
                        'sigla_sistema_webservice'
                    ).values_list(
                        'sigla_sistema_webservice', flat=True
                    )

                    if parte.get('tipo') in partes_associacao_vara:

                        if parte.get('tipo') == 'PA':
                            codigo_parte = Parte.TIPO_REU
                        elif parte.get('tipo') == 'TC':
                            codigo_parte = Parte.TIPO_TERCEIRO
                        elif parte.get('tipo') == 'VI':
                            codigo_parte = Parte.TIPO_VITIMA
                        elif parte.get('tipo') == 'AD':
                            codigo_parte = Parte.TIPO_ASSISTENTE

                        # Só realiza o cadastro caso a vara do aviso e da associação sejam a mesma e possuir associação naquela parte  # noqa: E501
                        if associacao.vara.codigo_eproc == processo.get('orgao_julgador').get('codigo'):  # noqa: E501

                            id_comarca = Comarca.objects.filter(codigo_eproc=processo.get('localidade').get('comarca')).first().id  # noqa: E501

                            try:
                                sucesso, processo_solar, parte_solar, atendimento = salvar_processo(dados={
                                    'defensor_cadastro': id_defensor,
                                    'defensoria': associacao.defensoria.id,
                                    'defensoria_cadastro': associacao.defensoria.id,
                                    'comarca': id_comarca if id_comarca else None,
                                    'tipo': Processo.TIPO_EPROC,  # Tipo processo de sistema judicial
                                    'numero': numero_processo,
                                    'grau': grau,
                                    'parte': codigo_parte
                                })
                                return 'sucesso: {}, processo_numero: {}, parte_id: {}, atendimento_numero: {}'.format(sucesso, processo_solar.numero, parte_solar.id, atendimento.numero)  # noqa: E501
                            except IntegrityError:
                                return 'Erro de integridade ao gravar processo número {}'.format(numero_processo)
        # Apenas SEEU  (nacional)
        if processo.get('sistema_webservice') == "SEEU-1G-BR":

            # Relaciona todas as associações de Varas a Defensorias
            associacoes = DefensoriaVara.objects.ativos().all()

            for associacao in associacoes:

                # Só realiza o cadastro caso a vara do aviso e da associação sejam a mesma
                if associacao.vara.codigo_eproc == processo.get('orgao_julgador').get('codigo'):

                    partes_associacao_vara = associacao.distribuir_por_polo.all().values(
                        'sigla_sistema_webservice'
                    ).values_list(
                        'sigla_sistema_webservice', flat=True
                    )

                    # Irá cadastrar somente polos passivos (caso associação vara/defensoria seja realizada por engano em outra parte não irá cadastrar)  # noqa: E501
                    if parte.get('tipo') == 'PA' and 'PA' in partes_associacao_vara:

                        if cpf_defensor and Defensor.objects.filter(servidor__cpf=cpf_defensor).exists():
                            id_defensor = Defensor.objects.filter(servidor__cpf=cpf_defensor).first().id
                        else:
                            id_defensor = Atuacao.objects.parcialmente_vigentes().filter(
                                defensoria=associacoes.first().defensoria,
                                tipo__in=[Atuacao.TIPO_TITULARIDADE, Atuacao.TIPO_ACUMULACAO, Atuacao.TIPO_SUBSTITUICAO]
                            ).order_by('-tipo').first().defensor_id

                        id_comarca = Comarca.objects.filter(codigo_eproc=processo.get('localidade').get('comarca')).first().id  # noqa: E501

                        try:
                            sucesso, processo_solar, parte_solar, atendimento = salvar_processo(dados={
                                'defensor_cadastro': id_defensor,
                                'defensoria': associacao.defensoria.id,
                                'defensoria_cadastro': associacao.defensoria.id,
                                'comarca': id_comarca,
                                'tipo': Processo.TIPO_EPROC,  # Tipo processo de sistema judicial
                                'numero': numero_processo,
                                'grau': grau,
                                'parte': Parte.TIPO_REU  # polo passivo (réu)
                            })
                            return 'sucesso: {}, processo_numero: {}, parte_id: {}, atendimento_numero: {}'.format(sucesso, processo_solar.numero, parte_solar.id, atendimento.numero)  # noqa: E501
                        except IntegrityError:
                            return 'Erro de integridade ao gravar processo número {}'.format(numero_processo)


@shared_task
def eproc_set_fase_plantao(dias=1):
    try:
        fase_eproc = FaseService()
        fase_eproc.set_plantao(dias=dias)
    except Exception:
        logger.error(u'Erro ao atualizar tipo das fases de plantão', extra={'params': {'dias': dias}})
        return False
    return True


@shared_task
def eproc_set_fase_tipo():
    fase_tipo = FaseService()
    try:
        resposta = fase_tipo.set_tipo_fase_processual()
        return u'Tipo das fases atualizadas! {0}'.format(resposta)
    except Exception as e:
        logger.error(u'Erro ao atualizar tipo das fases', extra={'params': {'erro': e}})
        return u'Erro ao atualizar tipo das fases'


@shared_task
def eproc_corrige_data_cadastro():
    processos = FaseService()
    try:
        processos.corrigir_data_cadastro()
        return u'Data de cadastro corrigida'
    except Exception as e:
        logger.error(u'Erro na correção da data de cadastro', extra={'params': {'erro': e}})
        return u'Erro na correção da data de cadastro: {0}'.format(e)


@shared_task(bind=True, retry_backoff=15, max_retries=3)
def converter_processos_fisicos_em_eletronicos(self):

    quantidade_processos_atualizados = 0

    # Obtem processos fisicos que possuem / "barra"
    processos_fisicos = Processo.objects.annotate(
        text_len=Length('numero_puro')
    ).filter(
        tipo=Processo.TIPO_FISICO,
        grau__in=[1, 2],
        text_len__gt=19,
        numero__contains='/',
        ativo=True
    )

    for processo in processos_fisicos:
        converter_processo_fisico_em_eletronico.apply_async(kwargs={'processo_fisico_id': processo.id}, queue='default')
        quantidade_processos_atualizados += 1

    return '{} processos serão processados'.format(quantidade_processos_atualizados)


@shared_task(bind=True, retry_backoff=15, max_retries=3)
def converter_processo_fisico_em_eletronico(self, processo_fisico_id):
    mensagem = ""

    processo = Processo.objects.get(id=processo_fisico_id)

    index_caracter_barra = processo.numero.find('/')

    numero_processo_tratado = processo.numero_puro[:index_caracter_barra]

    api = APIProcesso(numero=numero_processo_tratado)
    sucesso, resposta = api.consultar()

    if sucesso:

        numero_processo_procapi = resposta.get('numero')

        # Verifica que o processo já existe no SOLAR com status "pre-cadastro"
        processo_eletronico_ja_cadastrado = Processo.objects.filter(
            numero_puro=numero_processo_procapi,
            grau=int(resposta.get('grau')),
            tipo=Processo.TIPO_EPROC
        )

        if len(processo_eletronico_ja_cadastrado) > 1:
            mensagem += 'O processo {} está cadastrados de maneira duplicada na base de dados, necessário intervenção manual'.format(processo_eletronico_ja_cadastrado)  # noqa: E501

        elif processo_eletronico_ja_cadastrado:

            # Se processo pré-cadastrado então move partes do físico para o eletrônico
            if processo_eletronico_ja_cadastrado.first().pre_cadastro:
                partes_processo_fisico = Parte.objects.filter(processo=processo, atendimento__ativo=True, ativo=True)

                for parte in partes_processo_fisico:
                    parte.processo = processo_eletronico_ja_cadastrado.first()
                    parte.save()

                processo_eletronico_ja_cadastrado.first().pre_cadastro = False
                processo_eletronico_ja_cadastrado.first().save()
                mensagem += 'transferido partes do processo {} para {}'.format(processo.numero, processo_eletronico_ja_cadastrado.first().numero)  # noqa: E501

            # Move fases processuais do físico para o eletrônico
            fases_processuais_cadastradas_no_fisico = processo.lista_fases()

            for fase_fisico in fases_processuais_cadastradas_no_fisico:
                fase = Fase.objects.get(id=fase_fisico.id)
                fase.processo = processo_eletronico_ja_cadastrado.first()
                fase.save()
            # Desativa o processo físico
            processo.ativo = False
            processo.save()
            mensagem += 'transferido fases_processuais do processo {} para {}'.format(processo.numero, processo_eletronico_ja_cadastrado.first().numero)  # noqa: E501

        # Caso não existir versão eletrônica transforma fisico em eletrônico
        else:
            processo.numero = Processo.formatar_numero(numero_processo_procapi)
            processo.grau = int(resposta.get('grau'))
            processo.tipo = Processo.TIPO_EPROC
            processo.save()
            mensagem += 'Processo {} convertido de físico para eletrônico'.format(numero_processo_tratado)
    else:
        mensagem += 'Processo {} não localizado no PROCAPI'.format(numero_processo_tratado)

    return mensagem


@shared_task(bind=True, retry_backoff=15, max_retries=3)
def procapi_importar_classes(self, desativar_acoes_sem_codigo_cnj=False, filtro={}):

    itens = APIClasse().listar_todos(params={})
    qtd_itens_criados_ou_atualizados = 0

    if desativar_acoes_sem_codigo_cnj:
        Acao.objects.filter(codigo_cnj__isnull=False).update(ativo=False)

    for item in itens:
        try:
            classe, novo = Acao.objects.update_or_create(
                codigo_cnj=item['codigo'],
                defaults={
                    'nome': item['nome'],
                    'judicial': True,
                    'ativo': not item['tem_filhos']
                }
            )

            qtd_itens_criados_ou_atualizados = qtd_itens_criados_ou_atualizados + 1

        except Acao.MultipleObjectsReturned:
            Acao.objects.filter(codigo_cnj=item['codigo']).first().update(ativo=False)

    return 'Foram importados/atualizados {} classes com sucesso!'.format(qtd_itens_criados_ou_atualizados)


@shared_task(bind=True, retry_backoff=15, max_retries=3)
def procapi_importar_assuntos(self, desativar_assuntos_sem_codigo_cnj=False, filtro={}):

    itens = APIAssunto().listar_todos(params=filtro)
    qtd_itens_criados_ou_atualizados = 0

    if desativar_assuntos_sem_codigo_cnj:
        Assunto.objects.filter(codigo_cnj__isnull=False).update(ativo=False)

    for item in itens:
        try:
            assunto, novo = Assunto.objects.update_or_create(
                codigo_cnj=item['codigo'],
                defaults={
                    'nome': item['nome'],
                    'ativo': not item['tem_filhos']
                }
            )

            qtd_itens_criados_ou_atualizados = qtd_itens_criados_ou_atualizados + 1

        except Assunto.MultipleObjectsReturned:
            Assunto.objects.filter(codigo_cnj=item['codigo']).first().update(ativo=False)

    return 'Foram importados/atualizados {} assuntos com sucesso!'.format(qtd_itens_criados_ou_atualizados)


@shared_task(bind=True, retry_backoff=15, max_retries=3)
def procapi_importar_sistemas_e_competencias(self, filtro={}):

    itens = APISistema().listar_todos()
    qtd_itens_criados_ou_atualizados = 0

    for item in itens:

        SistemaWebService.objects.update_or_create(
            nome=item['nome'],
            defaults={
                'desativado_em': None,
                'desativado_por': None
            }
        )

    itens = APICompetencia().listar_todos(params=filtro)

    sistemas = dict(SistemaWebService.objects.ativos().values_list('nome', 'id'))
    Competencia.objects.update(desativado_em=datetime.now())

    for item in itens:

        # Importa apenas competências que tenha nome
        if 'nome' in item and item['nome']:
            competencia, novo = Competencia.objects.update_or_create(
                codigo_mni=item['codigo'],
                sistema_webservice_id=sistemas[str(item['sistema_webservice'])],
                defaults={
                    'nome': item['nome'],
                    'desativado_em': None,
                    'desativado_por': None
                }
            )
            qtd_itens_criados_ou_atualizados = qtd_itens_criados_ou_atualizados + 1

    return 'Foram importados/atualizados {} competencias com sucesso!'.format(qtd_itens_criados_ou_atualizados)
