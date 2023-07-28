# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import calendar
import json as simplejson
import logging
import math
import mimetypes
from datetime import date, datetime, time, timedelta

# Bibliotecas de terceiros
import re
import reversion

from constance import config
from core.context_processors import permissao_acesso_propacs
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import connection, transaction
from django.db.models import Count, Sum, Case, When, Value, IntegerField, F, Q, BooleanField, Prefetch, OuterRef, Subquery, Exists
from django.http import Http404, HttpResponseRedirect, JsonResponse, FileResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import CreateView, ListView, TemplateView, View
from djdocuments_solar_backend.backend import SolarDefensoriaBackend
from djdocuments.models import Documento as DocumentoGED
from djdocuments.views.documentos import VincularDocumentoBaseView, DocumentoCriar
from rest_framework import mixins, permissions
from rest_framework_extensions.mixins import DetailSerializerMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet


# Solar
from assistido.models import PessoaAssistida as Pessoa, Documento as DocumentoAssistido
from atendimento.atendimento.usecases import download_documentos
from atendimento.atendimento.models import TipoVulnerabilidade, AtendimentoVulnerabilidade
from atendimento.atendimento.permissions import PERMISSAO_PARA_ARQUIVAR, PERMISSAO_PARA_DESARQUIVAR
from evento.models import Evento
from contrib import constantes
from contrib.models import Bairro, Comarca, Dados, Documento, Servidor, Util, Defensoria, Telefone
from contrib.services import envia_sms
from core.models import (
    Classe as CoreClasse,
    Documento as CoreDocumento,
    TipoDocumento as CoreTipoDocumento,
    TipoEvento as CoreTipoEvento
)
from defensor.models import Atuacao, Defensor
from evento.models import Categoria
from indeferimento.models import Indeferimento
from luna_chatbot_client.tasks import (
    chatbot_notificar_requerente_atendimento,
    chatbot_notificar_requerente_documento,
    chatbot_notificar_requerente_exclusao,
)
from nucleo.nucleo.models import Formulario as FormularioNucleo
from nucleo.nucleo.models import Resposta as RespostaNucleo
from nucleo.nucleo.models import Nucleo
from nucleo.nadep.models import Prisao, Atendimento as AtendimentoPreso
from nucleo.nadep.services import Preso as ServicesPreso
from procapi_client.services import APIAviso
from processo.processo.forms import ProcessoForm, ProcessoParteForm
from processo.processo.models import Manifestacao, ManifestacaoDocumento, Parte as ParteProcesso, Processo
from processo.processo.models import Audiencia
from relatorios.models import Local, Relatorio
# Modulos locais
from .forms import (
    AnotacaoForm,
    AtendimentoDefensorForm,
    AtividadeForm,
    AtividadeDefensorForm,
    BuscarAtendimentoDocumentosForm,
    BuscarAtendimentoForm,
    BuscarTarefaForm,
    DistribuirAtendimentoForm,
    DocumentoForm,
    TabDocumentoForm,
    DocumentoRespostaForm,
    AgendarDocumentoForm,
    NotificacaoForm,
    NucleoPedidoForm,
    NucleoRespostaForm,
    TarefaForm,
    CriarDocumentoOnlineParaAtendimentoForm,
    CriarDocumentoOnlineParaAtendimentoViaModeloPublicoForm,
)
from .models import (
    Acesso,
    Acordo,
    Arvore,
    Assunto,
    Atendimento,
    AtendimentoParticipante,
    AtendimentoVisualizacao,
    Coletivo,
    Documento as DocumentoAtendimento,
    Cronometro,
    Defensor as AtendimentoDefensor,
    Documento as AtendimentoDocumento,
    MotivoExclusao,
    Pessoa as AtendimentoPessoa,
    Tarefa,
    TarefaVisualizacao,
    FormaAtendimento,
    PastaDocumento)
from .serializers import DocumentoAtendimentoSerializer, PastaDocumentoSerializer
from .services import (
    AtendimentoService,
    ServiceDocumentoAtendimento,
    arquivamento_esta_habilitado,
    atualiza_tarefa_atendimento_origem,
    envia_sms_exclusao,
    envia_email_exclusao,
    preencher_campos_ged,
    filtra_tarefas,
    swap_ordenacao_tarefas,
    get_tarefas_propac,
    criar_documento_ged_para_o_atendimento,
    consulta_status_arquivado,
    checar_possibilidade_retorno
)
from .tasks import atendimento_cria_arvore
from .view_mixins import SingleAtendimentoDefensorObjectMixin

logger = logging.getLogger(__name__)


@never_cache
@login_required
@permission_required('atendimento.change_atendimento')
def atender(request, atendimento_numero):
    """Utilizado para carregar a página Ficha de Atendimento"""

    servidor = request.user.servidor

    if hasattr(request.user.servidor, 'defensor'):
        defensor = request.user.servidor.defensor
    else:
        defensor = None

    try:
        atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero, ativo=True)
    except Exception:
        messages.error(request, u'O atendimento {} não existe!'.format(
            atendimento_numero
        ))
        return redirect('atendimento_index')

    # Se foi remarcado, redireciona para novo atendimento
    if atendimento.remarcado:
        messages.warning(request, u'O atendimento foi remarcado, seu novo número é {}'.format(
            atendimento.remarcado.numero
        ))
        return redirect('atendimento_atender', atendimento.remarcado.numero)

    # Se tipo processo e tem inicial, redireciona para atendimenot inicial
    if atendimento.tipo == Atendimento.TIPO_PROCESSO and atendimento.inicial and atendimento.inicial.ativo:
        return redirect('atendimento_atender', atendimento.inicial.numero)

    hoje = date.today()
    dia_um = datetime(hoje.year, hoje.month, 1)
    pode_ver_historico_do_atendimento = (atendimento.pode_ver_atendimento(request.user) and
                                         atendimento.pode_ver_detalhes_do_atendimento(request.user) and
                                         verifica_permissao_editar(request.user, atendimento))

    # Registrar primeira vez que um usuário acessar a página de atendimento a cada dia (se não for superusuário)
    if config.REGISTRAR_VISUALIZACAO_ATENDIMENTO_SUPERUSUARIO or not request.user.is_superuser:

        visualizou_hoje = AtendimentoVisualizacao.objects.filter(
            atendimento=atendimento.at_inicial,
            visualizado_por=request.user,
            visualizado_em__gte=hoje
        ).exists()

        if not visualizou_hoje:
            AtendimentoVisualizacao.objects.create(
                atendimento=atendimento.at_inicial,
                evento=atendimento,
                visualizado_por=request.user
            )

    form = AtendimentoDefensorForm(instance=atendimento)
    form_processo = ProcessoForm()
    form_processo_parte = ProcessoParteForm(prefix='parte')

    tab = request.GET.get('tab', None)  # seta a Tab ativa

    # altera qualificacao se solicitado para este atendimento e não realizado ou realizado no mês corrente
    if request.session.get('qualificacao_id') \
            and atendimento.id == request.session.get('atendimento_id') \
            and (request.user.has_perm('atendimento.requalificar_atendimento_retroativo') or (
                atendimento.data_atendimento is None or
                atendimento.data_atendimento >= dia_um)
            ):

        # recupera e aplica qualificacao da sessao
        atendimento.qualificacao_id = request.session['qualificacao_id']
        atendimento.save()

        # remove qualificacao da sessao
        request.session['qualificacao_id'] = None
        request.session['atendimento_id'] = None

    if request.session.get('nucleo'):
        ativo = request.session.get('nucleo') == atendimento.nucleo
    else:
        ativo = (atendimento.nucleo is None)

    prisoes = None
    preso = None

    if atendimento.requerente:
        prisoes = Prisao.objects.filter(pessoa=atendimento.requerente.pessoa, ativo=True).order_by('-data_prisao')
        preso = ServicesPreso(atendimento.requerente.pessoa)

    if prisoes:

        nadep = AtendimentoPreso.objects.filter(id=atendimento.id).first()

        if not atendimento.tipo == atendimento.TIPO_PROCESSO and not atendimento.realizado or atendimento.agendado_hoje:

            if request.GET.get('pessoa_id'):

                interessado = Pessoa.objects.filter(id=request.GET.get('pessoa_id')).first()

                if interessado:

                    if not atendimento.pessoas.filter(pessoa=interessado).exists():
                        atendimento.add_requerente(interessado.id)

                    nadep = AtendimentoPreso()
                    nadep.__dict__.update(atendimento.__dict__)
                    nadep.interessado = interessado
                    nadep.save()

    atendimento_permissao = atendimento.permissao_acessar(usuario=request.user)
    permissao_editar = verifica_permissao_editar(request.user, atendimento)

    # Só gera um cronômetro para calcular tempo de atendimento se pessoa tem permissão para atender
    if permissao_editar:

        try:
            cronometro, msg = Cronometro.objects.get_or_create(
                atendimento=atendimento,
                servidor=servidor,
                finalizado=False
            )
        except MultipleObjectsReturned:
            cronometro = Cronometro.objects.filter(
                atendimento=atendimento,
                servidor=servidor,
                finalizado=False
            ).first()

        cronometro.atualizar()

    acesso_solicitado = atendimento.acesso_solicitado(defensor)
    acesso_concedido = atendimento.acesso_concedido(defensor)
    propacs_acesso = permissao_acesso_propacs(request)

    if defensor:

        # Atuacoes vigentes para o dia
        atuacoes = Atuacao.objects.vigentes_por_defensor(defensor=defensor)

        if request.session.get('nucleo'):
            atuacoes = atuacoes.filter(defensoria__nucleo=request.session.get('nucleo'))

    request.session['atendimento_id'] = atendimento.id

    relatorios_dados = Relatorio.objects.filter(
        papeis=request.user.servidor.papel,
        locais__pagina=Local.PAG_ATENDIMENTO_ATENDER
    ).ativos()

    relatorios_btn_requerente = Relatorio.objects.filter(
        papeis=request.user.servidor.papel,
        locais__pagina=Local.PAG_ATENDIMENTO_ATENDER_BTN_REQUERENTE
    ).ativos()

    relatorios_btn_requerido = Relatorio.objects.filter(
        papeis=request.user.servidor.papel,
        locais__pagina=Local.PAG_ATENDIMENTO_ATENDER_BTN_REQUERIDO
    ).ativos()

    angular_app = 'atenderApp'
    angular = 'AtendimentoCtrl'

    return render(request=request, template_name="atendimento/atender.html", context=locals())


@never_cache
@login_required
@permission_required('atendimento.change_atendimento')
def ocultar(request, atendimento_numero, defensoria):

    try:
        AtendimentoDefensor.objects.filter(
            numero=atendimento_numero,
            ativo=True
        ).update(
            exibir_no_painel_de_acompanhamento=False
        )
    except Exception:
        messages.error(request, u'Não foi possível ocultar o atendimento {}!'.format(
            atendimento_numero
        ))
        return redirect('atendimento_index')

    return redirect(
        'atendimento_acompanhamento_defensoria_painel',
        defensoria_id=defensoria,
        painel='sem-peca-juridica'
    )


@login_required
def atender_tab_atividades(request, atendimento_numero):
    atendimento = get_object_or_404(
        AtendimentoDefensor,
        numero=atendimento_numero,
        defensoria__nucleo__apoio_pode_registrar_atividades=True,
        remarcado=None,
        ativo=True)

    # Atuações vigentes de defensores na defensoria do atendimento
    atuacoes = atendimento.defensoria.all_atuacoes.vigentes()
    participantes_exists = False
    permissao = False

    # Verifica se existem participantes de acordo com o tipo de núcleo
    if atendimento.defensoria.nucleo.multidisciplinar:
        participantes_exists = atendimento.participantes.exists()
        permissao = request.user.is_superuser or \
            atendimento.participantes.filter(usuario=request.user).exists() or \
            request.user.has_perm(perm='nucleo.admin_multidisciplinar')
    else:
        participantes_exists = atuacoes.exists()
        permissao = request.user.is_superuser or \
            atuacoes.filter(defensor=request.user.servidor.defensor).exists()

    atendimento_realizado = atendimento.realizado

    hoje = datetime.now()
    diaMin = datetime(hoje.year, hoje.month, 1)
    diaMax = datetime(hoje.year, hoje.month, calendar.monthrange(hoje.year, hoje.month)[1])

    pedido = atendimento.origem

    atividades = atendimento.filhos.select_related(
        'qualificacao'
    ).prefetch_related(
        'documento_set',
        'participantes_atendimentos'
    ).filter(
        origem=atendimento,
        ativo=True,
        tipo=Atendimento.TIPO_ATIVIDADE
    ).order_by(
        'data_atendimento'
    )

    documentos = AtendimentoDocumento.objects.filter(
        atendimento__origem=atendimento,
        ativo=True
    ).order_by('documento_online__esta_assinado', 'nome')

    form = DocumentoForm()

    return render(request=request, template_name="atendimento/atender_tab_atividades.html", context=locals())


@login_required
def atender_tab_documentos(request, atendimento_numero):

    atendimento = get_object_or_404(
        AtendimentoDefensor,
        numero=atendimento_numero,
        ativo=True,
        remarcado=None
    )

    if hasattr(request.user.servidor, 'defensor'):
        defensor = request.user.servidor.defensor
    else:
        defensor = None

    atendimento_para_upload = atendimento
    atendimento_permissao = False
    acesso_concedido = False
    pode_cadastrar_peticionamento = False
    pode_visualizar_aba = True
    abas_atendimento_restritas = config.ATIVAR_SIGILO_ABAS_ATENDIMENTO.title().replace(" ", "").split(',')

    # Verifica se é um pedido de apoio (se possui filho TIPO_NUCLEO)
    atendimento_para_apoio = atendimento.filhos.filter(
        tipo=Atendimento.TIPO_NUCLEO,
        ativo=True
    ).exists()

    # Se é um pedido de apoio, procura por último atendimento válido (que não seja pedido de apoio)
    if atendimento_para_apoio:

        atendimento_para_upload = AtendimentoDefensor.objects.filter(
            (
                Q(id=atendimento.inicial_id) |
                Q(inicial=atendimento.inicial_id)
            ) &
            (
                (
                    Q(tipo__in=[
                        Atendimento.TIPO_INICIAL,
                        Atendimento.TIPO_RETORNO,
                        Atendimento.TIPO_INTERESSADO,
                        Atendimento.TIPO_VISITA]) & ~
                    Q(data_atendimento=None)
                ) |
                Q(tipo=Atendimento.TIPO_PROCESSO)
            ) &
            Q(ativo=True)
        ).exclude(
            filhos__tipo=Atendimento.TIPO_NUCLEO
        ).order_by(
            '-data_atendimento'
        ).first()

        if atendimento_para_upload is None:
            raise Http404

    atendimento_permissao = atendimento.permissao_acessar(usuario=request.user)
    acesso_concedido = atendimento.acesso_concedido(defensor)

    try:
        if abas_atendimento_restritas[0] == 'True' and not atendimento_permissao and not acesso_concedido:
            pode_visualizar_aba = False
    except IndexError:
        pode_visualizar_aba = True

    # Verifica se usário está lotado em alguma defensoria com o recurso peticionamento habilitado
    pode_cadastrar_peticionamento = defensor.atuacoes().vigentes().filter(
        defensoria__pode_cadastrar_peticionamento=True
    ).exists()

    pode_peticionar_documento_nao_ged = False
    if atendimento.defensoria.nucleo is not None:
        pode_peticionar_documento_nao_ged = atendimento.defensoria.nucleo.acordo

    form_documento = DocumentoForm()
    form_peticao_simples = TabDocumentoForm(request.GET, usuario=request.user)

    '''
    ATENÇÃO!!!
    Jamais use 'atendimento' no contexto para upload de arquivos, visto que a validação acima pode trocar o atendimento
    usado. Isso é necessário visto que o usuário pode estar com o pedido de apoio aberto, ocasionando o envio do
    documento para o setor solicitado, mas atendimento em questão ainda é necessário para outros tratamentos
    '''

    return render(
        request=request,
        template_name="atendimento/atender_tab_documentos.html",
        context={
            'atendimento': atendimento,
            'atendimento_para_upload': atendimento_para_upload,
            'atendimento_permissao': atendimento_permissao,
            'pode_visualizar_aba': pode_visualizar_aba,
            'acesso_concedido': acesso_concedido,
            'pode_cadastrar_peticionamento': pode_cadastrar_peticionamento,
            'pode_peticionar_documento_nao_ged': pode_peticionar_documento_nao_ged,
            'form_documento': form_documento,
            'form_peticao_simples': form_peticao_simples,
            'config': config
        }
    )


def download_documentos_anexos(request, atendimento_numero):
    requisicao_payload = simplejson.loads(request.body)

    prefixo_arquivo = requisicao_payload.get("prefixo_arquivo", "documentos_solicitados")
    tipo_documentos = requisicao_payload.get("tipo_documentos")
    arquivos_solicitados = requisicao_payload.get("arquivos_solicitados")

    arquivo_path = download_documentos(arquivos_solicitados, prefixo_arquivo,
                                       atendimento_numero, tipo_documentos)

    return FileResponse(open(arquivo_path, "rb"), as_attachment=True)


@login_required
def atender_tab_tarefas(request, atendimento_numero):

    atendimento = get_object_or_404(
        AtendimentoDefensor,
        numero=atendimento_numero,
        remarcado=None,
        ativo=True)

    defensor = None
    if hasattr(request.user.servidor, 'defensor'):
        defensor = request.user.servidor.defensor

    atendimento_permissao = atendimento.permissao_acessar(usuario=request.user)
    acesso_concedido = atendimento.acesso_concedido(defensor)
    abas_atendimento_restritas = config.ATIVAR_SIGILO_ABAS_ATENDIMENTO.title().replace(" ", "").split(',')

    pode_visualizar_aba = True
    try:
        if abas_atendimento_restritas[1] == 'True' and not atendimento_permissao and not acesso_concedido:
            pode_visualizar_aba = False
    except IndexError:
        pode_visualizar_aba = True

    return render(request=request, template_name="atendimento/atender_tab_tarefas.html", context=locals())


def get_defensorias_usuario(usuario):

    defensorias = Defensoria.objects.none()

    if hasattr(usuario.servidor, 'defensor'):

        agora = datetime.now()

        # TODO: usar método Defensor.atuacoes_vigentes() c/ suporte aos eventos itnerantes
        defensorias = Defensoria.objects.filter(
            (
                (
                    Q(all_atuacoes__defensor=usuario.servidor.defensor)
                ) &
                (
                    (
                        Q(all_atuacoes__data_inicial__lte=agora) &
                        Q(all_atuacoes__data_final__gte=agora)
                    ) |
                    (
                        Q(all_atuacoes__data_inicial__lte=agora) &
                        Q(all_atuacoes__data_final=None)
                    )
                ) & Q(all_atuacoes__ativo=True)
            ) |
            (
                Q(evento__participantes=usuario.servidor) &
                Q(evento__data_inicial__lte=agora) &
                Q(evento__data_final__gte=agora - timedelta(days=agora.day)) &
                Q(evento__ativo=True)
            )
        ).distinct()

    return defensorias


# todo: mover para um local apropriado
def verifica_permissao_editar(usuario, atendimento):

    tem_permissao = False

    if usuario.is_superuser:
        tem_permissao = True
    else:
        tem_permissao = get_defensorias_usuario(usuario).filter(id=atendimento.defensoria_id).exists()

    return tem_permissao


@login_required
def atender_tab_historico(request, atendimento_numero):

    if hasattr(request.user.servidor, 'defensor'):
        defensor = request.user.servidor.defensor
    else:
        defensor = None

    atendimento = AtendimentoDefensor.objects.filter(numero=atendimento_numero, ativo=True, remarcado=None).first()
    pode_efetuar_retorno = checar_possibilidade_retorno(atendimento)

    inicio = date.today()
    termino = datetime.combine(inicio, time.max)

    if atendimento:

        nadep = AtendimentoPreso.objects.filter(id=atendimento.id).first()

        if atendimento.requerente:
            prisoes = Prisao.objects.filter(pessoa=atendimento.requerente.pessoa, ativo=True).order_by('-data_prisao')
            preso = ServicesPreso(atendimento.requerente.pessoa)

        # verifição que qual data será usada como referência para realizar o atendimento (padrão: hoje)
        data_referencia = inicio

        # se já realizado, assume data do atendimento como data de referência
        if atendimento.data_atendimento:
            data_referencia = atendimento.data_atendimento
        # senão, se puder realizar retroativamente, assume data do agendamento como data de referência
        elif (
            atendimento.tipo != Atendimento.TIPO_NUCLEO and
            atendimento.data_agendamento is not None and
            atendimento.data_agendamento.date() < date.today() and
            atendimento.pode_atender_retroativo(request.user)
        ):
            data_referencia = atendimento.data_agendamento

        q = Q(ativo=True)
        q &= Q(atendimento=atendimento.at_inicial)
        q &= ~Q(documento_online=None)
        documentos = AtendimentoDocumento.objects.filter(q).order_by('-documento_online__esta_assinado', 'nome')

        form = AtendimentoDefensorForm(instance=atendimento)

        permissao_acessar = atendimento.permissao_acessar(usuario=request.user)
        permissao_editar = verifica_permissao_editar(request.user, atendimento)

        if defensor:

            acesso_solicitado = atendimento.acesso_solicitado(defensor)
            acesso_concedido = atendimento.acesso_concedido(defensor)
            form_nucleo = NucleoPedidoForm()

            defensorias = get_defensorias_usuario(request.user)
            defensorias_titular = defensorias.filter(
                Q(all_atuacoes__tipo__in=[Atuacao.TIPO_TITULARIDADE, Atuacao.TIPO_ACUMULACAO])
            )

            esta_lotado_classe_especial = defensorias.filter(grau=Defensoria.GRAU_2).exists()
            possui_processo_2grau = atendimento.at_inicial.get_processos().filter(
                parte__defensoria__grau=Defensoria.GRAU_2
            ).exists()

            razoes_indeferimento = CoreClasse.objects.processo_indeferimento().ativos()
            setores_encaminhamento_indeferimento = Defensoria.objects.ativos().filter(
                nucleo__indeferimento_pode_receber_negacao=True
            )

            pessoas = list(atendimento.get_requerentes().values_list('pessoa_id', flat=True))

            # Negativas de Atendimento dos requerentes em outros atendimentos
            indeferimentos_requerentes = Indeferimento.objects.annotate(
                recursos=Sum(
                    Case(
                        When(processo__eventos__tipo__tipo=CoreTipoEvento.TIPO_RECURSO, then=1),
                        output_field=IntegerField()
                    ))
            ).filter(
                Q(processo__desativado_em=None) &
                Q(processo__classe__tipo=CoreClasse.TIPO_NEGACAO_HIPOSSUFICIENCIA) &
                Q(processo__partes__pessoa__in=pessoas) &
                Q(
                    Q(recursos=0) |
                    Q(resultado=Indeferimento.RESULTADO_INDEFERIDO)
                ) &
                ~Q(atendimento=atendimento)
            )

            # Busca todos os Indeferimentos relativos a qualquer atendimento da árvore de atendimentos
            inicial_id = None
            atendimentos_id = []

            if atendimento.inicial:
                inicial_id = atendimento.inicial.id
            else:
                inicial_id = atendimento.id

            atendimentos_id = Atendimento.objects.filter(
                Q(ativo=True) &
                (
                    Q(id=inicial_id) |
                    Q(inicial__id=inicial_id)
                )
            ).values_list('id', flat=True)

            indeferimentos = Indeferimento.objects.ativos().filter(atendimento_id__in=atendimentos_id)

        mostrar_exibicao_acesso_atendimento = False

        if config.MODO_EXIBICAO_ACESSO_ATENDIMENTO == '1' and atendimento.tipo == Atendimento.TIPO_INICIAL:  # inicial
            mostrar_exibicao_acesso_atendimento = True
        elif config.MODO_EXIBICAO_ACESSO_ATENDIMENTO == '2':  # todos
            mostrar_exibicao_acesso_atendimento = True

        pode_atender_sem_liberar = request.user.has_perm('atendimento.atender_sem_liberar')
        pode_atender_retroativo = atendimento.pode_atender_retroativo(request.user)
        pode_ver_atendimento = atendimento.pode_ver_atendimento(request.user)
        pode_ver_detalhes_do_atendimento = atendimento.pode_ver_detalhes_do_atendimento(request.user)

        possui_permissao_remeter_atendimento = request.user.has_perm(perm='atendimento.remeter_atendimento')
        exibir_vulnerabilidade_digital = config.EXIBIR_VULNERABILIDADE_DIGITAL
        possui_permissao_arquivar_atendimento = request.user.has_perm(perm=PERMISSAO_PARA_ARQUIVAR)
        possui_permissao_desarquivar_atendimento = request.user.has_perm(perm=PERMISSAO_PARA_DESARQUIVAR)

        mostrar_campos_interesse_conciliar = True if settings.SIGLA_UF == 'rn' else False
        mostrar_botao_encerrar = True if settings.SIGLA_UF == 'am' else False

    return render(request=request, template_name="atendimento/atender_tab_historico.html", context=locals())


@login_required
def atender_tab_outros(request, atendimento_numero):

    atendimento = get_object_or_404(
        AtendimentoDefensor,
        numero=atendimento_numero,
        remarcado=None,
        ativo=True)

    atendimento = atendimento.at_inicial  # redireciona para atendimento inicial
    atendimento_permissao = atendimento.permissao_acessar(usuario=request.user)
    abas_atendimento_restritas = config.ATIVAR_SIGILO_ABAS_ATENDIMENTO.title().replace(" ", "").split(',')
    acesso_concedido = atendimento.acesso_concedido(request.user.servidor.defensor)
    pode_visualizar_aba = True

    try:
        if abas_atendimento_restritas[3] == 'True' and not atendimento_permissao and not acesso_concedido:
            pode_visualizar_aba = False
    except IndexError:
        pode_visualizar_aba = True

    return render(request=request, template_name="atendimento/atender_tab_outros.html", context=locals())


@login_required
def atender_tab_processos(request, atendimento_numero):

    atendimento = get_object_or_404(
        AtendimentoDefensor,
        numero=atendimento_numero,
        remarcado=None,
        ativo=True)

    bloqueado = False
    if not config.VINCULAR_PROCESSO_COM_ATENDIMENTO_EM_ANDAMENTO:
        bloqueado = atendimento.at_inicial.tipo != Atendimento.TIPO_PROCESSO and not atendimento.at_inicial.realizado

    hoje = date.today()
    diaMin = date(hoje.year, hoje.month, 1)
    atendimento_permissao = atendimento.permissao_acessar(usuario=request.user)
    abas_atendimento_restritas = config.ATIVAR_SIGILO_ABAS_ATENDIMENTO.title().replace(" ", "").split(',')
    acesso_concedido = atendimento.acesso_concedido(request.user.servidor.defensor)
    pode_visualizar_aba = True
    sigla_uf = settings.SIGLA_UF.upper()

    evento_desbloqueio = Evento.get_desbloqueio_vigente_por_usuario(usuario=request.user.servidor.defensor).first()

    if evento_desbloqueio:
        diaMin = date(evento_desbloqueio.data_ini.year, evento_desbloqueio.data_ini.month, 1)
    elif hoje.day <= config.DIA_LIMITE_CADASTRO_FASE:
        diaMin -= relativedelta(months=1)

    try:
        if abas_atendimento_restritas[2] == 'True' and not atendimento_permissao and not acesso_concedido:
            pode_visualizar_aba = False
    except IndexError:
        pode_visualizar_aba = True

    sistemas_webservices_procapi = []

    if config.ATIVAR_PROCAPI:
        from procapi_client.services import APISistema
        sistemas_webservices_procapi = APISistema().listar_todos()

    return render(request=request, template_name="atendimento/atender_tab_processo.html", context=locals())


@login_required
def atender_tab_processos_eproc(request, atendimento_numero):

    atendimento = get_object_or_404(
        AtendimentoDefensor,
        numero=atendimento_numero,
        remarcado=None,
        ativo=True)

    atendimento_permissao = atendimento.permissao_acessar(usuario=request.user)
    abas_atendimento_restritas = config.ATIVAR_SIGILO_ABAS_ATENDIMENTO.title().replace(" ", "").split(',')
    acesso_concedido = atendimento.acesso_concedido(request.user.servidor.defensor)
    pode_visualizar_aba = True

    try:
        if abas_atendimento_restritas[2] == 'True' and not atendimento_permissao and not acesso_concedido:
            pode_visualizar_aba = False
    except IndexError:
        pode_visualizar_aba = True

    if settings.SIGLA_UF.upper() == 'AM':
        return render(request=request, template_name="atendimento/atender_tab_tjam.html", context=locals())

    return render(request=request, template_name="atendimento/atender_tab_eproc.html", context=locals())


@login_required
def atender_tab_procedimentos(request, atendimento_numero):
    atendimento = get_object_or_404(
        AtendimentoDefensor,
        numero=atendimento_numero,
        remarcado=None,
        ativo=True)
    atendimento_permissao = atendimento.permissao_acessar(usuario=request.user)
    abas_atendimento_restritas = config.ATIVAR_SIGILO_ABAS_ATENDIMENTO.title().replace(" ", "").split(',')
    acesso_concedido = atendimento.acesso_concedido(request.user.servidor.defensor)
    pode_visualizar_aba = True
    propacs_acesso = permissao_acesso_propacs(request)

    try:
        if abas_atendimento_restritas[4] == 'True' and not atendimento_permissao and not acesso_concedido:
            pode_visualizar_aba = False
    except IndexError:
        pode_visualizar_aba = True
        print("Erro")

    return render(request=request, template_name="atendimento/atender_tab_procedimento.html", context=locals())


@login_required
def atender_tab_oficios(request, atendimento_numero):
    return render(request=request, template_name="atendimento/atender_tab_oficio.html", context=locals())


@never_cache
@login_required
@permission_required('atendimento.change_atendimento')
def atender_get(request, atendimento_numero):

    resposta = []

    try:
        atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero, ativo=True, remarcado=None)
    except AtendimentoDefensor.DoesNotExist:
        atendimento = None

    if atendimento:

        inicial = atendimento.at_inicial
        arvore = Arvore.objects.filter(atendimento=inicial, data_exclusao=None, ativo=True).first()

        # se árvore não existe, tenta criar
        if not arvore:
            arvore = atendimento_cria_arvore(inicial.numero)

        # se árvore existe, retorna conteúdo
        if arvore:
            resposta = simplejson.loads(arvore.conteudo)

        if config.ATIVAR_ORDENACAO_ATENDIMENTO_DECRESCENTE:
            resposta.reverse()

    return JsonResponse(resposta, safe=False)


@never_cache
@login_required
@permission_required('atendimento.change_atendimento')
def atender_processos_get(request, atendimento_numero):

    atendimento = get_object_or_404(
        AtendimentoDefensor,
        numero=atendimento_numero,
        ativo=True,
        remarcado=None
    )

    processos = atendimento.get_processos().filter(
        pre_cadastro=False,
    ).annotate(
        acao_nome=F('acao__nome'),
        atendimento_numero=F('parte__atendimento__numero')
    ).values(
        'id',
        'numero',
        'numero_puro',
        'chave',
        'grau',
        'tipo',
        'acao_nome',
        'atendimento_numero'
    )

    return JsonResponse(list(processos), safe=False)


@never_cache
@login_required
def atender_outros_get(request, atendimento_numero):

    atendimento = get_object_or_404(
        AtendimentoDefensor,
        numero=atendimento_numero,
        ativo=True,
        remarcado=None
    )

    if atendimento.requerente is None:
        raise Http404

    outros = AtendimentoPessoa.objects.select_related(
        'atendimento__excluido_por',
        'atendimento__defensor__defensor__servidor',
        'atendimento__defensor__defensoria',
        'atendimento__qualificacao__area',
    ).filter(
        atendimento__tipo__in=[Atendimento.TIPO_INICIAL, Atendimento.TIPO_VISITA, Atendimento.TIPO_PROCESSO],
        atendimento__inicial=None,
        atendimento__remarcado=None,
        pessoa=atendimento.requerente.pessoa,
        ativo=True
    ).exclude(
        atendimento__defensor=None,
    ).exclude(
        atendimento_id=atendimento.at_inicial.id
    )

    atendimentos = []
    for outro_pessoa in outros:
        outro = outro_pessoa.atendimento.defensor
        atendimentos.append({
            'id': outro.id,
            'numero': outro.numero,
            'data_agendamento': Util.date_to_json(outro.data_agendamento) if outro.data_agendamento else None,
            'data_atendimento': Util.date_to_json(outro.data_atendimento) if outro.data_atendimento else None,
            'data_exclusao': Util.date_to_json(outro.data_exclusao) if outro.data_exclusao else None,
            'motivo_exclusao': outro.motivo_exclusao,
            'excluido_por': outro.excluido_por.nome if outro.excluido_por else None,
            'requerente': outro.requerente.pessoa.nome if outro.requerente else None,
            'requerido': outro.requerido.pessoa.nome if outro.requerido else None,
            'defensor': outro.defensor.nome if outro.defensor else None,
            'defensor_foto': outro.defensor.servidor.get_foto() if outro.defensor.servidor else None,
            'defensoria': outro.defensoria.nome if outro.defensoria else None,
            'nucleo': outro.nucleo.nome if outro.nucleo else None,
            'area': outro.qualificacao.area.nome if outro.qualificacao else None,
            'pedido': outro.qualificacao.titulo if outro.qualificacao else None,
            'realizado': outro.realizado,
            'processos': [],
            'tipo': outro_pessoa.tipo,
            'processo': (outro.tipo == Atendimento.TIPO_PROCESSO),
            'ativo': outro.ativo,
        })

        for parte in outro.processo_partes:
            atendimentos[-1]['processos'].append({
                'data_cadastro': Util.date_to_json(parte.data_cadastro),
                'tipo': parte.processo.get_tipo_display(),
                'numero': parte.processo.numero,
                'numero_puro': parte.processo.numero_puro,
                'grau': parte.processo.grau,
                'parte': parte.parte,
                'acao': parte.processo.acao.nome if parte.processo.acao else None,
                'vara': parte.processo.vara.nome if parte.processo.vara else None,
                'area': parte.processo.area.nome if parte.processo.area else None,
            })

    return JsonResponse(atendimentos, safe=False)


@never_cache
@login_required
def atender_procedimentos_propacs_get(request, atendimento_numero):
    procedimentos_list = []
    atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero, ativo=True, remarcado=None)
    inicial = atendimento.at_inicial if atendimento.at_inicial else atendimento
    procedimentos = inicial.procedimentos.filter(ativo=True)

    for procedimento in procedimentos:
        procedimentos_list.append({
            'numero': procedimento.numero,
            'uuid': str(procedimento.uuid),
            'tipo': procedimento.tipo,
            'tipo_nome': procedimento.get_tipo_display(),
            'situacao': procedimento.get_situacao_display(),
            'assunto': procedimento.assunto if procedimento.assunto else None,
            'data_ultima_movimentacao': procedimento.data_ultima_movimentacao.strftime("%d/%m/%Y %H:%M:%S"),

        })

    return JsonResponse(procedimentos_list, safe=False)


@login_required
def buscar(request):

    if request.method == 'POST':

        numero_registros = 25
        pessoas_lst = None

        filtro = simplejson.loads(request.body)
        filtro_defensoria = filtro.get('defensoria')

        # Converte diferentes tipos de dados em lista para filtro de defensoria
        if isinstance(filtro_defensoria, str) and len(filtro_defensoria):
            filtro['defensoria'] = filtro['defensoria'].split(',')
        elif isinstance(filtro_defensoria, int):
            filtro['defensoria'] = [filtro['defensoria']]
        else:
            filtro['defensoria'] = []

        form = BuscarAtendimentoForm(filtro)

        if form.is_valid():

            atendimentos_lst = AtendimentoDefensor.objects.filter(
                Q(tipo__in=[
                    Atendimento.TIPO_INICIAL,
                    Atendimento.TIPO_RETORNO,
                    Atendimento.TIPO_NUCLEO,
                    Atendimento.TIPO_VISITA,
                    Atendimento.TIPO_ENCAMINHAMENTO
                ]) &
                Q(remarcado=None)
            ).annotate(
                atividades=Sum(Case(When(filhos__ativo=True, filhos__tipo=Atendimento.TIPO_ATIVIDADE, then=Value(1)),
                                    default=Value(0), output_field=IntegerField())),
                tem_apoio=Sum(Case(When(filhos__ativo=True, filhos__tipo=Atendimento.TIPO_NUCLEO, then=Value(1)),
                              default=Value(0), output_field=IntegerField())),
            ).order_by(
                '-data_agendamento',
                '-data_atendimento')

            if filtro.get('filtro'):

                filtro_texto = filtro.get('filtro').strip()
                filtro_numero = re.sub('[^0-9]', '', filtro_texto)

                if len(filtro_numero) == 12:  # Numero do Atendimento

                    atendimentos_lst = atendimentos_lst.filter(numero=filtro_numero)

                elif len(filtro_numero) in [11, 14]:  # Numero do CPF ou CNPJ

                    pessoas_lst = set(
                        AtendimentoPessoa.objects.filter(
                            pessoa__cpf=filtro_numero,
                            ativo=True
                        ).values_list('atendimento_id', flat=True)
                    )

                else:

                    # Tratamento da consulta por nome, nome_social e apelido (nome fantasia para PJ)
                    # Se a consulta for com um nome com a quantidade de caracteres menos do que o mínimo configurado
                    # será retornada uma mensagem de alerta para que o usuário faça filtros mais elaborados
                    if config.BUSCAR_ATENDIMENTOS_FILTRO_NOME_MIN_CARACTERES and len(filtro_texto) < config.BUSCAR_ATENDIMENTOS_FILTRO_NOME_MIN_CARACTERES:  # noqa: E501
                        return JsonResponse({
                            'sucesso': False,
                            'mensagem': 'Erro: Aumente o texto para {} caracter(es) ou mais e tente novamente.'.format(
                                config.BUSCAR_ATENDIMENTOS_FILTRO_NOME_MIN_CARACTERES
                            )
                        })

                    filtro_norm = Util.normalize(filtro_texto)

                    # tratamento da busca por nome, nome_social; e apelido (nome_fantasia) apenas para PJ

                    q_nome = Q(pessoa__nome_norm__istartswith=filtro_norm)

                    # TODO verificar o método Save de Pessoa. Não está mantendo o 'LTDA'.
                    # TODO depois de verificar o método pode retirar o filtro por nome. Utilize apenas o nome_norm
                    if 'LTDA' in filtro_texto:
                        q_nome |= Q(pessoa__nome__istartswith=filtro_texto)

                    # Só busca por nome social caso seja tipo pessoa física
                    q_nome_social = Q(
                        Q(pessoa__tipo=constantes.TIPO_PESSOA_FISICA) &
                        Q(pessoa__nome_social__istartswith=filtro_texto)
                    )

                    # Só busca por nome fantasia (apelido) caso seja tipo pessoa jurídica
                    q_nome_fantasia = Q(
                        Q(pessoa__tipo=constantes.TIPO_PESSOA_JURIDICA) &
                        Q(pessoa__apelido__istartswith=filtro_texto)
                    )

                    q = Q(ativo=True)
                    q &= Q(pessoa__desativado_em=None)
                    q &= Q(q_nome | q_nome_social | q_nome_fantasia)

                    # Só executa o Bloqueio de Maria caso não tenha preenchido nenhum outro filtro
                    if filtro.get('defensoria') or filtro.get('defensor') or form.cleaned_data['data_ini'] or form.cleaned_data['data_fim']:  # noqa: E501
                        pessoas_lst = set(AtendimentoPessoa.objects.filter(q).values_list('atendimento_id', flat=True))
                    else:
                        # Se a consulta retornar uma quantidade acima do limite configurado será retornada uma mensagem
                        # de alerta para que o usuário faça filtros mais elaborados
                        pessoas_count = AtendimentoPessoa.objects.filter(q).count()

                        if config.BUSCAR_ATENDIMENTOS_FILTRO_NOME_MAX_PESSOAS and pessoas_count > config.BUSCAR_ATENDIMENTOS_FILTRO_NOME_MAX_PESSOAS:  # noqa: E501
                            return JsonResponse({
                                'sucesso': False,
                                'mensagem': 'Erro: Seriam retornados atendimentos de mais de {} pessoas. Preencha mais campos e tente novamente.'.format(  # noqa: E501
                                    pessoas_count
                                )
                            })
                        else:
                            pessoas_lst = set(AtendimentoPessoa.objects.filter(q).values_list('atendimento_id', flat=True))  # noqa: E501

                if pessoas_lst is not None:
                    if len(pessoas_lst):
                        atendimentos_lst = atendimentos_lst.filter(
                            (
                                Q(id__in=pessoas_lst) |
                                Q(inicial__in=pessoas_lst)
                            ))
                    else:
                        atendimentos_lst = atendimentos_lst.none()

            if filtro.get('defensoria'):
                q = Q(defensoria_id=filtro.get('defensoria'))
                if type(filtro.get('defensoria')) is list:
                    q = Q(defensoria_id__in=filtro.get('defensoria'))

                atendimentos_lst = atendimentos_lst.filter((q))

            if filtro.get('defensor'):

                defensor = Defensor.objects.filter(id=filtro.get('defensor')).first()

                if defensor.eh_defensor:
                    atendimentos_lst = atendimentos_lst.filter((
                        Q(defensor_id=filtro.get('defensor')) |
                        Q(substituto_id=filtro.get('defensor'))
                    ))
                elif not filtro.get('defensoria'):
                    defensorias = list(defensor.atuacoes(vigentes=True).values_list('defensoria_id', flat=True))
                    atendimentos_lst = atendimentos_lst.filter((
                        Q(defensoria__in=defensorias)
                    ))

            if form.cleaned_data['data_ini']:
                data_ini = form.cleaned_data['data_ini']

                atendimentos_lst = atendimentos_lst.filter((
                    (
                        Q(data_agendamento__gte=data_ini) &
                        Q(data_atendimento=None)
                    ) |
                    Q(data_atendimento__gte=data_ini)
                ))

            if form.cleaned_data['data_fim']:
                data_fim = form.cleaned_data['data_fim']
                data_fim = datetime.combine(data_fim, time.max)

                atendimentos_lst = atendimentos_lst.filter((
                    (
                        Q(data_agendamento__lte=data_fim) &
                        Q(data_atendimento=None)
                    ) |
                    Q(data_atendimento__lte=data_fim)
                ))

            if form.cleaned_data['situacao']:
                situacao = form.cleaned_data['situacao']
                if situacao == BuscarAtendimentoForm.SITUACAO_REALIZADO:
                    atendimentos_lst = atendimentos_lst.filter(
                        Q(ativo=True) &
                        Q(data_atendimento__isnull=False)
                    )
                elif situacao == BuscarAtendimentoForm.SITUACAO_AGENDADO:
                    atendimentos_lst = atendimentos_lst.filter(
                        Q(ativo=True) &
                        Q(data_atendimento=None)
                    )
                elif situacao == BuscarAtendimentoForm.SITUACAO_EXCLUIDO:
                    atendimentos_lst = atendimentos_lst.filter(Q(data_exclusao__isnull=False))
            else:
                atendimentos_lst = atendimentos_lst.filter(Q(ativo=True))

            primeiro = filtro.get('pagina') * numero_registros
            ultimo = primeiro + numero_registros

            if filtro.get('pagina') == 0:
                filtro['total'] = atendimentos_lst.count()
                filtro['paginas'] = math.ceil(float(filtro.get('total')) / numero_registros)

            atendimentos_lst = atendimentos_lst[primeiro:ultimo]

            atendimentos_lst = atendimentos_lst.values(
                'id',
                'inicial_id',
                'numero',
                'data_atendimento',
                'data_agendamento',
                'data_exclusao',
                'tipo',
                'agenda',
                'defensoria__nome',
                'defensoria__codigo',
                'defensoria__comarca',
                'qualificacao__titulo',
                'qualificacao__area__nome',
                'defensor__servidor__nome',
                'defensor__servidor__usuario__username',
                'responsavel__servidor__papel__nome',
                'responsavel__servidor__papel__css_label_class',
                'responsavel__servidor__nome',
                'substituto__servidor__nome',
                'substituto__servidor__usuario__username',
                'atividades',
                'tem_apoio',
                'tipo_motivo_exclusao_id'
            )

            atendimentos = []
            for atendimento in atendimentos_lst:

                inicial = atendimento['inicial_id'] if atendimento['inicial_id'] else atendimento['id']

                pessoas = AtendimentoPessoa.objects.filter(
                    atendimento=inicial,
                    ativo=True
                ).values('pessoa_id',
                         'pessoa__nome',
                         'pessoa__nome_social',
                         'pessoa__apelido',
                         'pessoa__tipo',
                         'tipo',
                         'responsavel',
                         )

                atendimento['pessoas'] = list(pessoas)
                atendimento['extra'] = (atendimento['data_agendamento'] and atendimento['data_agendamento'].time() == time())  # noqa: E501
                atendimento['apoio'] = (atendimento['tipo'] == Atendimento.TIPO_NUCLEO)

                # Hack para diferenciar 'retorno' do 'pedido de apoio'
                if atendimento['tem_apoio']:
                    atendimento['tipo'] = Atendimento.TIPO_NUCLEO_PEDIDO

                atendimento['pode_editar'] = False
                atendimento['pode_excluir'] = False

                if request.user.has_perm('atendimento.change_all_agendamentos') or (
                   request.user.has_perm('atendimento.view_recepcao') and
                   int(request.session.get('comarca', request.user.servidor.comarca_id)) == atendimento['defensoria__comarca']):  # noqa: E501

                    atendimento['pode_editar'] = atendimento['data_exclusao'] is None

                    # TODO: Usar método Atendimento.pode_excluir()
                    if atendimento['data_exclusao'] is None and not (atendimento['atividades'] or atendimento['apoio'] or (atendimento['data_atendimento'] and not request.user.is_superuser)):  # noqa: E501
                        atendimento['pode_excluir'] = True

                atendimentos.append(atendimento)

        else:

            atendimentos = []

        categorias_de_agendas = {}
        for categoria_agenda in Categoria.objects.all().values('id', 'nome'):
            categorias_de_agendas[categoria_agenda['id']] = categoria_agenda['nome']

        # Verifica que o recurso de arquivar/desarquivar atendimentos está habilitado antes de analisar o status
        if arquivamento_esta_habilitado() and atendimentos:
            # TODO verificar possibilidade de refatorar o status arquivado de property
            # para uma coluna física a fim de otimizar as consultas
            atendimentos_numero = map(lambda atendimento: atendimento["numero"], atendimentos)
            status_atendimentos = consulta_status_arquivado(atendimentos_numero)
            for atendimento in atendimentos:
                atendimento["arquivado"] = status_atendimentos[atendimento["numero"]]

        return JsonResponse(
            {
                'usuario': {
                    'comarca': int(request.session.get('comarca', request.user.servidor.comarca_id)),
                    'perms': {
                        'atendimento_view_recepcao': request.user.has_perm('atendimento.view_recepcao')
                    }
                },
                'atendimentos': atendimentos,
                'pagina': filtro.get('pagina'),
                'paginas': filtro.get('paginas', 0),
                'ultima': filtro.get('pagina') == filtro.get('paginas') - 1 if filtro.get('paginas') else True,
                'total': filtro.get('total'),
                'LISTA': {
                    'TIPO': dict(Atendimento.LISTA_TIPO),
                    'AGENDA': categorias_de_agendas,
                },
                'sucesso': True
            }, safe=False)

    prev = request.path
    prev_params = simplejson.dumps(dict(request.GET.items()))

    exibir_nome_da_defensoria = config.EXIBIR_NOME_DA_DEFENSORIA_NA_BUSCA_ATENDIMENTOS

    form = BuscarAtendimentoForm(request.GET)
    angular = 'BuscarCtrl'

    return render(request=request, template_name="atendimento/buscar.html", context=locals())


@login_required
def cronometro(request, atendimento_numero=None):
    cronometro = None

    if atendimento_numero:
        atendimento = Atendimento.objects.filter(numero=atendimento_numero).first()
        if atendimento:
            with transaction.atomic():
                cronometro = Cronometro.objects.filter(
                    atendimento=atendimento,
                    servidor=request.user.servidor,
                    finalizado=False).first()
                if not cronometro:
                    cronometro = Cronometro(
                        atendimento=atendimento,
                        servidor=request.user.servidor,
                        finalizado=False)
                    cronometro.save()
    elif request.session.get('ligacao_id'):
        cronometro = Cronometro.objects.filter(atendimento_id=request.session.get('ligacao_id')).first()

    if cronometro:
        cronometro.atualizar()
        return JsonResponse({'id': cronometro.id, 'duracao': cronometro.duracao, 'expirado': cronometro.expirado()})
    else:
        return JsonResponse({'erro': True, 'expirado': True})


@login_required
def distribuir(request):

    if request.method == 'POST' and request.is_ajax():

        atuacoes = None
        assessores = None
        atendimentos = None

        try:
            dados = simplejson.loads(request.body)
        except ValueError:
            dados = None

        form = DistribuirAtendimentoForm(request.user, dados)

        if form.is_valid():

            data_ini = form.cleaned_data['data_ini']
            data_fim = datetime.combine(data_ini, time.max)
            defensor = form.cleaned_data['defensor']
            defensoria = form.cleaned_data['defensoria']
            forma_atendimento = form.cleaned_data['forma_atendimento']

            assessores = []
            atendimentos = []
            atuacoes = []

            # Obtém lista de todos agendamentos da defensoria para o dia
            atendimentos_lst = AtendimentoDefensor.objects.select_related(
                'defensoria',
                'defensor',
                'substituto',
                'qualificacao',
                'qualificacao__area',
                'agenda',
                'forma_atendimento',
            ).filter(
                Q(ativo=True) &
                Q(remarcado=None) &
                Q(defensoria=defensoria) &
                Q(defensoria__nucleo__supervisionado=True) &
                (
                    (
                        Q(data_agendamento__gte=data_ini) &
                        Q(data_agendamento__lte=data_fim)
                    )
                )
            ).order_by('data_agendamento', 'data_atendimento')

            # Se informado, filtra agendamentos pelo defensor
            if defensor:
                atendimentos_lst = atendimentos_lst.filter(
                    (
                        Q(defensor=defensor) |
                        Q(substituto=defensor)
                    )
                )

            # Se informado, filtra agendamentos pela forma de atendimento
            if forma_atendimento:
                atendimentos_lst = atendimentos_lst.filter(
                    forma_atendimento__presencial=(forma_atendimento == FormaAtendimento.TIPO_PRESENCIAL)
                )

            # Transforma dados
            for atendimento in atendimentos_lst:

                forma_atendimento = None
                if config.EXIBIR_PRESENCIAL_REMOTO_AGENDAMENTO and atendimento.forma_atendimento:
                    forma_atendimento = 'P' if atendimento.forma_atendimento.presencial else 'R'

                pre_responsavel = atendimento.responsavel_id

                if not pre_responsavel and not atendimento.realizado and atendimento.inicial:
                    # Obtém ultimo atendimento de retorno realizado
                    ultimo_retorno = AtendimentoDefensor.objects.ultimos_validos().filter(
                        inicial=atendimento.inicial,
                        data_atendimento__isnull=False
                    ).first()
                    # Se não existe, usa o atendimento inicial como referência
                    if not ultimo_retorno:
                        ultimo_retorno = atendimento.inicial
                    # Define o servidor que atendeu como responsável pelo novo atendimento
                    if ultimo_retorno.atendido_por:
                        pre_responsavel = ultimo_retorno.atendido_por.defensor.id
                    else:
                        pre_responsavel = ultimo_retorno.responsavel_id

                atendimentos.append({
                    'id': atendimento.id,
                    'numero': atendimento.numero,
                    'tipo': atendimento.LISTA_TIPO[atendimento.tipo][1],
                    'data_agendamento': atendimento.data_agendamento.strftime('%Y-%m-%dT%H:%M:00-03:00'),
                    'extra': atendimento.extra,
                    'requerente': atendimento.requerente.pessoa.nome if atendimento.requerente else None,
                    'requerente_hipossuficiente': atendimento.requerente.pessoa.avaliar() if atendimento.requerente else False,  # noqa: E501
                    'requerido': atendimento.requerido.pessoa.nome if atendimento.requerido else None,
                    'defensoria': {'id': atendimento.defensoria.id, 'nome': atendimento.defensoria.nome},
                    'defensor': atendimento.substituto_id if atendimento.substituto_id else atendimento.defensor_id,
                    'area': atendimento.qualificacao.area.nome,
                    'pedido': atendimento.qualificacao.titulo,
                    'responsavel': atendimento.responsavel_id,
                    'pre_responsavel': pre_responsavel,
                    'agenda': {'id': atendimento.agenda.id, 'nome': atendimento.agenda.nome},
                    'forma_atendimento': forma_atendimento,
                    'realizado': atendimento.realizado,
                })

            # Obtém a lista de todos defensores/assessores lotados na defensoria
            for atuacao in Atuacao.objects.parcialmente_vigentes(inicio=data_ini).filter(defensoria=defensoria):

                assessores.append({
                    'id': atuacao.defensor.id,
                    'nome': atuacao.defensor.nome
                })

                if atuacao.defensor.eh_defensor:
                    atuacoes.append({
                        'id': atuacao.id,
                        'tipo': atuacao.tipo,
                        'defensoria': {'id': atuacao.defensoria.id, 'nome': atuacao.defensoria.nome},
                        'defensor': {'id': atuacao.defensor.id, 'nome': atuacao.defensor.nome},
                    })

        return JsonResponse({
            'atuacoes': atuacoes,
            'assessores': assessores,
            'atendimentos': atendimentos
        })

    else:

        form = DistribuirAtendimentoForm(request.user, initial={
            'data_ini': date.today(),
            'defensoria': request.user.servidor.defensor.defensorias.filter(nucleo__supervisionado=True).first()
        })

    angular = 'DistribuicaoCtrl'

    return render(request=request, template_name="atendimento/distribuir.html", context=locals())


@login_required
def distribuir_salvar(request):
    dados = simplejson.loads(request.body)

    for item in dados:
        AtendimentoDefensor.objects.filter(id=item['id']).update(
            responsavel=item['pre_responsavel'],
            distribuido_por=request.user.servidor,
            data_distribuido=datetime.now())

    return JsonResponse({'success': True})


@login_required
@permission_required('atendimento.delete_atendimento')
@reversion.create_revision(atomic=False)
def excluir(request, atendimento_numero=None):

    if not atendimento_numero:
        atendimento_numero = request.POST.get('atendimento')

    atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero)
    atendimento.excluir(
        excluido_por=request.user.servidor,
        data_exclusao=datetime.now(),
        motivo_exclusao=request.POST.get('motivo_exclusao', '').replace('\r\n', '\n'),
        tipo_motivo_exclusao_id=request.POST.get('tipo_motivo_exclusao')
    )

    reversion.set_user(request.user)
    reversion.set_comment(Util.get_comment_delete(request.user, atendimento))

    messages.success(request, u'Atendimento excluído.')

    # Se existe um atendimento para processo vinculado, transfere dados de volta
    try:
        atendimento_processo = AtendimentoDefensor.objects.get(
            inicial=atendimento,
            tipo=Atendimento.TIPO_PROCESSO,
            ativo=True
        )
    except ObjectDoesNotExist:
        atendimento_processo = None

    if atendimento_processo:

        service = AtendimentoService(atendimento)
        service.transferir_relacionamentos(
            atendimento_destino=atendimento_processo,
            transferir_filhos=False,
            transferir_documentos=False
        )

        atendimento_processo.inicial = None
        atendimento_processo.save()

    # Se for pré-agendamento no Painel do CRC, notifica assistido
    if atendimento.tipo == Atendimento.TIPO_LIGACAO:
        # Notifica assistido via chatbot Luna
        chatbot_notificar_requerente_exclusao.apply_async(
            kwargs={'numero': atendimento.numero},
            queue='sobdemanda'
        )
        # Notifica assistido via SMS
        if (config.USAR_SMS and config.SERVICO_SMS_DISPONIVEL):
            envia_sms_exclusao(request, atendimento, config.MENSAGEM_SMS_AGENDAMENTO_EXCLUSAO)
        # Notifica assistido via Email
        if (config.USAR_EMAIL):
            envia_email_exclusao(request, atendimento, config.MENSAGEM_EMAIL_AGENDAMENTO_EXCLUSAO)

    # Se atividade, redireciona para aba 'Atividades' do atendimento que a originou
    if atendimento.tipo == Atendimento.TIPO_ATIVIDADE and not request.GET.get('next'):
        return redirect('{}#/atividades'.format(reverse('atendimento_atender', args=[atendimento.origem.numero])))

    # Se next informado, inclui demais parametros e redireciona
    if request.GET.get('next'):
        params = request.GET['next']
        for param in request.GET:
            if param != 'next':
                params += "&%s=%s" % (param, request.GET[param])
        return redirect(params)
    else:
        return JsonResponse({'success': True})


@login_required
@permission_required('atendimento.delete_documento')
def excluir_documento(request, atendimento_numero=None):

    success = False
    mensagem = None

    if request.method == 'POST':

        if request.is_ajax():
            dados = simplejson.loads(request.body)
        else:
            dados = request.POST

        try:
            usuario = request.user
            documento = AtendimentoDocumento.objects.get(id=dados['id'], ativo=True)
            documento.excluir(excluido_por=usuario.servidor, agora=datetime.now())
        except Exception:
            mensagem = u'Erro ao excluir: O documento não existe!'
        else:
            mensagem = u'Documento excluído!'
            success = True

    if request.is_ajax():
        return JsonResponse({'success': success, 'mensagem': mensagem})
    else:
        if success:
            messages.success(request, mensagem)
        else:
            messages.error(request, mensagem)
        return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@permission_required('atendimento.delete_tarefa')
def excluir_tarefa(request, atendimento_numero):
    if request.method == 'POST':

        dados = simplejson.loads(request.body)
        success = True

        try:
            tarefa = Tarefa.objects.get(id=dados['id'], ativo=True, finalizado=None)
            tarefa.excluir(excluido_por=request.user.servidor)
        except Exception:
            success = False

        return JsonResponse({'success': success})

    return JsonResponse({'success': False})


@login_required
@permission_required('atendimento.change_tarefa')
def finalizar_tarefa(request, atendimento_numero):
    if request.method == 'POST':

        success = True
        dados = simplejson.loads(request.body)

        try:

            tarefa = Tarefa.objects.get(id=dados['id'], ativo=True, finalizado=None)
            tarefa.finalizar(request.user.servidor)

            if tarefa.tarefa_oficio:
                atendimento = tarefa.atendimento
                AtendimentoDefensor.objects.create(
                    origem=atendimento,
                    inicial=atendimento.at_inicial,
                    cadastrado_por=request.user.servidor,
                    atendido_por=request.user.servidor,
                    data_atendimento=datetime.now(),
                    tipo=AtendimentoDefensor.TIPO_OFICIO_FINALIZADO,
                    oficio=atendimento.oficio,
                    detalhes=atendimento.detalhes
                )

        except ObjectDoesNotExist:

            success = False

        return JsonResponse({'success': success, 'atendimento': atendimento_numero, 'id': dados['id']})

    return JsonResponse({'success': False})


@login_required
def remeter_atendimento(request, atendimento_numero):
    if request.method == 'POST':

        dados = simplejson.loads(request.body)
        success = True
        try:
            agora = timezone.now()
            servidor = request.user.servidor
            atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero)
            setor_responsavel = Defensoria.objects.get(id=dados['defensoria_destino_id'])

            # Cria anotação
            AtendimentoDefensor.objects.create(
                tipo=AtendimentoDefensor.TIPO_ANOTACAO,
                data_agendamento=agora,
                data_atendimento=agora,
                cadastrado_por=servidor,
                agendado_por=servidor,
                atendido_por=servidor,
                inicial_id=dados['atendimento_id'],
                origem_id=dados['atendimento_id'],
                defensor_id=dados['defensor_destino_id'],
                defensoria_id=dados['defensoria_destino_id'],
                qualificacao_id=dados['qualificacao_id'],
                historico=dados['historico'],
            )

            # cria cooperação com o remetimento
            Tarefa.objects.create(
                atendimento=atendimento.at_inicial,
                resposta_para=setor_responsavel,
                setor_responsavel=atendimento.defensoria,
                titulo='REMETIMENTO DE ATENDIMENTO',
                descricao="Cooperação gerada automaticamente após atendimento ser remetido de " + atendimento.defensoria.nome + " para " + setor_responsavel.nome,  # noqa: E501
                data_inicial=date.today(),
                data_final=None,
                prioridade=Tarefa.PRIORIDADE_COOPERACAO,
                cadastrado_por=request.user.servidor
            )

        except Exception:
            success = False

        return JsonResponse({'success': success})

    return JsonResponse({'success': False})


class BuscarTarefas(ListView):
    queryset = Tarefa.objects.select_related(
        'atendimento__defensor__defensoria',
        'setor_responsavel',
        'responsavel__usuario',
        'cadastrado_por__usuario',
    ).annotate(
        respondido_por=F('all_respostas__finalizado__nome'),
        respondido_por_username=F('all_respostas__finalizado__usuario__username'),
    ).filter(
        (
            Q(origem=None) &
            Q(atendimento__ativo=True) &
            ~Q(
                Q(titulo='Solicitação de Apoio Respondida') &
                Q(responsavel=None) &
                Q(data_inicial=None) &
                Q(data_final=None)
            )
        ) &
        (
            (
                Q(atendimento__partes__tipo=AtendimentoPessoa.TIPO_REQUERENTE) &
                Q(atendimento__partes__responsavel=True) &
                Q(atendimento__partes__ativo=True)
            ) |
            (
                Q(atendimento__inicial__partes__tipo=AtendimentoPessoa.TIPO_REQUERENTE) &
                Q(atendimento__inicial__partes__responsavel=True) &
                Q(atendimento__inicial__partes__ativo=True)
            )
        ) &
        (
            Q(all_respostas=None) |
            (
                ~Q(all_respostas__finalizado=None) &
                Q(all_respostas__ativo=True)
            )
        )
    ).order_by(
        'data_inicial', 'prioridade', 'data_final', 'id', '-all_respostas__id'
    ).distinct(
        'data_inicial', 'prioridade', 'data_final', 'id'
    )
    model = Tarefa
    paginate_by = 50
    template_name = "atendimento/tarefa/buscar.html"

    def get_context_data(self, **kwargs):

        context = super(BuscarTarefas, self).get_context_data(**kwargs)

        context.update({
            'form': self.get_form(),
            'ordering': swap_ordenacao_tarefas(self.request.GET.get('ordering', 'data_final'))
        })

        return context

    def get_queryset(self):

        queryset = super(BuscarTarefas, self).get_queryset()
        q = Q()

        # Obtém lista de defensorias do usuário
        defensorias = set(self.request.user.servidor.defensor.defensorias.values_list('id', flat=True))

        # Configuração para exibir ou não as cooperações cumpridas
        if not config.EXIBIR_COOPERACOES_CUMPRIDAS_PARA_RESPONSAVEL:
            q &= ~Q(
                Q(prioridade=Tarefa.PRIORIDADE_COOPERACAO) &
                Q(status=Tarefa.STATUS_CUMPRIDO) &
                Q(setor_responsavel__in=defensorias)
            )

        # Se usuário não tem permissão para ver todos atendimentos, restringe informações de acordo com suas lotações
        if not self.request.user.has_perm(perm='atendimento.view_all_atendimentos'):
            q &= Q(setor_responsavel__in=defensorias)

        tarefas_propac = get_tarefas_propac()

        form = self.get_form()

        # Só filtra se valores de busca forem válidos
        if form.is_valid():

            data = form.cleaned_data

            filtros_tarefas = filtra_tarefas(data)
            q &= filtros_tarefas

            tarefas_propac = tarefas_propac.filter(filtros_tarefas)

        queryset = queryset.filter(q)

        if tarefas_propac:
            queryset = queryset | tarefas_propac
            queryset = queryset.order_by('data_inicial', 'prioridade', 'data_final', 'id')

        return queryset

    def get_ordering(self):
        return self.request.GET.get('ordering', 'data_final')

    def get_form(self):

        form_initial = self.request.GET.copy()

        if config.PRE_FILTRAR_TAREFAS_USUARIO_LOGADO and 'responsavel' not in form_initial and self.request.user.servidor.defensor:  # noqa: E501
            form_initial['responsavel'] = self.request.user.servidor.defensor.id

        return BuscarTarefaForm(form_initial, usuario=self.request.user)


class FinalizarTarefas(View):
    def post(self, request, *args, **kwargs):

        # obtém lista de tarefas marcadas
        tarefas = Tarefa.objects.filter(
            id__in=request.POST.getlist('id')
        )

        agora = timezone.now()
        tarefas_finalizadas = 0
        tarefas_nao_finalizadas = 0

        # passa em cada registro, verificando permissão para finaliza
        for tarefa in tarefas:
            if tarefa.pode_finalizar(request.user):
                tarefa.finalizar(
                    servidor=request.user.servidor,
                    data_finalizado=agora
                )
                tarefas_finalizadas += 1
            else:
                tarefas_nao_finalizadas += 1

        if tarefas_finalizadas:
            messages.success(request, '{} tarefas foram finalizadas!'.format(
                tarefas_finalizadas
            ))

        if tarefas_nao_finalizadas:
            messages.error(request, '{} tarefas não puderam ser finalizadas!'.format(
                tarefas_nao_finalizadas
            ))

        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', '/'))


@login_required
def visualizar_tarefa(request, tarefa_id):

    success = True
    message = None

    try:

        tarefa = Tarefa.objects.get(id=tarefa_id, ativo=True)

        if request.user.is_superuser and not config.REGISTRAR_VISUALIZACAO_TAREFA_SUPERUSUARIO:
            message = 'Visualização não registrada (superusuário)'
        elif tarefa.cadastrado_por and tarefa.cadastrado_por.usuario_id == request.user.id:
            message = 'Visualização não registrada (cadastrante)'
        else:
            TarefaVisualizacao.objects.get_or_create(
                tarefa=tarefa,
                visualizada_por=request.user.servidor
            )
            message = 'Visualização registrada'

    except ObjectDoesNotExist:
        message = 'Tarefa não existe'
        success = False

    return JsonResponse({
        'id': tarefa_id,
        'success': success,
        'message': message
    })


@login_required
def get_tarefa(request, tarefa_id):

    resposta = {}

    try:

        tarefa = Tarefa.objects.get(id=tarefa_id, ativo=True)
        resposta = Util.object_to_dict(tarefa, {})

        resposta['visualizacoes'] = []
        visualizacoes = tarefa.visualizacoes.all().values('visualizada_em', 'visualizada_por__nome')

        for v in visualizacoes:
            resposta['visualizacoes'].append({
                'visualizada_em': v['visualizada_em'].strftime('%Y-%m-%dT%H:%M:%S-03:00'),
                'visualizada_por': v['visualizada_por__nome']
            })

    except ObjectDoesNotExist:
        pass

    return JsonResponse(resposta)


@never_cache
@login_required
def get_json(request, atendimento_numero):

    a = get_object_or_404(
        AtendimentoDefensor.objects.select_related(
            'qualificacao__area',
            'qualificacao__especializado',
            'comarca',
            'defensoria',
            'defensor__servidor',
            'substituto__servidor',
            'nucleo',
            'modificado_por',
            'agendado_por',
            'atendido_por',
            'tipo_motivo_exclusao'
        ),
        numero=atendimento_numero
    )

    requerente = None
    requentes = []

    requerido_nome = None
    requeridos = []

    for pessoa in a.pessoas.values('pessoa_id', 'pessoa__nome', 'responsavel', 'tipo'):

        assistido = {
            'id': pessoa['pessoa_id'],
            'nome': pessoa['pessoa__nome']
        }

        if pessoa['tipo'] == AtendimentoPessoa.TIPO_REQUERENTE:
            if pessoa['responsavel']:
                requerente = assistido
            requentes.append(assistido)
        else:
            if pessoa['responsavel']:
                requerido_nome = assistido['nome']
            requeridos.append(assistido)

    resposta = {
        'id': a.id,
        'numero': a.numero,
        'tipo': a.LISTA_TIPO[a.tipo][1],
        'tipo_id': a.tipo,
        'requerente': requerente['nome'] if requerente else None,
        'requerentes': requentes,
        'requerido': requerido_nome,
        'requeridos': requeridos,
        'area': a.qualificacao.area.nome if a.qualificacao else None,
        'pedido': a.qualificacao.titulo if a.qualificacao else None,
        'nucleo': a.nucleo.nome if a.nucleo else None,
        'especializado': a.qualificacao.especializado.nome if a.qualificacao and a.qualificacao.especializado else None,
        'horario': a.data_agendamento.time().strftime('%H:%M') if a.data_agendamento else None,
        'horario_atendimento': a.data_atendimento.time().strftime('%H:%M') if a.data_atendimento else None,
        'atrasado': a.atrasado,
        'historico_recepcao': 1 if a.recepcao else 0,
        'historico_atendimento': 1 if a.historico else 0,
        'comarca': a.comarca.nome if a.comarca else None,
        'defensoria': a.defensoria.nome if a.defensoria else None,
        'defensor': a.defensor.nome if a.defensor else None,
        'substituto': a.substituto.nome if a.substituto else None,
        'id_comarca': a.comarca.id if a.comarca else None,
        'guiche': 0,
        'agendado_por': a.agendado_por.nome if a.agendado_por else None,
        'data_agendado': a.data_cadastro.strftime('%Y-%m-%dT%H:%M:00-03:00'),
        'cadastrado_por': a.recepcao.atendido_por.nome if a.recepcao else None,
        'data_cadastro': a.recepcao.data_atendimento.strftime('%Y-%m-%dT%H:%M:00-03:00') if a.recepcao else None,
        'modificado_por': a.modificado_por.nome if a.modificado_por else None,
        'data_modificacao': a.data_modificacao.strftime('%Y-%m-%dT%H:%M:00-03:00') if a.data_modificacao else None,
        'atendido_por': a.atendido_por.nome if a.atendido_por else None,
        'data_atendimento': a.data_atendimento.strftime('%Y-%m-%dT%H:%M:00-03:00') if a.data_atendimento else None,
        'agenda': a.agenda.nome,
        'extra': a.extra,
        'remarcado': a.qtd_remarcado,
        'telefones': Util.json_serialize(Telefone.objects.filter(pessoa=requerente['id']) if requerente else []),
        'pode_excluir': a.pode_excluir(usuario=request.user),
        'motivo_exclusao': a.motivo_exclusao,
        'motivo_exclusao_nome': a.tipo_motivo_exclusao.nome if a.tipo_motivo_exclusao else None,
        'motivos_exclusao': list(MotivoExclusao.objects.ativos().values('id', 'nome'))
    }

    return JsonResponse(resposta)


@never_cache
@login_required
def get_json_permissao_atendimento_botoes(request, atendimento_numero):
    """Utilizado para o tratamento de renderização dos botões das ações da Ficha de Atendimento.
        Botão de anotação, apoio operacional e agendar.
    """

    sucesso = True
    atendimento = AtendimentoDefensor.objects.filter(numero=atendimento_numero, ativo=True, remarcado=None).first()

    pode_agendar = False
    pode_solicitar_apoio = False
    pode_cadastrar_anotacao = False
    pode_cadastrar_visita_ao_preso = False

    retorno_pendente = False

    if atendimento:

        if (verifica_permissao_editar(request.user, atendimento) or
           atendimento.permissao_acessar(usuario=request.user) or
           atendimento.acesso_concedido(defensor=request.user.servidor.defensor)):

            if atendimento.realizado:

                # não tem retorno pendente
                if not atendimento.retornos_pendentes:
                    pode_agendar = True
                else:
                    retorno_pendente = True

            if not atendimento.tipo == atendimento.TIPO_NUCLEO:
                pode_solicitar_apoio = True

            if atendimento.realizado or config.REGISTRAR_ANOTACAO_EM_AGENDAMENTO:
                pode_cadastrar_anotacao = True

            if atendimento.requerente:
                prisoes = Prisao.objects.filter(
                    pessoa=atendimento.requerente.pessoa,
                    ativo=True
                ).exists()

                if prisoes:
                    pode_cadastrar_visita_ao_preso = True

    else:
        sucesso = False

    permissao_botoes_acoes = {
        'retorno_pendente': retorno_pendente,
        'pode_agendar': pode_agendar,
        'pode_solicitar_apoio': pode_solicitar_apoio,
        'pode_cadastrar_anotacao': pode_cadastrar_anotacao,
        'pode_cadastrar_visita_ao_preso': pode_cadastrar_visita_ao_preso
    }

    return JsonResponse({
        'sucesso': sucesso,
        'permissao_botoes': permissao_botoes_acoes
    })


@never_cache
@login_required
def get_json_pessoas(request, atendimento_numero, tipo):
    """Utilizado para buscar Requerentes e Requeridos via json"""

    atendimento = AtendimentoDefensor.objects.filter(numero=atendimento_numero).first()

    if atendimento:

        pessoas_dict = []
        interessado = None
        eh_requerente = True

        if int(tipo) == AtendimentoPessoa.TIPO_REQUERENTE:
            pessoas = atendimento.get_requerentes()
            tipo = 'requerentes'

            if hasattr(atendimento, 'atendimento'):
                interessado = atendimento.atendimento.interessado_id

        else:
            pessoas = atendimento.get_requeridos()
            tipo = 'requeridos'
            eh_requerente = False

        for pessoa in pessoas:
            filiacao = []

            for f in pessoa.pessoa.filiacoes.all():
                filiacao.append({'nome': f.nome})

            # busca a foto da pessoa
            from assistido.models import PessoaAssistida
            foto = PessoaAssistida.objects.filter(id=pessoa.pessoa.id).first().get_foto()

            # verifica se a pessoa esta presa
            from nucleo.nadep.models import Aprisionamento
            preso = Aprisionamento.objects.filter(prisao__pessoa=pessoa.pessoa, data_final=None, ativo=True).exists(),

            pessoas_dict.append({
                'pessoa_id': pessoa.pessoa.id,
                'nome': pessoa.pessoa.nome,
                'nome_tratado': pessoa.pessoa.nome_tratado,
                'possui_nome_social': pessoa.pessoa.possui_nome_social(),
                'possui_nome_fantasia': pessoa.pessoa.possui_nome_fantasia(),
                'eh_pessoa_fisica': pessoa.pessoa.eh_pessoa_fisica,
                'cpf': pessoa.pessoa.cpf,
                'data_nascimento': pessoa.pessoa.data_nascimento,
                'idade': pessoa.pessoa.idade,
                'idoso': pessoa.pessoa.idoso,
                'pne': pessoa.pessoa.pne,
                'responsavel': pessoa.responsavel,
                'interessado': pessoa.pessoa.id == interessado,
                'preso': preso[0],
                'eh_requerente': eh_requerente,
                'eh_requerido': not eh_requerente,
                'filiacao': filiacao,
                'foto': foto
            })

        return JsonResponse({tipo: pessoas_dict})

    return JsonResponse({'mensagem': 'Atendimento não encontrado.'})


@never_cache
@login_required
def get_json_documentos(request, atendimento_numero):
    """Busca os documentos do atendimento"""

    documentos = AtendimentoDefensor.objects.filter(
        numero=atendimento_numero
    ).first().documentos.select_related(
        'documento_online',
        'cadastrado_por__usuario',
        'enviado_por__usuario',
    )

    documentos_list = []

    for documento in documentos:
        documentos_list.append({
            'id': documento.id,
            'nome': documento.nome,
            'arquivo': documento.arquivo.url if documento.arquivo else '',
            'data_cadastro': documento.data_cadastro,
            'cadastrado_por_nome': documento.cadastrado_por.nome if documento.cadastrado_por else None,
            'cadastrado_por_username': documento.cadastrado_por.usuario.username if documento.cadastrado_por else None,
            'data_enviado': documento.data_enviado,
            'enviado_por_nome': documento.enviado_por.nome if documento.enviado_por else None,
            'enviado_por_username': documento.enviado_por.usuario.username if documento.enviado_por else None,
            'documento_online': {
                'id': documento.documento_online_id,
                'assunto': documento.documento_online.assunto,
                'identificador_versao': documento.documento_online.identificador_versao
            } if documento.documento_online else None,
            'pendente': documento.pendente,
        })

    return JsonResponse({'documentos': documentos_list})


@never_cache
@login_required
def get_arvore_json(request, atendimento_numero):
    inicial = AtendimentoDefensor.objects.filter(numero=atendimento_numero).first()

    if inicial:

        resposta = {'success': True, 'remarcar': None, 'retornos': [], 'processos': []}

        retornos = inicial.retornos.values(
            'id',
            'numero',
            'data_cadastro',
            'data_agendamento',
            'data_atendimento',
            'defensor__servidor__nome',
            'defensoria__nome',
            'nucleo__nome',
            'qualificacao__titulo',
            'qualificacao__area__nome',
            'tipo',
            'cadastrado_por__nome',
            'historico_recepcao',
            'historico',
        ).exclude(
            tipo=Atendimento.TIPO_NUCLEO
        ).order_by(
            'data_atendimento', 'data_agendamento'
        )

        for retorno in retornos:

            if not retorno['data_atendimento']:
                resposta['remarcar'] = retorno['numero']

            resposta['retornos'].append({
                'numero': retorno['numero'],
                'data_cadastro': retorno['data_cadastro'],
                'data_agendamento': retorno['data_agendamento'],
                'data_atendimento': retorno['data_atendimento'],
                'defensor': retorno['defensor__servidor__nome'],
                'defensoria': retorno['defensoria__nome'],
                'nucleo': retorno['nucleo__nome'],
                'qualificacao': retorno['qualificacao__titulo'],
                'area': retorno['qualificacao__area__nome'],
                'tipo': dict(Atendimento.LISTA_TIPO)[retorno['tipo']],
                'cadastrado_por': retorno['cadastrado_por__nome'],
                'historico_agendamento': retorno['historico_recepcao'],
                'historico_defensor': retorno['historico'],
                'recepcao': None,
                'arquivado': inicial.arquivado,
            })

            resposta['retornos'][-1]['recepcao'] = Atendimento.objects.filter(
                origem=retorno['id'], tipo=Atendimento.TIPO_RECEPCAO, ativo=True
            ).values('data_atendimento', 'atendido_por__nome', 'historico').first()

        processos = inicial.get_processos().values(
            'numero_puro',
            'numero',
            'chave',
            'grau',
            'tipo',
        )

        resposta['processos'] = list(processos)

        return JsonResponse(resposta)

    else:

        return JsonResponse({'success': False})


@login_required
@permission_required('atendimento.view_defensor')
def index(request):
    if hasattr(request.user.servidor, 'defensor'):
        defensor = request.user.servidor.defensor
    else:
        raise Http404

    if request.session.get('comarca'):
        comarca = Comarca.objects.get(id=request.session['comarca'])
    else:
        comarca = request.user.servidor.comarca.id

    nucleo = request.session.get('nucleo')
    pode_cadastrar_atividade_extraordinaria = False

    try:
        inicio = datetime.strptime(request.POST['data_atendimento'], '%d/%m/%Y')
    except KeyError:
        inicio = datetime.now()

    atuacoes = Atuacao.objects.filter(defensor=defensor)

    # Se hoje, obtém atuações vigentes
    if inicio.date() == date.today():
        atuacoes = atuacoes.vigentes(inicio=inicio, ajustar_horario=False)
    # Se outro dia, obtém atuações parcialmente vigentes no dia
    else:
        atuacoes = atuacoes.parcialmente_vigentes(inicio=inicio)

    # Se núcleo, filtra atuações do núcleo, senão, filtra atuações sem núcleo vinculado
    if nucleo:
        atuacoes = atuacoes.filter(defensoria__nucleo=nucleo)
    else:
        atuacoes = atuacoes.filter(defensoria__nucleo__isnull=True)

    pode_cadastrar_atividade_extraordinaria = atuacoes.filter(
        defensoria__pode_cadastrar_atividade_extraordinaria=True
    ).exists()

    ids_defensoria_atuacoes = list(set(atuacoes.values_list('defensoria_id', flat=True)))
    processos_cadastrados = ParteProcesso.objects.filter(
        (
            (
                Q(defensoria__in=ids_defensoria_atuacoes) & Q(defensoria__nucleo=nucleo)
            ) |
            (
                Q(defensoria_cadastro__in=ids_defensoria_atuacoes) & Q(defensoria_cadastro__nucleo=nucleo)
            )
        ) &
        Q(ativo=True) &
        ~Q(atendimento=None) &
        Q(data_cadastro__gte=(datetime.now().date() - timedelta(days=30)))
    ).order_by('-data_cadastro')

    processos_movimentados = ParteProcesso.objects.filter(
        (
            (
                Q(defensoria__in=ids_defensoria_atuacoes) & Q(defensoria__nucleo=nucleo)
            ) |
            (
                Q(defensoria_cadastro__in=ids_defensoria_atuacoes) & Q(defensoria_cadastro__nucleo=nucleo)
            )
        ) &
        Q(ativo=True) &
        ~Q(atendimento=None) &
        Q(processo__ultima_consulta__gte=(datetime.now().date() - timedelta(days=30)))
    ).order_by('-processo__ultima_consulta')

    sistemas_webservices_procapi = []

    if config.ATIVAR_PROCAPI:
        from procapi_client.services import APISistema
        sistemas_webservices_procapi = APISistema().listar_todos()

    return render(
        request=request,
        template_name="atendimento/index.html",
        context={
            'usuario': request.user,
            'defensor_id': defensor.id,
            'defensor': defensor,
            'comarca': comarca,
            'nucleo': nucleo,
            'inicio': inicio,
            'ids_defensoria_atuacoes': ids_defensoria_atuacoes,
            'processos_cadastrados': processos_cadastrados,
            'processos_movimentados': processos_movimentados,
            'angular': 'AtendimentoIndexCtrl',
            'pode_cadastrar_atividade_extraordinaria': pode_cadastrar_atividade_extraordinaria,
            'next_excluir': reverse('atendimento_index'),
            'sigla_uf': settings.SIGLA_UF.upper(),
            'ativar_acompanhamento_processo': config.ATIVAR_ACOMPANHAMENTO_PROCESSO,
            'dias_acompanhamento_processo': config.DIAS_ACOMPANHAMENTO_PROCESSO,
            'sistemas_webservices_procapi': sistemas_webservices_procapi
        }
    )


@never_cache
@login_required
@permission_required('atendimento.view_defensor')
def index_get(request):
    """Utilizado para buscar os atendimentos conforme o dia selecionado no Painel do Defensor"""

    mensagem = 'Erro ao buscar dados'
    sucesso = False

    if request.method == 'POST' and request.is_ajax():

        if hasattr(request.user.servidor, 'defensor'):

            # faz leitura de dados do request Ajax e trata a data base
            dados = simplejson.loads(request.body)
            try:
                data_base = datetime.strptime(dados['data'][:10], '%Y-%m-%d').date()
            except KeyError:
                data_base = date.today()

            defensor = request.user.servidor.defensor

            # busca as atuações do dia selecionado
            defensorias = list(defensor.all_atuacoes.parcialmente_vigentes(
                inicio=data_base,
                termino=data_base
            ).values_list('defensoria_id', flat=True))

            if request.session.get('comarca'):
                comarca = Comarca.objects.get(id=request.session['comarca'])
            else:
                comarca = request.user.servidor.comarca

            nucleo = request.session.get('nucleo')
            itinerante = request.user.servidor.proximo_itinerante

            if not defensor.eh_defensor and itinerante and nucleo and nucleo.itinerante:
                defensorias = [itinerante.defensoria_id]

            # Se não existir atuação para o dia selecionado não deve nem executar a query
            if defensorias:

                # início da criação da query para buscar dados da vw_atendimentos_defensor
                data_base_ini = data_base
                data_base_fim = datetime.combine(data_base, time.max)

                from atendimento.atendimento.models import ViewAtendimentoDefensor

                query = Q(
                    Q(defensoria_id__in=defensorias) &
                    Q(
                        Q(data_atendimento__range=[data_base_ini, data_base_fim]) |
                        Q(
                            Q(data_atendimento=None) &
                            Q(
                                Q(data_agendamento__range=[data_base_ini, data_base_fim]) |
                                Q(tipo=Atendimento.TIPO_NUCLEO)
                            )
                        )
                    )
                )

                if nucleo:
                    query &= Q(nucleo_id=nucleo.id)

                    if nucleo.supervisionado and not defensor.eh_defensor:
                        query &= Q(responsavel_id=defensor.id)

                else:
                    query &= Q(comarca_id=comarca.id) & Q(nucleo_id=None)

                atendimentos = ViewAtendimentoDefensor.objects.filter(
                    query
                ).order_by(
                    '-data_atendimento',
                    '-prioridade',
                    'data_atendimento_recepcao',
                    'data_agendamento'
                )

                # TODO: Usar método da model atendimento.Defensor
                # Permite atender sem liberar pela recepção se tiver permissão pra isso
                pode_atender_sem_liberar = request.user.has_perm('atendimento.atender_sem_liberar')
                pode_atender_retroativo = request.user.has_perm('atendimento.atender_retroativo')

                dados = []
                for a in atendimentos:

                    if not a.data_atendimento and a.recepcao_id:
                        cron = Cronometro.objects.filter(
                            atendimento_id=a.id,
                            termino__gte=a.data_atendimento_recepcao
                        ).order_by(
                            '-termino'
                        ).first()
                    else:
                        cron = None

                    # Adiciona verificação se o atendimento é LUNA, visto que os atendimentos LUNA sempre recebem um
                    # Responsável a partir do momento que é distribuído no CRC, quebrando a lógica abaixo.
                    # Tratar um agendamento LUNA com a lógica de distribuído faz com que os liberados não apareçam
                    # devido o filtro presente em atendimento/index_box_atendimentos.html
                    usuario_luna = None
                    atendimento_online = False
                    if settings.CHATBOT_LUNA_USERNAME:
                        usuario_luna = User.objects.get(username=settings.CHATBOT_LUNA_USERNAME)
                        if usuario_luna:
                            atendimento_online = True if usuario_luna.first_name == a.cadastrado_por_nome else False

                    dados.append({
                        'id': a.id,
                        'numero': a.numero,
                        'tipo': Atendimento.LISTA_TIPO[a.tipo][1],
                        'data_agendamento': Util.date_to_json(a.data_agendamento) if a.data_agendamento else None,
                        'data_atendimento': Util.date_to_json(a.data_atendimento) if a.data_atendimento else None,
                        'data_atendimento_recepcao': Util.date_to_json(a.data_atendimento_recepcao) if a.data_atendimento_recepcao else None,  # noqa: E501
                        'requerente': a.requerente_nome,
                        'requerente_nome_social': a.requerente_nome_social,
                        'requerido': a.requerido_nome,
                        'requerido_nome_social': a.requerido_nome_social,
                        'agenda': a.agenda_id,
                        'forma_atendimento': a.forma_atendimento_id,
                        'extra': a.extra,
                        'inicial': a.inicial_numero,
                        'origem': a.origem_tipo,
                        'recepcao': a.recepcao_id or pode_atender_sem_liberar or pode_atender_retroativo,
                        'defensor': a.defensor_nome,
                        'substituto': a.substituto_nome,
                        'responsavel': a.responsavel_nome,
                        'defensoria': a.defensoria_origem_nome if a.tipo == Atendimento.TIPO_NUCLEO else a.defensoria_nome,  # noqa: E501
                        'nucleo': a.nucleo_nome,
                        'apoio': True if a.tipo == Atendimento.TIPO_NUCLEO else False,
                        'liberado': True if a.liberado_por_nome is not None else False,
                        'qualificacao': a.qualificacao_nome,
                        'area': a.area_nome,
                        'agendado': True if a.data_agendamento else False,
                        'realizado': True if a.data_atendimento else False,
                        'distribuido': True if a.responsavel_nome and not atendimento_online else False,
                        'atrasado': True if a.data_agendamento and a.data_agendamento < datetime.now() else False,
                        'prazo': a.prazo,
                        'prioridade': a.prioridade,
                        'cadastrado_por': a.cadastrado_por_nome,
                        'liberado_por': a.liberado_por_nome,
                        'atendido_por': a.atendido_por_nome,
                        'em_atendimento': {
                            'servidor': cron.servidor.nome if cron.servidor else None,
                            'servidor_id': cron.servidor.id if cron.servidor else None,
                            'data_inicio': cron.inicio
                        } if cron else None,
                        'historico_agendamento': a.historico_agendamento
                    })

                return JsonResponse(dados, safe=False)
            else:
                mensagem = 'Não há atuação/lotação para o dia selecionado'
                sucesso = True

    return JsonResponse({'success': sucesso, 'mensagem': mensagem})


@login_required
@permission_required('atendimento.view_defensor')
def index_get_documentos(request):

    if request.method == 'POST' and request.is_ajax():

        dados = simplejson.loads(request.body)

        if hasattr(request.user.servidor, 'defensor'):

            defensor = request.user.servidor.defensor

            try:
                inicio = datetime.strptime(dados['data'][:10], '%Y-%m-%d')
            except KeyError:
                inicio = date.today()

            termino = datetime.combine(inicio, time.max)
            semana_anterior = inicio.fromordinal(inicio.toordinal() - 7)

            if request.session.get('comarca'):
                comarca = Comarca.objects.get(id=request.session['comarca'])
            else:
                comarca = request.user.servidor.comarca.id

            nucleo = request.session.get('nucleo')

            # DOCUMENTOS
            if nucleo:
                defensorias = defensor.atuacoes(vigentes=True).filter(defensoria__nucleo=nucleo)
            else:
                defensorias = defensor.atuacoes(vigentes=True).filter(defensoria__comarca=comarca)

            defensorias = set(defensorias.values_list('defensoria_id', flat=True))

            documentos = AtendimentoDocumento.objects.filter(
                Q(atendimento__defensor__defensoria__in=defensorias) &
                (
                    (
                        Q(atendimento__partes__tipo=AtendimentoPessoa.TIPO_REQUERENTE) &
                        Q(atendimento__partes__responsavel=True) &
                        Q(atendimento__partes__ativo=True)
                    ) |
                    (
                        Q(atendimento__inicial__partes__tipo=AtendimentoPessoa.TIPO_REQUERENTE) &
                        Q(atendimento__inicial__partes__responsavel=True) &
                        Q(atendimento__inicial__partes__ativo=True)
                    )
                ) &
                (
                    (
                        Q(documento_online_id=None) &
                        (
                            Q(analisar=True) |
                            Q(data_enviado=None) |
                            Q(data_enviado__range=[semana_anterior, termino])
                        )
                    ) |
                    (
                        ~Q(prazo_resposta=None) &
                        Q(status_resposta=AtendimentoDocumento.STATUS_RESPOSTA_PENDENTE)
                    )
                ) &
                Q(atendimento__ativo=True) &
                Q(ativo=True)
            ).order_by(
                'prazo_resposta',
                '-data_enviado',
                'data_cadastro'
            ).values(
                'id',
                'nome',
                'arquivo',
                'atendimento__numero',
                'atendimento__partes__pessoa__nome',
                'atendimento__inicial__partes__pessoa__nome',
                'atendimento__partes__pessoa__nome_social',
                'atendimento__inicial__partes__pessoa__nome_social',
                'data_cadastro',
                'data_enviado',
                'arquivo',
                'cadastrado_por_id',
                'cadastrado_por__nome',
                'enviado_por_id',
                'enviado_por__nome',
                'documento_online_id',
                'prazo_resposta',
                'analisar',
            )

            dados = []
            for a in documentos:
                requerente = None
                if a['atendimento__partes__pessoa__nome_social']:
                    requerente = a['atendimento__partes__pessoa__nome_social']
                elif a['atendimento__inicial__partes__pessoa__nome_social']:
                    requerente = a['atendimento__inicial__partes__pessoa__nome_social']
                elif a['atendimento__partes__pessoa__nome']:
                    requerente = a['atendimento__partes__pessoa__nome']
                else:
                    requerente = a['atendimento__inicial__partes__pessoa__nome']
                dados.append({
                    'id': a['id'],
                    'nome': a['nome'],
                    'arquivo': a['arquivo'],
                    'atendimento_numero': a['atendimento__numero'],
                    'requerente': requerente,
                    'enviado': True if a['data_enviado'] or a['documento_online_id'] else False,
                    'prazo': True if a['prazo_resposta'] else False,
                    'prazo_resposta': a['prazo_resposta'],
                    'prazo_resposta_dias': (a['prazo_resposta'].date() - date.today()).days if a['prazo_resposta'] else None,  # noqa: E501
                    'data_cadastro': a['data_cadastro'],
                    'data_enviado': a['data_enviado'],
                    'cadastrado_por_id': a['cadastrado_por_id'],
                    'cadastrado_por_nome': a['cadastrado_por__nome'],
                    'enviado_por_id': a['enviado_por_id'],
                    'enviado_por_nome': a['enviado_por__nome'],
                    'documento_online_id': a['documento_online_id'],
                    'analisar': a['analisar'],
                })

            return JsonResponse(dados, safe=False)

    return JsonResponse({'success': False})


@login_required
@permission_required('atendimento.view_defensor')
def index_get_resumo(request):

    if request.method == 'POST' and request.is_ajax():

        dados = simplejson.loads(request.body)

        if hasattr(request.user.servidor, 'defensor'):

            defensor = request.user.servidor.defensor
            defensorias = set(defensor.atuacoes(vigentes=True).values_list('defensoria_id', flat=True))

            try:
                inicio = datetime.strptime(dados['data'][:10], '%Y-%m-%d')
            except KeyError:
                inicio = date.today()

            if request.session.get('comarca'):
                comarca = Comarca.objects.get(id=request.session['comarca'])
            else:
                comarca = request.user.servidor.comarca

            nucleo = request.session.get('nucleo')

            dia_semana, dias_mes = calendar.monthrange(inicio.year, inicio.month)

            # AGENDAMENTOS

            agendamentos = []
            for dia in range(dias_mes):
                agendamentos.append({'dia': dia + 1, 'pauta': 0, 'extra': 0})

            if nucleo:
                atendimentos = AtendimentoDefensor.objects.filter(
                    defensoria__nucleo=nucleo,
                    tipo__in=[1, 2, 4, 9])
            else:
                atendimentos = AtendimentoDefensor.objects.filter(
                    defensoria__comarca=comarca,
                    defensoria__nucleo=None,
                    tipo__in=[1, 2, 4, 9])

            if defensor.eh_defensor:
                atendimentos = atendimentos.filter(
                    (
                        (
                            Q(defensor=defensor)
                            & Q(substituto=None)
                        ) |
                        Q(substituto=defensor)
                    ) &
                    Q(remarcado=None) &
                    Q(ativo=True)
                )
            elif nucleo and nucleo.supervisionado:
                atendimentos = atendimentos.filter(
                    Q(responsavel=defensor) &
                    Q(remarcado=None) &
                    Q(ativo=True)
                )
            else:
                atendimentos = atendimentos.filter(
                    Q(defensoria__in=defensorias) &
                    Q(remarcado=None) &
                    Q(ativo=True)
                )

            for dias in atendimentos.extra(
                select={
                    'day': "DATE_PART('day', atendimento_atendimento.data_agendamento)",
                    'hour': "DATE_PART('hour', atendimento_atendimento.data_agendamento)",
                    'minute': "DATE_PART('minute', atendimento_atendimento.data_agendamento)"
                }
            ).values(
                'day', 'hour', 'minute'
            ).annotate(
                # noqa
                Count('id')
            ).filter(
                data_agendamento__year=inicio.year,
                data_agendamento__month=inicio.month
            ).order_by('day'):

                dia = int(dias['day'] - 1)

                if dias['hour'] or dias['minute']:
                    agendamentos[dia]['pauta'] += dias['id__count']
                else:
                    agendamentos[dia]['extra'] += dias['id__count']

            # AUDIENCIAS

            audiencias = []
            for dia in range(dias_mes):
                audiencias.append({'dia': dia + 1, 'marcadas': 0, 'realizadas': 0, 'canceladas': 0})

            # Filtro base para audiências
            q_audiencias = Q()
            q_audiencias &= Q(tipo__audiencia=True)
            q_audiencias &= Q(data_protocolo__year=inicio.year)
            q_audiencias &= Q(data_protocolo__month=inicio.month)
            q_audiencias &= Q(ativo=True)

            # TODO: Unificar filtros defensor e assessor (ver impacto onde tem vários defensores na mesma defensoria)
            # Se defensor, vê apenas suas audiências na comarca
            if defensor.eh_defensor:
                q_audiencias &= Q(defensor_cadastro=defensor)
            # Se assessor, vê audiêcias de todas as defensorias onde está lotado
            else:
                q_audiencias &= Q(defensoria__in=defensorias)

            # TODO: Aplicar este filtro na variável defensorias (replicar pra toda view)
            if nucleo:
                q_audiencias &= Q(defensoria__nucleo=nucleo)
            else:
                q_audiencias &= Q(defensoria__comarca=comarca)

            audiencias_lst = Audiencia.objects.extra(
                select={'day': "DATE_PART('day', data_protocolo)"}
            ).values(
                'day',
                'audiencia_status'
            ).annotate(
                Count('id')
            ).filter(
                q_audiencias
            ).order_by('day')

            for dias in audiencias_lst:

                dia = int(dias['day'] - 1)

                if dias['audiencia_status'] == 0:
                    audiencias[dia]['marcadas'] = dias['id__count']
                elif dias['audiencia_status'] == 1:
                    audiencias[dia]['realizadas'] = dias['id__count']
                elif dias['audiencia_status'] == 2:
                    audiencias[dia]['canceladas'] = dias['id__count']

            return JsonResponse({
                'agendamentos': agendamentos,
                'audiencias': audiencias,
                'ativar_acompanhamento_processo': config.ATIVAR_ACOMPANHAMENTO_PROCESSO,
            })

    return JsonResponse({'success': False})


@login_required
@permission_required('atendimento.view_defensor')
def index_get_tarefas(request):

    if request.method == 'POST' and request.is_ajax():

        dados = simplejson.loads(request.body)

        tarefas = Tarefa.objects.none()  # Consulta vazia é retornada por padrão
        atuacoes = Atuacao.objects.none()  # Consulta vazia é retornada por padrão

        if hasattr(request.user.servidor, 'defensor'):

            defensor = request.user.servidor.defensor

            try:
                inicio = datetime.strptime(dados['data'][:10], '%Y-%m-%d')
            except KeyError:
                inicio = date.today()

            termino = datetime.combine(inicio, time.max)

            # Atuacoes vigentes para o dia
            atuacoes = Atuacao.objects.vigentes_por_defensor(defensor=defensor, inicio=inicio)
            atuacoes = set(atuacoes.values_list('defensoria', flat=True))

            # filtro geral
            q = (
                    Q(origem=None) &
                    ~Q(
                        Q(titulo='Solicitação de Apoio Respondida') &
                        Q(responsavel=None) &
                        Q(data_inicial=None) &
                        Q(data_final=None)
                    ) &
                    (
                        Q(movimento__isnull=False) |
                        (
                            Q(atendimento__ativo=True) &
                            (
                                (
                                    Q(atendimento__partes__tipo=AtendimentoPessoa.TIPO_REQUERENTE) &
                                    Q(atendimento__partes__responsavel=True) &
                                    Q(atendimento__partes__ativo=True)
                                ) |
                                (
                                    Q(atendimento__inicial__partes__tipo=AtendimentoPessoa.TIPO_REQUERENTE) &
                                    Q(atendimento__inicial__partes__responsavel=True) &
                                    Q(atendimento__inicial__partes__ativo=True)
                                )
                            )
                        )
                    ) &
                    (
                        Q(all_respostas=None) |
                        (
                            ~Q(all_respostas__finalizado=None) &
                            Q(all_respostas__ativo=True)
                        )
                    )
                )

            # Configuração para exibir ou não as cooperações cumpridas
            if not config.EXIBIR_COOPERACOES_CUMPRIDAS_PARA_RESPONSAVEL:
                q &= ~Q(
                    Q(prioridade=Tarefa.PRIORIDADE_COOPERACAO) &
                    Q(status=Tarefa.STATUS_CUMPRIDO) &
                    Q(setor_responsavel__in=atuacoes)
                )

            # filtro do usuário
            qs = Q()

            # tarefas com resposta para as atuações vigentes
            qs |= Q(resposta_para__in=atuacoes)

            if defensor.eh_defensor or request.user.is_superuser or request.user.has_perm(perm='atendimento.view_all_tarefas'):  # noqa: E501

                # tarefas de atendimentos das atuações vigentes
                qs |= Q(setor_responsavel__in=atuacoes)

                # tarefas de atendimentos feitos no itinerante
                qs |= (
                    Q(atendimento__defensor__defensoria__nucleo__itinerante=True) &
                    Q(atendimento__defensor__defensor=defensor)
                )

                if config.HERDAR_TAREFAS_DOS_SUPERVISIONADOS:

                    # Todos servidores vinculados as atuacoes do defensor
                    servidores = set(Atuacao.objects.filter(
                        defensoria__in=atuacoes
                    ).vigentes().values_list('defensor__servidor_id', flat=True))

                    qs |= Q(responsavel__in=servidores)

                else:

                    qs |= Q(responsavel=defensor.servidor_id)

            else:  # filtro-base analista

                # tarefas cadastradas pelo servidor
                qs |= Q(cadastrado_por=request.user.servidor)

                # tarefas onde o servidor é responsável
                qs |= Q(responsavel=request.user.servidor)

                # tarefas de atendimentos das atuações vigentes ou prioridade alerta
                qs |= Q(
                    Q(setor_responsavel__in=atuacoes) &
                    Q(prioridade__in=[Tarefa.PRIORIDADE_ALERTA, Tarefa.PRIORIDADE_COOPERACAO])
                )

            q &= qs

            tarefas = Tarefa.objects.ativos().filter(q).values(
                'id',
                'data_finalizado',
                'data_final',
                'data_inicial',
                'prioridade',
                'responsavel_id',
                'responsavel__nome',
                'setor_responsavel__nome',
                'atendimento__nucleo__nome',
                'titulo',
                'status',
                'atendimento__numero',
                'atendimento__agenda',
                'atendimento__partes__pessoa__nome',
                'atendimento__inicial__partes__pessoa__nome',
                'atendimento__partes__pessoa__nome_social',
                'atendimento__inicial__partes__pessoa__nome_social',
                'movimento_id',
                'movimento__procedimento__uuid',
                'movimento__procedimento__numero',
                'all_respostas__finalizado__nome',
                'resposta_para',
                'resposta_para__nome',
                'visualizacoes'
            ).order_by(
                'data_inicial', 'prioridade', 'data_final', 'id', '-all_respostas__id'
            ).distinct(
                'data_inicial', 'prioridade', 'data_final', 'id'
            )

        dados = []

        # tarefas aguardando
        tarefas_ativas = tarefas.filter(
            (
                Q(data_final__gte=termino) |
                Q(data_final=None)
            ) &
            Q(data_finalizado=None) &
            Q(status=Tarefa.STATUS_CADASTRO)
        ).order_by(
            'data_inicial',
            'prioridade',
            'data_final'
        )

        index_get_tarefas_to_array(
            dados,
            tarefas_ativas,
            inicio, termino,
            Tarefa.TAREFA_AGUARDANDO,
            atuacoes,
            request.user.servidor
        )

        # tarefas atrasadas
        tarefas_atrasadas = tarefas.filter(
            data_finalizado=None,
            data_final__lt=inicio,
            status=Tarefa.STATUS_CADASTRO
        ).order_by(
            'prioridade',
            '-data_final'
        )

        index_get_tarefas_to_array(
            dados,
            tarefas_atrasadas,
            inicio,
            termino,
            Tarefa.TAREFA_ATRASADA,
            atuacoes,
            request.user.servidor
        )

        # tarefas com pendencias
        index_get_tarefas_to_array(
            dados,
            tarefas.filter(data_finalizado=None, status=Tarefa.STATUS_PENDENTE),
            inicio,
            termino,
            Tarefa.TAREFA_PENDENCIA,
            atuacoes,
            request.user.servidor
        )

        tarefas_cumpridas = tarefas.filter(data_finalizado=None, status=Tarefa.STATUS_CUMPRIDO)

        if config.DIA_LIMITE_EXIBICAO_TAREFAS_CUMPRIDAS > 0:
            data_base = date.today() - timedelta(days=config.DIA_LIMITE_EXIBICAO_TAREFAS_CUMPRIDAS)
            tarefas_cumpridas = tarefas_cumpridas.filter(all_respostas__data_finalizado__gte=data_base)

        # tarefas cumpridas
        index_get_tarefas_to_array(
            dados,
            tarefas_cumpridas,
            inicio,
            termino,
            Tarefa.TAREFA_CUMPRIDA,
            atuacoes,
            request.user.servidor
        )

        # tarefas finalizadas
        index_get_tarefas_to_array(
            dados,
            tarefas.filter(data_finalizado__range=[inicio, termino]),
            inicio,
            termino,
            Tarefa.TAREFA_FINALIZADA,
            atuacoes,
            request.user.servidor
        )

        return JsonResponse(dados, safe=False)

    return JsonResponse({'success': False})


def index_get_tarefas_to_array(arr, queryset, inicio, termino, status, atuacoes, servidor):

    for t in queryset:

        assistido = None
        if t['atendimento__partes__pessoa__nome_social']:
            assistido = t['atendimento__partes__pessoa__nome_social']
        elif t['atendimento__inicial__partes__pessoa__nome_social']:
            assistido = t['atendimento__inicial__partes__pessoa__nome_social']
        elif t['atendimento__partes__pessoa__nome']:
            assistido = t['atendimento__partes__pessoa__nome']
        else:
            assistido = t['atendimento__inicial__partes__pessoa__nome']

        arr.append({
            'id': t['id'],
            'ultima_resposta': t['all_respostas__finalizado__nome'],
            'atendimento_numero': t['atendimento__numero'],
            'nucleo': t['atendimento__nucleo__nome'],
            'defensoria': t['setor_responsavel__nome'],
            'titulo': t['titulo'],
            'responsavel': t['responsavel__nome'],
            'resposta_para': t['resposta_para__nome'],
            'assistido': assistido,
            'movimento': t['movimento_id'],
            'propac_uuid': t['movimento__procedimento__uuid'],
            'propac_numero': t['movimento__procedimento__numero'],
            'prioridade': t['prioridade'],
            'data_inicial': Util.date_to_json(t['data_inicial']) if t['data_inicial'] else None,
            'data_final': Util.date_to_json(t['data_final']) if t['data_final'] else None,
            'data_finalizado': Util.date_to_json(t['data_finalizado']) if t['data_finalizado'] else None,
            'agenda': t['atendimento__agenda'],
            'visualizada': bool(t['visualizacoes']),
            'status': status,
            'acompanhando': t['responsavel_id'] != servidor.id,
            'eh_alerta': t['prioridade'] == Tarefa.PRIORIDADE_ALERTA,
            'eh_cooperacao': t['prioridade'] == Tarefa.PRIORIDADE_COOPERACAO,
            'eh_tarefa': t['prioridade'] not in (Tarefa.PRIORIDADE_ALERTA, Tarefa.PRIORIDADE_COOPERACAO)
        })


@never_cache
@login_required
def listar(request):

    if request.GET.get('next'):
        request.session['next'] = request.GET.get('next')

    if request.GET.get('pessoa_id'):
        request.session['pessoa_id'] = request.GET.get('pessoa_id')

        if request.GET.get('ligacao_numero'):
            ligacao = Atendimento.objects.get(numero=request.GET.get('ligacao_numero'))
            request.session['ligacao_id'] = ligacao.id
            return redirect('{}?ligacao_numero={}'.format(reverse('atendimento_listar'), ligacao.numero))
        else:
            return redirect('atendimento_listar')

    assistido = request.session.get('pessoa_id')

    # ATENDIMENTOS EXCLUIDOS
    atendimentos_excluidos = AtendimentoPessoa.objects.filter(
        pessoa=assistido,
        tipo=AtendimentoPessoa.TIPO_REQUERENTE,
        ativo=True,
        atendimento__tipo__in=[Atendimento.TIPO_INICIAL, Atendimento.TIPO_VISITA],
        atendimento__inicial=None,
        atendimento__remarcado=None,
        atendimento__ativo=False,
        atendimento__partes__ativo=True,
        atendimento__partes__responsavel=True
    ).values(
        'atendimento_id',
        'atendimento__numero',
        'atendimento__data_agendamento',
        'atendimento__data_atendimento',
        'atendimento__partes__tipo',
        'atendimento__partes__pessoa__nome',
        'atendimento__defensor__defensor__servidor__nome',
        'atendimento__defensor__defensoria__nome',
        'atendimento__defensor__nucleo__nome',
        'atendimento__qualificacao__titulo',
        'atendimento__qualificacao__area__nome',
        'atendimento__historico_recepcao',
        'atendimento__agendado_por__nome',
        'atendimento__data_cadastro',
        'atendimento__historico',
        'atendimento__atendido_por__nome',
        'atendimento__data_exclusao',
        'atendimento__motivo_exclusao',
        'atendimento__excluido_por__nome',
    ).order_by(
        '-atendimento__data_atendimento', 'atendimento__data_agendamento', 'atendimento__numero'
    )

    atendimentos = []
    for parte in atendimentos_excluidos:

        if not atendimentos or parte['atendimento__numero'] != atendimentos[-1]['numero']:
            atendimentos.append({
                'numero': parte['atendimento__numero'],
                'data_cadastro': parte['atendimento__data_cadastro'],
                'data_agendamento': parte['atendimento__data_agendamento'],
                'data_atendimento': parte['atendimento__data_atendimento'],
                'defensor': parte['atendimento__defensor__defensor__servidor__nome'],
                'defensoria': parte['atendimento__defensor__defensoria__nome'],
                'nucleo': parte['atendimento__defensor__nucleo__nome'],
                'qualificacao': parte['atendimento__qualificacao__titulo'],
                'area': parte['atendimento__qualificacao__area__nome'],
                'requerente': None,
                'requerido': None,
                'recepcao': None,
                'agendado_por': parte['atendimento__agendado_por__nome'],
                'historico_agendamento': parte['atendimento__historico_recepcao'],
                'historico_defensor': parte['atendimento__historico'],
                'atendido_por': parte['atendimento__atendido_por__nome'],
                'data_exclusao': parte['atendimento__data_exclusao'],
                'motivo_exclusao': parte['atendimento__motivo_exclusao'],
                'excluido_por': parte['atendimento__excluido_por__nome'],
            })

            atendimentos[-1]['recepcao'] = Atendimento.objects.filter(
                origem=parte['atendimento_id'], tipo=Atendimento.TIPO_RECEPCAO, ativo=True
            ).values('data_atendimento', 'atendido_por__nome', 'historico').first()

        if parte['atendimento__partes__tipo'] == 0:
            atendimentos[-1]['requerente'] = parte['atendimento__partes__pessoa__nome']
        else:
            atendimentos[-1]['requerido'] = parte['atendimento__partes__pessoa__nome']

    atendimentos_excluidos = atendimentos

    # ATENDIMENTOS COMO REQUERENTE
    atendimentos_requerente = AtendimentoPessoa.objects.select_related("atendimento").filter(
        pessoa=assistido,
        tipo=AtendimentoPessoa.TIPO_REQUERENTE,
        ativo=True,
        atendimento__tipo__in=[Atendimento.TIPO_INICIAL, Atendimento.TIPO_VISITA],
        atendimento__inicial=None,
        atendimento__remarcado=None,
        atendimento__ativo=True,
        atendimento__partes__ativo=True,
        atendimento__partes__responsavel=True
    ).values(
        'atendimento_id',
        'atendimento__numero',
        'atendimento__data_agendamento',
        'atendimento__data_atendimento',
        'atendimento__partes__tipo',
        'atendimento__partes__pessoa__nome',
        'atendimento__defensor__defensor__servidor__nome',
        'atendimento__defensor__defensoria__nome',
        'atendimento__defensor__defensoria__atuacao',
        'atendimento__defensor__nucleo__nome',
        'atendimento__qualificacao__titulo',
        'atendimento__qualificacao__area__nome',
        'atendimento__historico_recepcao',
        'atendimento__agendado_por__nome',
        'atendimento__data_cadastro',
        'atendimento__historico',
        'atendimento__atendido_por__nome',
    ).order_by(
        '-atendimento__data_atendimento', 'atendimento__data_agendamento', 'atendimento__numero'
    )

    atendimentos = []
    arquivados_status = {}

    if arquivamento_esta_habilitado():
        # TODO verificar possibilidade de refatorar o status arquivado de property
        # para uma coluna física a fim de otimizar as consultas
        atendimentos_numeros = [atendimento['atendimento__numero'] for atendimento in atendimentos_requerente]
        arquivados_status = consulta_status_arquivado(atendimentos_numeros) or dict()

    for parte in atendimentos_requerente:

        if not atendimentos or parte['atendimento__numero'] != atendimentos[-1]['numero']:

            atendimentos.append({
                'numero': parte['atendimento__numero'],
                'data_cadastro': parte['atendimento__data_cadastro'],
                'data_agendamento': parte['atendimento__data_agendamento'],
                'data_atendimento': parte['atendimento__data_atendimento'],
                'defensor': parte['atendimento__defensor__defensor__servidor__nome'],
                'atuacao': parte['atendimento__defensor__defensoria__atuacao'],
                'defensoria': parte['atendimento__defensor__defensoria__nome'],
                'nucleo': parte['atendimento__defensor__nucleo__nome'],
                'qualificacao': parte['atendimento__qualificacao__titulo'],
                'area': parte['atendimento__qualificacao__area__nome'],
                'requerente': None,
                'requerido': None,
                'recepcao': None,
                'agendado_por': parte['atendimento__agendado_por__nome'],
                'historico_agendamento': parte['atendimento__historico_recepcao'],
                'historico_defensor': parte['atendimento__historico'],
                'atendido_por': parte['atendimento__atendido_por__nome'],
                'atendimento_principal_arquivado': arquivados_status.get(parte['atendimento__numero'], False)
            })

            atendimentos[-1]['recepcao'] = Atendimento.objects.filter(
                origem=parte['atendimento_id'], tipo=Atendimento.TIPO_RECEPCAO, ativo=True
            ).values('data_atendimento', 'atendido_por__nome', 'historico').first()

        if parte['atendimento__partes__tipo'] == 0:
            atendimentos[-1]['requerente'] = parte['atendimento__partes__pessoa__nome']
        else:
            atendimentos[-1]['requerido'] = parte['atendimento__partes__pessoa__nome']

    atendimentos_como_requerente = atendimentos

    # ATENDIMENTOS COMO NÃO HIPOSSUFICIÊNCIA
    indeferimentos = Indeferimento.objects.annotate(
        recursos=Sum(
            Case(
                When(processo__eventos__tipo__tipo=CoreTipoEvento.TIPO_RECURSO, then=1),
                output_field=IntegerField()
            ))
    ).filter(
        Q(pessoa=assistido) &
        Q(processo__desativado_em=None) &
        Q(processo__classe__tipo=CoreClasse.TIPO_NEGACAO_HIPOSSUFICIENCIA) &
        Q(
            Q(recursos=0) |
            Q(resultado=Indeferimento.RESULTADO_INDEFERIDO)
        )
    )

    # ATENDIMENTOS COMO REQUERIDO
    atendimentos_requerido = AtendimentoPessoa.objects.filter(
        pessoa=assistido,
        tipo=AtendimentoPessoa.TIPO_REQUERIDO,
        ativo=True,
        atendimento__tipo__in=[Atendimento.TIPO_INICIAL, Atendimento.TIPO_VISITA],
        atendimento__inicial=None,
        atendimento__remarcado=None,
        atendimento__ativo=True,
        atendimento__partes__ativo=True,
        atendimento__partes__responsavel=True
    ).values(
        'atendimento__numero',
        'atendimento__data_agendamento',
        'atendimento__data_atendimento',
        'atendimento__partes__tipo',
        'atendimento__partes__pessoa__nome',
        'atendimento__defensor__defensor__servidor__nome',
        'atendimento__defensor__defensoria__nome',
        'atendimento__defensor__nucleo__nome',
        'atendimento__qualificacao__titulo',
        'atendimento__qualificacao__area__nome',
    ).order_by(
        '-atendimento__data_atendimento', 'atendimento__data_agendamento', 'atendimento__numero'
    )

    atendimentos = []
    for parte in atendimentos_requerido:

        if not atendimentos or parte['atendimento__numero'] != atendimentos[-1]['numero']:
            atendimentos.append({
                'numero': parte['atendimento__numero'],
                'data_agendamento': parte['atendimento__data_agendamento'],
                'data_atendimento': parte['atendimento__data_atendimento'],
                'defensor': parte['atendimento__defensor__defensor__servidor__nome'],
                'defensoria': parte['atendimento__defensor__defensoria__nome'],
                'nucleo': parte['atendimento__defensor__nucleo__nome'],
                'qualificacao': parte['atendimento__qualificacao__titulo'],
                'area': parte['atendimento__qualificacao__area__nome'],
                'requerente': None,
                'requerido': None
            })

        if parte['atendimento__partes__tipo'] == 0:
            atendimentos[-1]['requerente'] = parte['atendimento__partes__pessoa__nome']
        else:
            atendimentos[-1]['requerido'] = parte['atendimento__partes__pessoa__nome']

    atendimentos_como_requerido = atendimentos

    # PROCESSOS
    atendimentos_processo = AtendimentoPessoa.objects.filter(
        pessoa=assistido,
        tipo=AtendimentoPessoa.TIPO_REQUERENTE,
        ativo=True,
        atendimento__tipo=Atendimento.TIPO_PROCESSO,
        atendimento__inicial=None,
        atendimento__remarcado=None,
        atendimento__ativo=True,
        atendimento__partes__ativo=True,
        atendimento__partes__responsavel=True
    ).values(
        'atendimento__numero',
        'atendimento__data_agendamento',
        'atendimento__data_atendimento',
        'atendimento__partes__tipo',
        'atendimento__partes__pessoa__nome',
        'atendimento__defensor__parte__parte',
        'atendimento__defensor__parte__data_cadastro',
        'atendimento__defensor__parte__processo__tipo',
        'atendimento__defensor__parte__processo__numero',
        'atendimento__defensor__parte__processo__acao__nome',
        'atendimento__defensor__parte__processo__vara__nome',
        'atendimento__defensor__parte__processo__area__nome',
    )

    atendimentos = []
    for parte in atendimentos_processo:

        if not atendimentos or parte['atendimento__numero'] != atendimentos[-1]['numero']:

            processo_tipo = parte['atendimento__defensor__parte__processo__tipo']

            if processo_tipo:
                processo_tipo = Processo.LISTA_TIPO[processo_tipo][1]

            atendimentos.append({
                'numero': parte['atendimento__numero'],
                'processo': parte['atendimento__defensor__parte__processo__numero'],
                'processo_parte': parte['atendimento__defensor__parte__parte'],
                'processo_acao': parte['atendimento__defensor__parte__processo__acao__nome'],
                'processo_vara': parte['atendimento__defensor__parte__processo__vara__nome'],
                'processo_area': parte['atendimento__defensor__parte__processo__area__nome'],
                'processo_tipo': processo_tipo,
                'processo_data_cadastro': parte['atendimento__defensor__parte__data_cadastro'],
                'requerente': None,
                'requerido': None
            })

        if parte['atendimento__partes__tipo'] == 0:
            atendimentos[-1]['requerente'] = parte['atendimento__partes__pessoa__nome']
        else:
            atendimentos[-1]['requerido'] = parte['atendimento__partes__pessoa__nome']

    atendimentos_processo = atendimentos

    modo_exibicao = config.MODO_EXIBICAO_LISTA_DE_ATENDIMENTOS_DO_ASSISTIDO.lower()
    exibicao = modo_exibicao.replace(" ", "").split(',')

    if request.GET.get('ligacao_numero'):
        url_agendamento_inicial = reverse('qualificacao_index', args=[request.GET.get('ligacao_numero')])
    else:
        url_agendamento_inicial = reverse('qualificacao_index')

    url_agendamento_inicial = '{}?next={}'.format(url_agendamento_inicial, request.session.get('next', ''))

    # if not atendimentos_como_requerente and \
    #         not atendimentos_como_requerido and \
    #         not atendimentos_processo and \
    #         not atendimentos_excluidos:
    #     return redirect(url_agendamento_inicial)
    # else:
    angular = 'AtendimentosPessoaCtrl'
    return render(request=request, template_name="atendimento/atendimentos.html", context=locals())


@login_required
def listar_comunidade(request, atendimento_numero):
    atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero)

    try:
        comunidade = Coletivo.objects.get(atendimento=atendimento.at_inicial).comunidade.to_dict()
    except ObjectDoesNotExist:
        comunidade = None

    return JsonResponse({'success': (comunidade is not None), 'comunidade': comunidade})


@never_cache
@login_required
def listar_documento(request, atendimento_numero=None):
    if atendimento_numero:

        atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero)

        partes = atendimento.processo_partes.values_list('id', flat=True)

        manifestacoes = Manifestacao.objects.ativos().select_related(
            'parte__processo'
        ).prefetch_related(
            Prefetch(
                'documentos',
                queryset=ManifestacaoDocumento.objects.ativos().filter(
                    manifestacao__parte__in=partes
                )
            )
        ).filter(
            parte__in=partes
        ).order_by(
            '-situacao',
            '-respondido_em',
        )

        manifestacoes = [{
            'id': manifestacao.id,
            'situacao': manifestacao.situacao,
            'respondido_em': manifestacao.respondido_em,
            'processo': {
                'numero': manifestacao.parte.processo.numero if not manifestacao.parte.processo.pre_cadastro else None
            },
            'documentos': [{
                'id': documento.id,
                'origem': documento.origem,
                'origem_id': documento.origem_id
            } for documento in manifestacao.documentos.ativos()]
        } for manifestacao in manifestacoes]

        # Identifica se o documento está vinculado à uma solicitação de Diligência
        subquery_diligencia = AtendimentoDefensor.objects.filter(
            Q(nucleo__diligencia=True) &
            Q(filhos__data_atendimento=None) &
            Q(filhos__ativo=True) &
            (
                (
                    Q(documento__documento_online__isnull=False) &
                    Q(documento__documento_online=OuterRef('documento_online_id'))
                ) |
                (
                    Q(documento__documento_online__isnull=True) &
                    Q(documento__arquivo=OuterRef('arquivo'))
                )
            )
        ).values('id')[:1]

        uploads = atendimento.documentos.select_related('pasta').filter(
            # documento_online=None
            origem_resposta=None
        ).annotate(
            pk=F('id'),
            documento_online_assunto=F('documento_online__assunto'),
            # titulo=F('documento_online__titulo'),
            documento_online_pk_uuid=F('documento_online__pk_uuid'),
            documento_online_versao=F('documento_online__versao_numero'),
            documento_online_criado_em=F('documento_online__criado_em'),
            documento_online_criado_por_nome_servidor=F('documento_online__criado_por__servidor__nome'),
            documento_online_modificado_em=F('documento_online__modificado_em'),
            documento_online_modificado_por_nome_servidor=F('documento_online__modificado_por__servidor__nome'),
            # TODO: renomear field data_assinado para "assinado_em" ou "finalizado_em"
            documento_online_assinado_em=F('documento_online__data_assinado'),
            # TODO: remover assinado por e incluir assinantes
            # documento_online_assinado_por_nome_servidor=F('documento_online__assinado_por__servidor__nome'),
            # documento_online_assinado_por_pk=F('documento_online__assinado_por__pk'),
            documento_online_esta_assinado=F('documento_online__esta_assinado'),
            cadastrado_por_nome=F('cadastrado_por__nome'),
            cadastrado_por_username=F('cadastrado_por__usuario__username'),
            enviado_por_nome=F('enviado_por__nome'),
            enviado_por_username=F('enviado_por__usuario__username'),
            pendente=Case(When(arquivo="", documento_online=None, then=Value(True)), default=Value(False),
                          output_field=BooleanField()),
            documento_resposta_nome=F('documento_resposta__nome'),
            documento_resposta_arquivo=F('documento_resposta__arquivo'),
            documento_resposta_data_enviado=F('documento_resposta__data_enviado'),
            documento_resposta_enviado_por_nome=F('documento_resposta__enviado_por__nome'),
            documento_resposta_enviado_por_username=F('documento_resposta__enviado_por__usuario__username'),
            pasta_nome=F("pasta__nome"),
            pasta_descricao=F("pasta__descricao"),
            diligencia=Exists(Subquery(subquery_diligencia, output_field=BooleanField()))
        ).order_by('-pendente', 'data_cadastro').values()

        for upload in uploads:

            if upload.get('arquivo'):
                documento_url = AtendimentoDocumento.objects.get(id=upload.get('pk')).arquivo.url
                # identifica tipo do arquivo
                filetype, encoding = mimetypes.guess_type(upload['arquivo'], strict=True)
                upload['filetype'] = filetype
                # completa URL do arquivo
                upload['arquivo'] = documento_url

            # Variável para controle se o documento ged pode ser baixado (padrão: False)
            upload['documento_online_pode_baixar'] = False
            upload['defensoria_nome'] = atendimento.defensoria.nome

            # Tratamentos para GED
            if upload['documento_online_id']:
                # Faz tratamento para habilitar os botões GED
                ged = DocumentoGED.objects.get(id=upload['documento_online_id'])

                pode_visualizar = SolarDefensoriaBackend().pode_visualizar(
                    document=ged,
                    usuario=request.user)
                upload['documento_online_pode_visualizar'] = pode_visualizar

                pode_editar = SolarDefensoriaBackend().pode_editar(
                    document=ged,
                    usuario=request.user)
                upload['documento_online_pode_editar'] = pode_editar[0]
                upload['documento_online_pode_editar_msg'] = pode_editar[1]

                pode_excluir = SolarDefensoriaBackend().pode_excluir_documento(
                    document=ged,
                    usuario=request.user)
                upload['documento_online_pode_excluir'] = pode_excluir[0]
                upload['documento_online_pode_excluir_msg'] = pode_excluir[1]

                pode_revogar_assinatura = SolarDefensoriaBackend().pode_revogar_assinatura(
                    document=ged,
                    usuario=request.user)
                upload['documento_online_pode_revogar_assinatura'] = pode_revogar_assinatura[0]
                upload['documento_online_pode_revogar_assinatura_msg'] = pode_revogar_assinatura[1]

                # Só pode baixar documento assinado ou com a configuração para baixar não assinados habilitada
                if upload['documento_online_esta_assinado'] or config.GED_PODE_BAIXAR_DOCUMENTO_NAO_ASSINADO:
                    upload['documento_online_pode_baixar'] = True

            if upload['prazo_resposta']:
                upload['prazo_resposta_dias'] = (upload['prazo_resposta'].date() - date.today()).days
            if not upload['status_resposta'] is None:
                upload['status_resposta_str'] = AtendimentoDocumento.LISTA_STATUS_RESPOSTA[upload['status_resposta']][1]

            # completa URL do arquivo
            if upload['documento_resposta_arquivo']:
                upload['documento_resposta_arquivo'] = AtendimentoDocumento.objects.get(id=upload.get('documento_resposta_id')).arquivo.url  # noqa: E501

            # Verifica em quais manifestações o documento está vinculado
            upload['manifestacoes'] = []
            for manifestacao in manifestacoes:
                for doc in manifestacao['documentos']:
                    if doc['origem'] == ManifestacaoDocumento.ORIGEM_ATENDIMENTO and doc['origem_id'] == upload['pk']:
                        upload['manifestacoes'].append(manifestacao['id'])

            if len(upload['manifestacoes']) == 0:
                upload['manifestacoes'] = None

            upload['pasta'] = {
                "id": upload["pasta_id"],
                "nome": upload["pasta_nome"],
                "descricao": upload["pasta_descricao"]
            }

        assistidos = AtendimentoPessoa.objects.filter(
            atendimento=atendimento.at_inicial,
            ativo=True,
        ).annotate(
            pessoa_nome=Case(
                When(pessoa__declara_identidade_genero=True, then=F('pessoa__nome_social')),
                default=F('pessoa__nome')
            ),
        ).values()

        assistidos_documentos = AtendimentoPessoa.objects.filter(
            pessoa__documentos__ativo=True,
            atendimento=atendimento.at_inicial,
            ativo=True,
        ).annotate(
            pk=F('pessoa__documentos__id'),
            arquivo=F('pessoa__documentos__arquivo'),
            documento_pk=F('pessoa__documentos__id'),
            nome=F('pessoa__documentos__nome'),
            data_enviado=F('pessoa__documentos__data_enviado'),
            enviado_por_nome=F('pessoa__documentos__enviado_por__nome'),
            enviado_por_username=F('pessoa__documentos__enviado_por__usuario__username'),
        ).values(
            'pk',
            'documento_pk',
            'pessoa_id',
            'arquivo',
            'nome',
            'data_enviado',
            'enviado_por_nome',
            'enviado_por_username'
        )

        for documento in assistidos_documentos:
            # completa URL do arquivo
            if documento.get('arquivo'):
                documento_url = DocumentoAssistido.objects.get(id=documento.get('documento_pk')).arquivo.url
                documento['arquivo'] = documento_url
                documento['pendente'] = False

            # Verifica em quais manifestações o documento está vinculado
            documento['manifestacoes'] = []
            for manifestacao in manifestacoes:
                for doc in manifestacao['documentos']:
                    if doc['origem'] == ManifestacaoDocumento.ORIGEM_PESSOA and doc['origem_id'] == documento['pk']:
                        documento['manifestacoes'].append(manifestacao['id'])

            if len(documento['manifestacoes']) == 0:
                documento['manifestacoes'] = None

        atendimento_url = reverse('atendimento_atender', args=[atendimento_numero, ])

        return JsonResponse({
            'uploads': list(uploads),
            'assistidos': list(assistidos),
            'assistidos_documentos': list(assistidos_documentos),
            'atendimento_url': atendimento_url,
            'atendimento_numero': atendimento_numero,
            'manifestacoes': manifestacoes
        }, safe=False)

    else:

        arr = []
        for i in Documento.objects.all():
            arr.append(i.nome)

        return JsonResponse(arr, safe=False)


@login_required
def listar_formulario(request, atendimento_numero):

    formularios = []

    try:
        atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero)
    except ObjectDoesNotExist:
        return JsonResponse({'success': False, 'formularios': formularios})

    if atendimento.nucleo:
        nucleo = atendimento.nucleo
    elif atendimento.defensoria and atendimento.defensoria.nucleo:
        nucleo = atendimento.defensoria.nucleo
    else:
        nucleo = None

    formularios_lst = FormularioNucleo.objects.ativos().filter(
        Q(exibir_em_atendimento=True) &
        (
            Q(nucleo_id=nucleo) |
            Q(publico=True)
        )
    )

    for formulario in formularios_lst:

        item = {
            'id': formulario.id,
            'texto': formulario.texto,
            'perguntas': []
        }

        for pergunta in formulario.perguntas:
            item['perguntas'].append({
                'id': pergunta.id,
                'texto': pergunta.texto,
                'tipo': pergunta.tipo,
                'alternativas': pergunta.alternativas,
                'resposta': None
            })

        respostas = RespostaNucleo.objects.filter(
            atendimento=atendimento.at_inicial,
            pergunta__formulario=formulario
        )

        for resposta in respostas:
            for pergunta in item['perguntas']:
                if pergunta['id'] == resposta.pergunta_id:
                    pergunta['resposta'] = resposta.texto

        formularios.append(item)

    return JsonResponse({'success': True, 'formularios': formularios})


@never_cache
@login_required
def listar_defensorias(request, atendimento_numero=None):

    atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero)

    # Recupera todos atendimentos vinculados ao inicial
    atendimentos = AtendimentoDefensor.objects.filter(
        Q(inicial=atendimento.at_inicial.id) &
        Q(tipo__in=[
            Atendimento.TIPO_INICIAL,
            Atendimento.TIPO_RETORNO,
            Atendimento.TIPO_NUCLEO,
            Atendimento.TIPO_VISITA,
            Atendimento.TIPO_ENCAMINHAMENTO,
            Atendimento.TIPO_ANOTACAO
        ]) &
        Q(remarcado=None) &
        Q(ativo=True)
    ).values_list('id', flat=True)

    # Gera lista dos ids dos atendimentos (inicial + retornos)
    atendimentos = [atendimento.at_inicial.id] + list(atendimentos)

    # Recupera lista de defensorias dos atendimentos
    defensorias_atendimentos = AtendimentoDefensor.objects.filter(
        id__in=atendimentos
    ).order_by('defensoria_id').distinct().values_list('defensoria_id', flat=True)

    # Recupera lista de defensorias das partes de processos
    defensorias_processos = ParteProcesso.objects.filter(
        atendimento__in=atendimentos
    ).order_by('defensoria_id').distinct().values_list('defensoria_id', flat=True)

    # Unifica lista de defensorias participantes (via atendimentos ou processos)
    defensorias_participantes = set(list(defensorias_atendimentos) + list(defensorias_processos))

    # Recupera dados das defensorias participantes ou que podem vincular tarefa de cooperacao
    defensorias = list(Defensoria.objects.filter(
        Q(id__in=defensorias_participantes) |
        Q(pode_vincular_tarefa_de_cooperacao=True)
    ).values(
        'id',
        'nome',
        'atuacao',
        'nucleo__multidisciplinar',
        'nucleo__diligencia',
        'nucleo__indeferimento',
        'nucleo__agendamento',
    ))

    # Marca quais das defensorias participam do atendimento/processo
    for defensoria in defensorias:

        if defensoria['id'] in defensorias_participantes:
            defensoria['participante'] = True
        else:
            defensoria['participante'] = False

        # Só permite o cadastro de tarefas para setores com acesso ao Painel do Defensor (ver nucleo.views.index)
        defensoria['pode_cadastrar_tarefa'] = True
        nucleo_multidisciplinar = defensoria.pop('nucleo__multidisciplinar')
        nucleo_diligencia = defensoria.pop('nucleo__diligencia')
        nucleo_indeferimento = defensoria.pop('nucleo__indeferimento')
        nucleo_agendamento = defensoria.pop('nucleo__agendamento')

        if nucleo_multidisciplinar:
            defensoria['pode_cadastrar_tarefa'] = False
        elif nucleo_diligencia:
            defensoria['pode_cadastrar_tarefa'] = False
        elif nucleo_indeferimento and not nucleo_agendamento:
            defensoria['pode_cadastrar_tarefa'] = False

    data_base = datetime.today()

    resposta_para = []

    if hasattr(request.user.servidor, 'defensor'):
        defensor = request.user.servidor.defensor

        atuacoes = Atuacao.objects.vigentes_por_defensor(
            defensor=defensor,
            inicio=data_base
        ).values(
            'defensoria_id',
            'defensoria__nome',
            'defensoria__nucleo__multidisciplinar',
            'defensoria__nucleo__diligencia',
            'defensoria__nucleo__indeferimento',
            'defensoria__nucleo__agendamento',
        )

        for atuacao in atuacoes:

            # Só permite o cadastro de tarefas para setores com acesso ao Painel do Defensor (ver nucleo.views.index)
            pode_cadastrar_tarefa = True
            nucleo_multidisciplinar = atuacao.pop('defensoria__nucleo__multidisciplinar')
            nucleo_diligencia = atuacao.pop('defensoria__nucleo__diligencia')
            nucleo_indeferimento = atuacao.pop('defensoria__nucleo__indeferimento')
            nucleo_agendamento = atuacao.pop('defensoria__nucleo__agendamento')

            if nucleo_multidisciplinar:
                pode_cadastrar_tarefa = False
            elif nucleo_diligencia:
                pode_cadastrar_tarefa = False
            elif nucleo_indeferimento and not nucleo_agendamento:
                pode_cadastrar_tarefa = False

            resposta_para.append({
                'id': atuacao['defensoria_id'],
                'nome': atuacao['defensoria__nome'],
                'pode_cadastrar_tarefa': pode_cadastrar_tarefa,
            })

    return JsonResponse({
        'defensorias': defensorias,
        'resposta_para': resposta_para
    })


@never_cache
@login_required
def listar_tipos_tarefas(request, atendimento_numero=None):
    from atendimento.atendimento.models import Qualificacao
    tipos_tarefas = list(Qualificacao.objects.filter(tipo=40).values('id', 'titulo'))
    return JsonResponse({
        'tipos_tarefas': tipos_tarefas
    })


@login_required
def perfil(request, comarca_id=None):
    if hasattr(request.user.servidor, 'defensor'):
        data_base = datetime.now()
        servidor = request.user.servidor
        defensor = request.user.servidor.defensor

        AtuacaoClass = Atuacao
        atuacoes_lst = defensor.atuacoes().filter(
            defensoria__evento=None
        )

        atuacoes_ativas = atuacoes_lst.vigentes()

        atuacoes_futuras = atuacoes_lst.filter(
            Q(data_inicial__gt=data_base)
        )

        comarcas = atuacoes_ativas.filter(
            defensoria__nucleo=None
        ).distinct(
            'defensoria__comarca_id',
            'defensoria__comarca__nome'
        ).order_by(
            'defensoria__comarca__nome'
        ).values_list(
            'defensoria__comarca_id',
            'defensoria__comarca__nome'
        )

        nucleos = Atuacao.objects.filter(
            Q(defensor=defensor) &
            ~Q(defensoria__nucleo=None) &
            (
                (
                    (
                        Q(data_inicial__lte=data_base) &
                        Q(data_final=None)
                    ) |
                    (
                        Q(data_inicial__lte=data_base) &
                        Q(data_final__gte=data_base)
                    )
                ) |
                (
                    Q(defensoria__evento__participantes=servidor) &
                    Q(defensoria__evento__data_inicial__lte=datetime.now()) &
                    Q(defensoria__evento__data_final__gte=datetime.now() - timedelta(days=5)) &
                    Q(defensoria__evento__ativo=True)
                )
            )
        ).distinct(
            'defensoria__nucleo_id',
            'defensoria__nucleo__nome',
            'defensoria__nucleo__plantao'
        ).order_by(
            'defensoria__nucleo__nome'
        ).values_list(
            'defensoria__nucleo_id',
            'defensoria__nucleo__nome',
            'defensoria__nucleo__plantao',
            'defensoria__nucleo__diligencia',
        )

        # Verifica se usário está lotado em alguma defensoria com o recurso peticionamento habilitado
        pode_cadastrar_peticionamento = atuacoes_ativas.filter(
            defensoria__pode_cadastrar_peticionamento=True
        ).exists()

        total_peticionamentos = Manifestacao.objects.ativos().filter(
            situacao__in=[Manifestacao.SITUACAO_ANALISE, Manifestacao.SITUACAO_ERRO],
            defensoria__in=atuacoes_ativas.values('defensoria')
        ).count()

        total_avisos = 0

        # Se pode cadastrar peticionamentos e procapi está ativo, permite visualizar avisos
        if pode_cadastrar_peticionamento and config.ATIVAR_PROCAPI:

            # Só consulta se credenciais foram identificadas ou é um superusuário
            if defensor.eh_defensor or request.user.is_superuser:
                # Consulta no ProcAPI o total de avisos pendentes
                api = APIAviso()
                total_avisos = api.consultar_total_abertos(params={
                    'distribuido_cpf': defensor.servidor.cpf if not request.user.is_superuser else None,
                    'ativo': True
                })

        # Se pode processos e procapi está ativo, permite visualizar avisos
        if request.user.has_perm('processo.view_distribuicao') and config.ATIVAR_PROCAPI:

            total_processos_para_distribuir = 0

            api = APIAviso()
            # Consulta no ProcAPI a lista de avisos pendentes
            total_processos_para_distribuir = api.consultar_total(params={
                'distribuido': False,
                'ativo': True,
            })

        request.session['nucleo'] = None
        request.session['comarca'] = servidor.comarca.id

    return render(request=request, template_name="atendimento/perfil.html", context=locals())


@login_required
def responder_nucleo(request, atendimento_numero):
    pass


@login_required
def responder_tarefa(request, atendimento_numero):
    if request.method == 'POST':

        servidor = Servidor.objects.get(usuario_id=request.user.id)
        tarefa = Tarefa.objects.get(id=request.POST.get('tarefa'))
        documento = None

        if request.FILES:

            salvou, documento = salvar_documento_pre(request, atendimento_numero)

            if not salvou:
                for k, v in documento.items():
                    messages.error(request, '{0}: {1}'.format(k, v))
                return redirect(request.POST['next'])

        resposta = tarefa.responder(request.POST.get('resposta'), servidor, int(request.POST.get('status')))

        if documento:
            resposta.documento = documento
            resposta.save()

        if request.POST.get('documento_ged'):
            resposta.documentos.add(request.POST.get('documento_ged'))

        if tarefa.status != resposta.status:
            tarefa.status = resposta.status
            tarefa.save()

        messages.success(request, 'Resposta à tarefa registrada com sucesso!')

        return redirect(request.POST['next'])

    raise Http404


@login_required
@transaction.atomic
def salvar(request, atendimento_numero):
    """Utilizado para salvar o atendimento na página Ficha de Atendimento Histórico"""

    success = False
    errors = None
    recarregar_pagina = False

    if request.method == 'POST':

        atendimento = AtendimentoDefensor.objects.filter(numero=atendimento_numero, ativo=True, remarcado=None).first()

        if (atendimento and
            (not atendimento.realizado or
             atendimento.agendado_hoje or
             atendimento.realizado_hoje or
             atendimento.pode_atender_retroativo(request.user))):

            data_atendimento_original = atendimento.data_atendimento
            form = AtendimentoDefensorForm(request.POST, instance=atendimento)

            if form.is_valid():

                atendimento = form.save(commit=False)
                atendimento.modificado_por = request.user.servidor

                servidor = request.user.servidor
                defensor = servidor.defensor

                if not atendimento.atendido_por:
                    atendimento.atendido_por = servidor

                # Corrige vínculo do defensor com o atendimento
                if defensor.eh_defensor and defensor not in [atendimento.defensor, atendimento.substituto]:

                    atuacao = defensor.all_atuacoes.vigentes(
                        ajustar_horario=False
                    ).filter(
                        defensoria=atendimento.defensoria
                    ).first()

                    if atuacao is None:
                        logger.warning('O defensor {} não está lotado na defensoria {}'.format(defensor, atendimento.defensoria))  # noqa: E501
                    elif atuacao.tipo == Atuacao.TIPO_SUBSTITUICAO:
                        atendimento.defensor = atuacao.titular
                        atendimento.substituto = atuacao.defensor
                    elif atuacao:
                        atendimento.defensor = atuacao.defensor

                if atendimento.data_atendimento.date() == date.today():
                    if data_atendimento_original:
                        atendimento.data_atendimento = data_atendimento_original
                    else:
                        atendimento.data_atendimento = datetime.now()

                if request.POST.get('finalizado'):
                    atendimento.finalizado_por = Defensor.objects.get(servidor__usuario=request.user)
                    atendimento.data_finalizado = datetime.now()

                if request.POST.get('forma_atendimento'):
                    atendimento.forma_atendimento_id = request.POST.get('forma_atendimento')
                else:
                    atendimento.forma_atendimento_id = None

                if request.POST.get('tipo_coletividade'):
                    atendimento.tipo_coletividade_id = request.POST.get('tipo_coletividade')
                else:
                    atendimento.tipo_coletividade_id = None

                if request.POST.get('interesse_conciliacao'):
                    atendimento.interesse_conciliacao = request.POST.get('interesse_conciliacao')
                else:
                    atendimento.interesse_conciliacao = None

                if request.POST.get('justificativa_nao_interesse'):
                    atendimento.justificativa_nao_interesse = request.POST.get('justificativa_nao_interesse')
                else:
                    atendimento.justificativa_nao_interesse = None

                if request.POST.get('tipo'):
                    atendimento.nucleo = Nucleo.objects.filter(acordo=True).first()

                if AtendimentoPreso.objects.filter(id=atendimento.id).exists():
                    nadep = AtendimentoPreso.objects.get(id=atendimento.id)
                    nadep.__dict__.update(atendimento.__dict__)
                    atendimento = nadep

                atualiza_tarefa_atendimento_origem(
                    atendimento=atendimento,
                    resposta=atendimento.historico,
                    servidor=servidor,
                    finalizar=True,
                    reabrir=False
                )

                salvar_acordo_para_atendimento(request, atendimento)

                atendimento.save()

                # Muda status publico/privado do atendimento
                if request.POST.get('publico'):
                    if request.POST.get('publico') == 'true':
                        Acesso.conceder_publico(atendimento, request.user.servidor.defensor)
                    else:
                        Acesso.revogar_publico(atendimento, request.user.servidor.defensor)

                # Salvar indeferimento por negação para cada pessoa marcada
                if request.POST.get('indeferimento_classe'):

                    success = True

                    # recarregar página ao Salvar o Indeferimento
                    if request.POST.getlist('indeferimento_pessoa'):
                        recarregar_pagina = True

                        for pessoa in request.POST.getlist('indeferimento_pessoa'):
                            try:
                                Indeferimento.objects.get_or_create_atendimento_pessoa(
                                    atendimento=atendimento,
                                    atuacao_id=None,
                                    pessoa_id=pessoa,
                                    classe_id=request.POST.get('indeferimento_classe'),
                                    setor_encaminhado_id=request.POST.get('indeferimento_setor_encaminhado'),
                                )
                            except Exception as e:
                                errors = {
                                    'field': 'Indeferimento',
                                    'message': str(e)
                                }
                                success = False
                                recarregar_pagina = False
                                break
                            else:
                                success = True
                else:
                    success = True

            else:

                errors = [({'field': k, 'message': v[0]}) for k, v in form.errors.items()]

    return JsonResponse({
        'success': success,
        'errors': errors,
        'recarregar_pagina': recarregar_pagina
    })


def salvar_acordo_para_atendimento(request, atendimento):

    if request.POST.get('acordo') and (atendimento.nucleo or atendimento.defensoria.nucleo):

        acordo, novo = Acordo.objects.update_or_create(
            atendimento=atendimento,
            defaults={
                'tipo': int(request.POST.get('acordo')),
                'ativo': True
            }
        )

        if request.FILES:

            if acordo.termo:
                documento = acordo.termo
            else:
                documento = AtendimentoDocumento(
                    atendimento=atendimento.at_inicial,
                    cadastrado_por=request.user.servidor)

            documento.data_enviado = datetime.now()
            documento.enviado_por = request.user.servidor

            form = DocumentoForm(request.POST, request.FILES, instance=documento)

            if form.is_valid():
                acordo.termo = form.save()
                acordo.save()

        # Remove dados de atendimento se ambas as partes não compareceram
        if acordo.tipo == Acordo.TIPO_AMBOS and not config.CONTABILIZAR_ACORDO_TIPO_AMBOS:
            atendimento.atendido_por = None
            atendimento.data_atendimento = None

    else:

        if hasattr(atendimento, 'acordo'):
            atendimento.acordo.ativo = False
            atendimento.acordo.save()


@login_required
def finalizar(request, atendimento_numero):
    atendimento = AtendimentoDefensor.objects.filter(numero=atendimento_numero, ativo=True, remarcado=None).first()
    data_atendimento_original = atendimento.data_atendimento

    if atendimento.data_atendimento:
        if atendimento.data_atendimento.date() == date.today():
            if data_atendimento_original:
                atendimento.data_atendimento = data_atendimento_original
            else:
                atendimento.data_atendimento = datetime.now()
    else:
        atendimento.data_atendimento = datetime.now()

    atendimento.save()

    messages.success(request, 'Atendimento finalizado com sucesso!')
    return redirect('atendimento_index')


class AnotacaoCreateView(CreateView):
    form_class = AnotacaoForm
    model = AtendimentoDefensor
    template_name = "atendimento/atender_modal_anotacao_form.html"

    # variáveis para uso em heranças
    atendimento = None
    atendimento_tipo = Atendimento.TIPO_ANOTACAO

    def get_context_data(self, **kwargs):

        context = super(AnotacaoCreateView, self).get_context_data(**kwargs)
        context['form_name'] = 'AnotacaoForm'

        # carrega dados do atendimento em que a anotação será vinculada
        if self.kwargs['atendimento_numero']:
            self.atendimento = AtendimentoDefensor.objects.get(
                numero=self.kwargs['atendimento_numero'],
                ativo=True
            )
            context['atendimento'] = self.atendimento

        return context

    def form_invalid(self, form):

        mensagem = "Erro ao salvar! Por favor, tente novamente."

        if self.request.is_ajax():
            return JsonResponse({'success': False, 'message': mensagem, 'errors': form.errors})
        else:
            messages.error(self.request, mensagem)
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', '/'))

    def form_valid(self, form):

        anotacao = form.save(commit=False)
        atendimento = AtendimentoDefensor.objects.only('id', 'inicial_id').get(numero=self.kwargs['atendimento_numero'])

        # atualiza objeto com dados adicionais
        anotacao.origem = atendimento
        anotacao.inicial = atendimento.at_inicial
        anotacao.cadastrado_por = self.request.user.servidor
        anotacao.tipo = self.atendimento_tipo
        if not settings.SIGLA_UF.upper() == 'AM':
            qualificacao = form.cleaned_data['qualificacao']

            if (qualificacao.eh_qualificacao_sms and (not config.USAR_SMS or not config.SERVICO_SMS_DISPONIVEL)):
                mensagem = "<b>O envio de SMS está desabilitado no sistema!</b>"
                if self.request.is_ajax():
                    return JsonResponse({'success': False, 'message': mensagem, 'anotacao': Util.object_to_dict(anotacao)})  # noqa: E501
                else:
                    messages.error(self.request, mensagem)
                    return HttpResponseRedirect(self.get_success_url())

            enviar_sms = (qualificacao.eh_qualificacao_sms and config.USAR_SMS and config.SERVICO_SMS_DISPONIVEL)

            if (enviar_sms):
                # Substitui as palavras chaves no modelo MENSAGEM_SMS_ANOTACAO
                historico = config.MENSAGEM_SMS_ANOTACAO.replace(
                    "SMS_CONTEUDO_ANOTACAO", form.cleaned_data['historico'], 1
                ).replace(
                    "SMS_DEF_SIGLA", settings.SIGLA_INSTITUICAO
                )
                # Remove os acencos da mensagem se assim foi configurado
                if config.SMS_REMOVER_ACENTOS:
                    historico = Util.unaccent(historico)
                    anotacao.historico = historico

        # só registra dados de atendimento em anotações
        if self.atendimento_tipo == Atendimento.TIPO_ANOTACAO:
            anotacao.atendido_por = self.request.user.servidor
            anotacao.data_atendimento = timezone.now()

        if not settings.SIGLA_UF.upper() == 'AM':
            # obtem defensor/defensoria a partir da atuação
            anotacao.defensor = form.cleaned_data['atuacao'].defensor
            anotacao.defensoria = form.cleaned_data['atuacao'].defensoria

            if enviar_sms:
                telefone = atendimento.telefone_para_sms

                # Se o telefone não foi encontrado, algo deu errado
                # Mostra uma mensagem de erro
                if not telefone['telefone']:
                    mensagem = "Não foi possível enviar o SMS."
                    if telefone['no_valid_cell']:
                        mensagem += " Nenhum telefone válido foi encontrado."
                    if self.request.is_ajax():
                        return JsonResponse({
                            'success': False,
                            'message': mensagem,
                            'anotacao': Util.object_to_dict(anotacao)
                        })
                    else:
                        messages.error(self.request, mensagem)
                        return HttpResponseRedirect(self.get_success_url())

                telefone_numero = "55{}{}".format(telefone['telefone'].ddd, telefone['telefone'].numero)
                envio = envia_sms(historico, telefone_numero)

                if not (envio.status_code >= 200 and envio.status_code < 300):
                    mensagem = "Não foi possível enviar o SMS! Código do erro: {}".format(envio.status_code)
                    if self.request.is_ajax():
                        return JsonResponse({
                            'success': False,
                            'message': mensagem,
                            'anotacao': Util.object_to_dict(anotacao)
                        })
                    else:
                        messages.error(self.request, mensagem)
                        return HttpResponseRedirect(self.get_success_url())

        super(AnotacaoCreateView, self).form_valid(form)

        # salva documento vinculado a anotação
        if self.request.FILES:

            documento = AtendimentoDocumento(
                atendimento=self.object,
                data_enviado=timezone.now(),
                enviado_por=self.request.user.servidor)

            form_documento = DocumentoForm(self.request.POST, self.request.FILES, instance=documento)

            if form_documento.is_valid():
                form_documento.save()

        # força limpeza da árvore do atendimento
        if hasattr(atendimento.at_inicial, 'arvore'):
            atendimento.at_inicial.arvore.ativo = False
            atendimento.at_inicial.arvore.save()

        mensagem = "Registro salvo com sucesso!"

        if self.request.is_ajax():
            return JsonResponse({'success': True, 'message': mensagem, 'anotacao': Util.object_to_dict(anotacao)})
        else:
            messages.success(self.request, mensagem)
            return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', '/')


class NotificacaoCreateView(AnotacaoCreateView):
    form_class = NotificacaoForm
    template_name = "atendimento/atender_modal_notificacao_form.html"
    atendimento_tipo = Atendimento.TIPO_NOTIFICACAO

    def get_context_data(self, **kwargs):

        context = super(NotificacaoCreateView, self).get_context_data(**kwargs)
        context['form_name'] = 'NotificacaoForm'
        context['notificar'] = True
        context['pode_notificar_assistido'] = False

        # Se houver, insere informações do documento que está sendo recusado
        if self.request.GET.get('documento_id'):
            context['documento'] = AtendimentoDocumento.objects.get(
                id=self.request.GET.get('documento_id'),
                analisar=True
            )

        # Verifica se o assistido pode ser notificado
        if config.USAR_NOTIFICACOES_ASSISTIDO_VIA_CHATBOT and self.atendimento:
            context['pode_notificar_assistido'] = self.atendimento.requerente.pessoa.aderiu_luna_chatbot

        return context

    def form_valid(self, form):

        result = super(NotificacaoCreateView, self).form_valid(form)

        assistido = Pessoa.objects.get(
            id=self.request.POST.get('assistido')
        )

        self.object.add_pessoa(
            pessoa_id=assistido.id,
            tipo=AtendimentoPessoa.TIPO_NOTIFICACAO,
            responsavel=False,
            vincular_ao_inicial=False
        )

        # Se houver, registra recusa de documento vinculado
        if self.request.POST.get('documento_id'):

            documento = AtendimentoDocumento.objects.get(
                id=self.request.POST.get('documento_id'),
                analisar=True
            )

            documento.analisar = False
            documento.arquivo = None
            documento.data_enviado = None
            documento.enviado_por = None
            documento.save()

        chatbot_notificar_requerente_atendimento.apply_async(
            kwargs={
                'numero': self.object.numero,
                'pessoa_id': assistido.id
            },
            queue='sobdemanda'
        )

        return result


@login_required
@permission_required('atendimento.add_coletivo')
def salvar_comunidade(request, atendimento_numero):
    from assistido.models import Pessoa
    from assistido.forms import CadastrarEndereco, PessoaForm

    # resposta padrao
    resposta = {'success': False, 'errors': {}}
    errors = []

    if request.method == 'POST':

        atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero)

        # carrega e trata dados recebidos via ajax
        dados = Dados(request.body)
        dados['tipo'] = constantes.TIPO_PESSOA_JURIDICA

        # tenta carregar registro, se nao conseguir carrega novo
        try:
            pessoa = Pessoa.objects.get(id=dados['id'])
        except Pessoa.DoesNotExist:
            pessoa = Pessoa()

        # verifica se já existe outra pessoa com o cpf informado
        if dados['cpf']:
            cpf_existe = Pessoa.objects.filter(cpf=dados['cpf']).exclude(id=dados['id'])
        else:
            cpf_existe = False

        if cpf_existe:

            errors.append('O cpf/cnpj informado já está vinculado a outra pessoa!')

        else:

            # recupera id do bairro a partir do municipio/nome
            if dados.get('bairro') is not None:
                try:
                    bairro, msg = Bairro.objects.get_or_create(
                        municipio_id=dados.get('municipio'),
                        nome__iexact=dados.get('bairro'),
                        desativado_em=None,
                        defaults={
                            # necessário por ter usado uma func no get_or_create para esse field
                            'nome': dados.get('bairro')
                        }
                    )
                except Exception:
                    bairro = Bairro.objects.filter(
                        municipio_id=dados.get('municipio'),
                        nome__iexact=dados.get('bairro'),
                        desativado_em=None,
                    ).first()

                dados.set('bairro', bairro.id)

            pessoa_form = PessoaForm(dados.get_all(), instance=pessoa)

            if pessoa_form.is_valid():
                # TODO: Verificar consistencia ou remover
                novo = (pessoa.id == None)  # noqa
                pessoa = pessoa_form.save()

                try:

                    endereco_form = CadastrarEndereco(
                        dados.get_all(),
                        instance=pessoa.endereco,
                        initial={
                            'estado': dados.get('estado'),
                            'municipio': dados.get('municipio')
                        })

                except KeyError:
                    endereco_form = CadastrarEndereco(dados.get_all(), instance=pessoa.endereco)

                if endereco_form.is_valid():
                    pessoa.enderecos.add(endereco_form.save())

            else:
                # inclui erros no array de erros
                errors.append([(k, v[0]) for k, v in pessoa_form.errors.items()])

        if len(errors) == 0:

            resposta['success'] = True

            coletivo, msg = Coletivo.objects.get_or_create(atendimento=atendimento.at_inicial)
            coletivo.comunidade = pessoa
            coletivo.save()

        else:

            resposta['errors'] = errors

        resposta['id'] = pessoa.id
        resposta['pessoa'] = pessoa.to_dict()

    return JsonResponse(resposta)


@login_required
@permission_required('atendimento.add_documento')
def salvar_documento(request, atendimento_numero):

    if request.method == 'POST':

        salvou, documento = salvar_documento_pre(request, atendimento_numero)

        if salvou and documento and documento.documento_online:

            if documento.atendimento.tipo == Atendimento.TIPO_ATIVIDADE:
                atendimento = documento.atendimento.origem
            else:
                atendimento = documento.atendimento

            sda = ServiceDocumentoAtendimento(documento)

            sda.preencher({
                'defensoria': documento.documento_online.grupo_dono,
                'atendimento': atendimento.at_defensor,
                'servidor': request.user.servidor,
                'pessoa': documento.pessoa,
                'hoje': date.today(),
            })

            if documento.atendimento.tipo == Atendimento.TIPO_ATIVIDADE:

                for participante in documento.atendimento.participantes.all():
                    documento.documento_online.adicionar_pendencia_de_assinatura_por_usuario(
                        grupo=documento.atendimento.origem.defensor.defensoria,
                        assinado_por=participante.usuario,
                        cadastrado_por=request.user)

        if salvou and documento and documento.pendente:
            # Notifica assistido via chatbot Luna
            chatbot_notificar_requerente_documento.apply_async(
                kwargs={'documento_id': documento.id},
                queue='sobdemanda'
            )

        if request.is_ajax():

            documento_dict = None

            if salvou and documento:

                url = None
                filetype = None

                if documento.arquivo:
                    url = documento.arquivo.url
                    filetype, encoding = mimetypes.guess_type(documento.arquivo.url, strict=True)

                enviado_por_nome = None
                enviado_por_username = None

                if documento.enviado_por:
                    enviado_por_nome = documento.enviado_por.nome
                    enviado_por_username = documento.enviado_por.usuario.username

                cadastrado_por_nome = None
                cadastrado_por_username = None

                if documento.cadastrado_por:
                    cadastrado_por_nome = documento.cadastrado_por.nome
                    cadastrado_por_username = documento.cadastrado_por.usuario.username

                documento_dict = {
                    'id': documento.id,
                    'documento_online_id': documento.documento_online_id,
                    'nome': documento.nome,
                    'arquivo': url,
                    'enviado_por_nome': enviado_por_nome,
                    'enviado_por_username': enviado_por_username,
                    'data_enviado': documento.data_enviado,
                    'data_cadastro': documento.data_cadastro,
                    'cadastrado_por_username': cadastrado_por_username,
                    'cadastrado_por_nome': cadastrado_por_nome,
                    'filetype': filetype
                }

            resposta = {
                'success': documento_dict is not None,
                'errors': [(k, v[0]) for k, v in documento.items()] if documento and not salvou else [],
                'documento': documento_dict
            }

            return JsonResponse(resposta)

        else:

            return redirect(request.POST['next'])

    else:

        raise Http404


@login_required
@permission_required('atendimento.add_documento')
def salvar_documento_pre(request, atendimento_numero, **kwags):
    if request.method == 'POST':

        atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero)

        if request.POST.get('id'):
            documento = AtendimentoDocumento.objects.get(id=request.POST.get('id'))
        else:
            documento = AtendimentoDocumento(atendimento=atendimento, cadastrado_por=request.user.servidor)

        if request.FILES:

            documento.data_enviado = datetime.now()
            documento.enviado_por = request.user.servidor

            # Se possuía versão assinada, desativa e remove vínculo
            if documento.documento_assinado:
                documento.documento_assinado.desativar(usuario=request.user)
                documento.documento_assinado = None

        form = DocumentoForm(request.POST, request.FILES, instance=documento)

        if form.is_valid():
            return True, form.save()
        else:
            return False, form.errors

    return False, None


@login_required
def auto_criar_documento_ged(request, atendimento_numero):

    cpf = request.GET.get('cpf')

    if not cpf and len(cpf) == 11:
        messages.error(request, '<b>Não foi possível criar o documento de ciência!</b> <br> Verifique se o cpf/cpnj do assistido foi informado corretamente.')  # noqa: E501

    from .models import PessoaAssistida
    pessoa = PessoaAssistida.objects.ativos().filter(pessoa_ptr__cpf=cpf).first()

    atendimento_defensor = AtendimentoDefensor.objects.filter(numero=atendimento_numero).first()

    form = TabDocumentoForm(request.POST)

    if form.is_valid():

        data = form.cleaned_data
        modelo_ged = data['modelo']
        assunto_ged = data['assunto']

        try:
            criar_documento_ged_para_o_atendimento(
                modelo_ged,
                atendimento_defensor,
                pessoa,
                request.user,
                assunto=assunto_ged,
                liberar_para_assinar=True
            )
        except Exception as e:
            erro = str(e.args).replace('(', '').replace(')', '').replace(',', '.')

            messages.error(request, f'<b>Não foi possível criar o documento GED!</b><br><br>Erro técnico: < {erro} > ')

    return redirect('{}#/documentos'.format(
                        reverse('atendimento_atender', args=[atendimento_numero]),
                    ))


class DocumentoCriarParaAtendimento(SingleAtendimentoDefensorObjectMixin, DocumentoCriar):
    atendimentodefensor_queryset = AtendimentoDefensor.objects.only('numero')
    form_class = CriarDocumentoOnlineParaAtendimentoForm

    @method_decorator(permission_required('atendimento.add_documento'))
    def dispatch(self, request, *args, **kwargs):
        return super(DocumentoCriarParaAtendimento, self).dispatch(request, *args, **kwargs)

    def get_form_action(self):
        kwargs = {self.atendimentodefensor_slug_url_kwarg: self.atendimentodefensor_object.numero}
        action = reverse('atendimento_ged_criar', kwargs=kwargs)
        return action

    def get_form_kwargs(self):
        kwargs = super(DocumentoCriarParaAtendimento, self).get_form_kwargs()
        kwargs.update({
            'atendimento': self.atendimentodefensor_object
        }
        )
        return kwargs

    def get_initial(self):

        initial = super(DocumentoCriarParaAtendimento, self).get_initial()
        grupo = self.atendimentodefensor_object.defensoria

        initial.update({
            'grupo': grupo,
        })

        if self.request.GET.get('modelo_documento'):
            modelo_documento = DocumentoGED.admin_objects.get(pk_uuid=self.request.GET.get('modelo_documento'))
            initial.update({
                'tipo_documento': modelo_documento.tipo_documento_id,
                'modelo_documento': modelo_documento.pk_uuid,
            })

        return initial

    def form_valid(self, form):
        ret = super(DocumentoCriarParaAtendimento, self).form_valid(form)
        atendimento = self.atendimentodefensor_object.atendimento_ptr
        documento_online = self.object
        pessoa = form.cleaned_data['pessoa']
        pasta = form.cleaned_data.get('pasta', None)
        documento_atendimento = AtendimentoDocumento(
            atendimento=atendimento,
            documento_online=documento_online,
            cadastrado_por=self.request.user.servidor,
            nome=documento_online.assunto,
            pessoa=pessoa,
            pasta=pasta
        )
        documento_atendimento.save()

        context_conteudo = {
            'defensoria': documento_online.grupo_dono,
            'atendimento': self.atendimentodefensor_object,
            'servidor': self.request.user.servidor,
            'pessoa': pessoa,
            'hoje': date.today(),
        }
        preencher_campos_ged(documento=documento_online, context_conteudo=context_conteudo, fallback_to_conteudo=True)
        documento_online.save()

        return ret


class DocumentoCriarParaAtendimentoViaModeloPublico(DocumentoCriarParaAtendimento):
    form_class = CriarDocumentoOnlineParaAtendimentoViaModeloPublicoForm

    def get_form_action(self):
        kwargs = {self.atendimentodefensor_slug_url_kwarg: self.atendimentodefensor_object.numero}
        action = reverse('atendimento_ged_criar_via_modelo_publico', kwargs=kwargs)
        return action


@login_required
@permission_required('atendimento.add_documento')
def agendar_documento(request):

    if request.method == 'POST' and request.POST.get('id'):

        documento = AtendimentoDocumento.objects.get(id=request.POST.get('id'))
        form = AgendarDocumentoForm(request.POST, instance=documento)

        if form.is_valid():

            documento = form.save(commit=False)

            if request.FILES:

                if documento.documento_resposta:
                    resposta = documento.documento_resposta
                else:
                    resposta = AtendimentoDocumento(
                        atendimento=documento.atendimento,
                        cadastrado_por=request.user.servidor
                    )

                resposta.nome = '{} (RESPOSTA)'.format(documento.nome).upper()
                resposta.data_enviado = datetime.now()
                resposta.enviado_por = request.user.servidor
                resposta.ativo = True

                form_resposta = DocumentoRespostaForm(request.POST, request.FILES, instance=resposta)

                if form_resposta.is_valid():
                    resposta = form_resposta.save()

                documento.documento_resposta = resposta

            documento.save()

            return redirect(request.POST['next'])

    raise Http404


@login_required
@permission_required('atendimento.add_documento')
def analisar_documento(request):

    if request.method == 'POST' and request.POST.get('id'):

        documento = AtendimentoDocumento.objects.get(
            id=request.POST.get('id'),
            analisar=True
        )

        if request.POST.get('aceitar') == 'true':
            documento.data_analise = datetime.now()
            documento.analisado_por = request.user.servidor
            documento.analisar = False
            documento.save()

        return redirect(request.POST['next'])

    raise Http404


@login_required
@permission_required('nucleo.add_resposta')
def salvar_formulario(request, atendimento_numero):
    if request.method == 'POST':

        atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero)

        dados = simplejson.loads(request.body)
        success = True

        formulario = FormularioNucleo.objects.get(id=dados['id'])

        novo = not RespostaNucleo.objects.filter(
            atendimento=atendimento.at_inicial,
            pergunta__formulario=formulario
        ).exists()

        for pergunta in dados['perguntas']:

            RespostaNucleo.objects.update_or_create(
                atendimento=atendimento.at_inicial,
                pergunta_id=pergunta['id'],
                defaults={
                    'texto': pergunta['resposta']
                }
            )

        if novo and formulario.gerar_alerta_em_atendimento:

            descricao = ''

            for pergunta in dados['perguntas']:
                descricao += '<p>{}<br><b>{}</b></p>'.format(
                    pergunta['texto'],
                    pergunta['resposta'] if not pergunta['resposta'] is None else 'Não informado'
                )

            Tarefa.objects.create(
                atendimento=atendimento.at_inicial,
                resposta_para=atendimento.defensoria,
                setor_responsavel=formulario.nucleo.defensoria_set.ativos().first(),
                titulo=formulario.texto,
                descricao=descricao,
                data_inicial=date.today(),
                data_final=None,
                prioridade=Tarefa.PRIORIDADE_ALERTA,
                cadastrado_por=request.user.servidor
            )

        return JsonResponse({'success': success})

    return JsonResponse({'success': False})


@login_required
@permission_required('atendimento.add_tarefa')
@reversion.create_revision(atomic=False)
def salvar_tarefa(request, atendimento_numero):
    if request.method == 'POST':

        dados = Dados(request.body)
        errors = []
        novo = True

        if dados.get('id'):
            tarefa = Tarefa.objects.get(id=dados.get('id'))
            novo = False
        else:
            atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero)
            tarefa = Tarefa(atendimento=atendimento, cadastrado_por=request.user.servidor)

        form = TarefaForm(dados.get_all(), instance=tarefa)

        if form.is_valid():

            tarefa = form.save()

            reversion.set_user(request.user)
            reversion.set_comment(Util.get_comment_save(request.user, tarefa, novo))

        else:
            errors.append([(k, v[0]) for k, v in form.errors.items()])

    return JsonResponse({'success': (len(errors) == 0), 'errors': errors, 'id': tarefa.id})


@login_required
def solicitar_nucleo_form(request, atendimento_numero):

    return render(
        request,
        template_name="atendimento/atender_modal_nucleos.html",
        context={
            'atendimento_numero': atendimento_numero,
        })


@login_required
def solicitar_nucleo(request, atendimento_numero):
    from defensor.models import Atuacao

    atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero)

    atuacao_origem = Atuacao.objects.get(id=request.POST.get('atuacao'))

    atuacao_destino = Atuacao.objects.filter(
        defensoria_id=request.POST.get('defensoria'),
        tipo=Atuacao.TIPO_TITULARIDADE,
        ativo=True
    ).order_by(
        '-defensor__eh_defensor',
        'data_inicial'
    ).first()

    agora = datetime.now()

    # se o atendimento de origem não tiver qualificação, assume qualificação do pedido de apoio
    if atendimento.qualificacao_id:
        qualificacao_id = atendimento.qualificacao_id
    else:
        qualificacao_id = request.POST.get('qualificacao')

    # cria solicitação do apoio
    pedido = AtendimentoDefensor(
        tipo=Atendimento.TIPO_RETORNO,
        inicial=atendimento.at_inicial,
        origem=atendimento,
        data_agendamento=agora,
        data_atendimento=agora,
        cadastrado_por=request.user.servidor,
        agendado_por=request.user.servidor,
        atendido_por=request.user.servidor,
        defensor=atuacao_origem.titular if atuacao_origem.titular else atuacao_origem.defensor,
        substituto=atuacao_origem.defensor if atuacao_origem.titular else None,
        defensoria=atuacao_origem.defensoria,
        qualificacao_id=qualificacao_id)

    sucesso = False
    form = NucleoPedidoForm(request.POST, instance=pedido)

    if form.is_valid():

        with transaction.atomic():

            pedido = form.save()

            # cria resposta do apoio
            resposta = AtendimentoDefensor(
                tipo=Atendimento.TIPO_NUCLEO,
                inicial=pedido.at_inicial,
                origem=pedido,
                cadastrado_por=request.user.servidor,
                agendado_por=request.user.servidor,
                defensor=atuacao_destino.defensor)

            form_resposta = NucleoRespostaForm(request.POST, instance=resposta)

            if form_resposta.is_valid():

                resposta = form_resposta.save()

                # se possuir documentos, os vincula à solicitação do apoio
                if 'documentos' in request.POST:

                    # remove ids de documento em duplicidade
                    documentos = []
                    for documento in request.POST.getlist('documentos'):
                        if documento not in documentos:
                            documentos.append(documento)

                    for documento in documentos:

                        doc_original = AtendimentoDocumento.objects.get(id=documento)

                        AtendimentoDocumento.objects.create(
                            atendimento=pedido,
                            pessoa=doc_original.pessoa,
                            modelo=doc_original.modelo,
                            documento=doc_original.documento,
                            documento_online=doc_original.documento_online,
                            arquivo=doc_original.arquivo,
                            nome=doc_original.nome,
                            data_enviado=doc_original.data_enviado,  # mantem data envio original
                            enviado_por=doc_original.enviado_por,  # mantem usuario que enviou original
                            cadastrado_por=request.user.servidor
                        )

                # se for para o núcleo de diligência, vincula pessoa à solicitação do apoio
                if request.POST.get('pessoa') and resposta.defensoria.nucleo.diligencia:

                    pedido.add_pessoa(
                        pessoa_id=request.POST.get('pessoa'),
                        tipo=AtendimentoPessoa.TIPO_DILIGENCIA,
                        responsavel=False,
                        vincular_ao_inicial=False
                    )

                    titulo_tarefa = 'Diligência para {0}'.format(pedido.partes.first())

                else:

                    titulo_tarefa = resposta.qualificacao.titulo

                # cria tarefa para acompanhamento do apoio
                tarefa = Tarefa(
                    atendimento=pedido,
                    cadastrado_por=request.user.servidor
                )

                form_tarefa = TarefaForm({
                    'prioridade': Tarefa.PRIORIDADE_ALERTA,
                    'titulo': titulo_tarefa.upper(),
                    'descricao': pedido.historico,
                    'data_inicial': date.today(),
                    'data_final': resposta.data_agendamento.date(),
                    'resposta_para': pedido.defensoria_id,
                    'setor_responsavel': resposta.defensoria_id
                }, instance=tarefa)

                if form_tarefa.is_valid():
                    form_tarefa.save()
                    sucesso = True
                else:
                    transaction.set_rollback(True)

            else:
                transaction.set_rollback(True)

    if sucesso:
        messages.success(request, u'Pedido de apoio enviado com sucesso!')
    else:
        messages.error(request, u'Erro ao salvar, verifique se todos campos foram preenchidos corretamente!')

    if 'atendimento/recepcao/marcados/' in request.META.get('HTTP_REFERER', '/'):
        return redirect(request.META.get('HTTP_REFERER', '/'))

    elif request.POST.get('next'):
        return redirect(request.POST['next'])

    else:
        return redirect('{}#/historico'.format(reverse('atendimento_atender', args=[atendimento.numero])))


@login_required
@permission_required('atendimento.view_defensor')
def visualizar(request, atendimento_id):
    pass


@login_required
def listar_atendimento_documentos_pendentes(request):
    servidor = request.user.servidor

    if hasattr(request.GET, 'submit'):
        page = 1
    else:
        page = request.GET.get('page')

    form = BuscarAtendimentoDocumentosForm(request.GET)

    if form.is_valid():

        filtro = request.GET.get('filtro')
        filtro_numero = re.sub('[^0-9]', '', filtro)

        comarca = request.session.get('comarca')

        atendimentos_lst = AtendimentoDefensor.objects.filter(
            Q(documento__ativo=True) &
            Q(documento__arquivo='') &
            Q(defensoria__comarca_id=comarca) &
            Q(ativo=True) &
            Q(remarcado=None) &
            (Q(tipo=Atendimento.TIPO_INICIAL) | Q(tipo=Atendimento.TIPO_RETORNO))
        ).distinct().order_by('-data_agendamento', '-data_atendimento')

        if len(filtro_numero) == 12:  # Numero do Atendimento

            atendimentos_lst = atendimentos_lst.filter(
                numero=filtro_numero
            )

        elif len(filtro_numero) == 11:  # Numero do CPF

            atendimentos_lst = atendimentos_lst.filter(
                partes__pessoa__cpf=filtro,
                partes__ativo=True
            )

        else:

            atendimentos_lst = atendimentos_lst.filter(
                partes__pessoa__nome__icontains=filtro,
                partes__ativo=True
            )

        paginacao = Paginator(atendimentos_lst, 25)

        try:
            atendimentos = paginacao.page(page)
        except PageNotAnInteger:
            atendimentos = paginacao.page(1)
        except EmptyPage:
            atendimentos = paginacao.page(paginacao.num_pages)

    angular = 'BuscarCtrl'

    return render(request=request, template_name="atendimento/busca_docs_pendentes.html", context=locals())


@login_required
@permission_required('atendimento.change_atendimento')
def unificar(request, atendimento_principal, atendimento_secundario):

    primario = AtendimentoDefensor.objects.get(numero=atendimento_principal)
    secundario = AtendimentoDefensor.objects.get(numero=atendimento_secundario)

    # Pode unificar se principal for atendimento inicial ou de processo e secundário for processo
    if (primario.tipo in [Atendimento.TIPO_INICIAL, Atendimento.TIPO_VISITA, Atendimento.TIPO_PROCESSO] and
       secundario.tipo == Atendimento.TIPO_PROCESSO):  # noqa: E501

        # Move relacionamentos dependentes para novo agendamento
        service = AtendimentoService(secundario)
        service.transferir_relacionamentos(
            atendimento_destino=primario,
            copiar_pessoas=True,
            transferir_pessoas=False
        )

        secundario.partes.update(ativo=False)  # desativa pessoas do atendimento secundário
        secundario.ativo = False  # desativa atendimento para processo
        secundario.save()

        processo = request.GET.get('processo', '')
        messages.success(request, u'Processo nº %s unificado ao atendimento atual!' % processo)

    # Pode unificar se principal e secundário forem inicial
    elif (primario.tipo in [Atendimento.TIPO_INICIAL, Atendimento.TIPO_VISITA] and
          secundario.tipo in [Atendimento.TIPO_INICIAL, Atendimento.TIPO_VISITA]):

        service = AtendimentoService(secundario)
        service.transferir_relacionamentos(
            atendimento_destino=primario,
            copiar_pessoas=True,
            transferir_pessoas=False
        )

        hoje = datetime.now()
        dia_um = datetime(hoje.year, hoje.month, 1)

        # se não realizado ou realizado no mes vigente, vira tipo retorno
        if not secundario.data_atendimento or secundario.data_atendimento > dia_um:
            secundario.tipo = Atendimento.TIPO_RETORNO

        secundario.partes.update(ativo=False)  # desativa pessoas do atendimento secundário
        secundario.inicial = primario  # vincula atendimento duplicado ao atendimento principal
        secundario.save()

        messages.success(request, u'Atendimento nº %s unificado ao atendimento atual!' % secundario.numero)

    else:

        messages.error(request, u'Não foi possível unificar atendimentos!')

    return redirect('atendimento_atender', atendimento_principal)


@login_required
def visualizar_acesso(request):
    defensor = request.user.servidor.defensor if hasattr(request.user.servidor, 'defensor') else None

    if defensor:
        defensorias = defensor.atuacoes(vigentes=True).values('defensoria_id')

        meus_atendimentos = Acesso.objects.filter(
            (
                (
                    Q(atendimento__defensor__defensoria__in=defensorias) &
                    Q(atendimento__ativo=True)
                ) |
                (

                    Q(atendimento__retorno__defensor__defensoria__in=defensorias) &
                    ~Q(atendimento__retorno__data_atendimento=None) &
                    Q(atendimento__retorno__ativo=True)
                )
            ),
            data_revogacao=None,
            ativo=True
        ).distinct().order_by('-data_concessao')

        outros_atendimentos = Acesso.objects.filter(
            defensor=defensor,
            data_revogacao=None,
            ativo=True
        ).order_by('-data_concessao')

    angular = 'AcessoCtrl'

    return render(request=request, template_name="atendimento/acessos.html", context=locals())


@login_required
def listar_acesso(request, atendimento_numero):
    atendimento = Atendimento.objects.get(numero=atendimento_numero)
    resposta = {
        'publico': bool(atendimento.acesso_publico()),
        'historico': [],
        'solicitacoes': [],
        'concessoes': []
    }

    acessos = Acesso.objects.select_related(
        'defensor__servidor',
        'solicitado_por__servidor',
        'concedido_por__servidor',
        'revogado_por__servidor',
    ).filter(
        atendimento=atendimento.at_inicial,
        ativo=True
    ).order_by(
        'defensor__servidor__nome',
        'id'
    )

    for acesso in acessos:
        obj = {
            'defensor': {
                'id': acesso.defensor.id,
                'nome': acesso.defensor.nome,
            } if acesso.defensor else None,
            'data_solicitacao': Util.date_to_json(acesso.data_solicitacao),
            'solicitado_por': {
                'id': acesso.solicitado_por.id,
                'nome': acesso.solicitado_por.nome,
            } if acesso.solicitado_por else None,
            'data_concessao': Util.date_to_json(acesso.data_concessao),
            'concedido_por': {
                'id': acesso.concedido_por.id,
                'nome': acesso.concedido_por.nome,
            } if acesso.concedido_por else None,
            'data_revogacao': Util.date_to_json(acesso.data_revogacao),
            'revogado_por': {
                'id': acesso.revogado_por.id,
                'nome': acesso.revogado_por.nome,
            } if acesso.revogado_por else None,
            'concedido': True if acesso.data_concessao else False,
        }

        resposta['historico'].append(obj)

        if acesso.defensor and not acesso.data_revogacao:
            if acesso.data_concessao:
                resposta['concessoes'].append(obj)
            else:
                resposta['solicitacoes'].append(obj)

    return JsonResponse(resposta, safe=False)


@login_required
def conceder_acesso_por_id(request, acesso_id):
    defensor = request.user.servidor.defensor if hasattr(request.user.servidor, 'defensor') else None

    if defensor:
        Acesso.objects.filter(
            id=acesso_id,
            data_concessao=None,
            data_revogacao=None
        ).update(
            data_concessao=datetime.now(),
            concedido_por=defensor
        )

        messages.success(request, u'Acesso ao atendimento concedido!')

    return redirect('atendimento_acesso_visualizar')


@login_required
def conceder_acesso(request, atendimento_numero):
    dados = Dados(request.body)
    atendimento = Atendimento.objects.get(numero=atendimento_numero)

    if dados['defensor']:
        Acesso.conceder(atendimento.at_inicial, dados['defensor'], request.user.servidor.defensor)
    else:
        Acesso.conceder_publico(atendimento.at_inicial, request.user.servidor.defensor)

    return JsonResponse({'success': True})


@login_required
def revogar_acesso_por_id(request, acesso_id):
    defensor = request.user.servidor.defensor if hasattr(request.user.servidor, 'defensor') else None

    if defensor:
        Acesso.objects.filter(
            id=acesso_id,
            data_revogacao=None
        ).update(
            data_revogacao=datetime.now(),
            revogado_por=defensor
        )

        messages.success(request, u'Acesso ao atendimento cancelado!')

    return redirect('atendimento_acesso_visualizar')


@login_required
def revogar_acesso(request, atendimento_numero):
    dados = Dados(request.body)
    atendimento = Atendimento.objects.get(numero=atendimento_numero)

    if dados['defensor']:
        Acesso.revogar(atendimento.at_inicial, dados['defensor'], request.user.servidor.defensor)
    else:
        Acesso.revogar_publico(atendimento.at_inicial, request.user.servidor.defensor)

    return JsonResponse({'success': True})


@login_required
def solicitar_acesso(request, atendimento_numero):
    dados = Dados(request.body)
    atendimento = Atendimento.objects.get(numero=atendimento_numero)

    Acesso.objects.update_or_create(
        atendimento=atendimento.at_inicial,
        defensor_id=dados['defensor'],
        data_concessao=None,
        data_revogacao=None,
        defaults={
            'data_solicitacao': datetime.now(),
            'solicitado_por': request.user.servidor.defensor
        })

    return JsonResponse({'success': True})


@login_required
def assuntos_get(request):
    cache_key = 'assunto.listar:'
    cache_data = cache.get(cache_key)

    if not cache_data:

        assuntos = Assunto.objects.filter(ativo=True).order_by(
            'pai', 'ordem'
        ).values(
            'id', 'pai', 'ordem', 'titulo', 'descricao', 'codigo'
        )

        arr = {}

        # inicializa array
        for assunto in assuntos:
            arr[assunto['id']] = {
                'id': assunto['id'],
                'titulo': assunto['titulo'],
                'descricao': assunto['descricao'],
                'ordem': assunto['ordem'],
                'pai': assunto['pai'],
                'filhos': []
            }

        # vincula filhos aos pais
        for assunto in assuntos:
            if assunto['pai']:
                arr[assunto['pai']]['filhos'].append(str(assunto['id']))

        cache_data = arr
        cache.set(cache_key, cache_data)

    return JsonResponse(cache_data, safe=False)


@login_required
def salvar_assunto(request):
    data = simplejson.loads(request.body)

    try:
        pai = Assunto.objects.get(id=data['pai']['id'])
    except ObjectDoesNotExist:
        pai = None

    assunto = Assunto(
        codigo=data['codigo'],
        titulo=data['titulo'],
        pai=pai,
        cadastrado_por=request.user.servidor,
    )

    if pai:
        assunto.ordem = pai.filhos.filter(ativo=True).count() + 1
    else:
        assunto.ordem = Assunto.objects.filter(ativo=True, pai=None).count() + 1

    assunto.save()

    return JsonResponse({'success': True}, safe=False)


@login_required
def excluir_assunto(request):
    data = simplejson.loads(request.body)
    erro = False

    try:
        assunto = Assunto.objects.get(id=data['id'], ativo=True)
    except ObjectDoesNotExist:
        erro = 'Assunto não existe.'
    else:
        if assunto.atendimentos.count():
            erro = 'Este assunto já esta sendo utilizado em algum atendimento.'
        else:
            Assunto.objects.filter(id=data['id']).update(ativo=False, excluido_por=request.user.servidor,
                                                         data_exclusao=datetime.now())
            Assunto.objects.filter(pai=assunto.pai, ordem__gt=assunto.ordem, ativo=True).update(ordem=F('ordem') - 1)
            cache.delete('assunto.listar:')

    return JsonResponse({'success': not erro, 'erro': erro}, safe=False)


@login_required
@reversion.create_revision(atomic=False)
def mover_assunto(request):
    data = simplejson.loads(request.body)

    try:
        assunto = Assunto.objects.get(id=data['id'], ativo=True)
        irmao = Assunto.objects.get(pai=assunto.pai, ordem=assunto.ordem + data['posicao'], ativo=True)
    except ObjectDoesNotExist:
        return JsonResponse({'success': False, 'erro': 'Assunto e/ou irmão não existe(m).'}, safe=False)

    assunto.ordem = assunto.ordem + data['posicao']
    assunto.save()

    irmao.ordem = irmao.ordem - data['posicao']
    irmao.save()

    msg = 'Assunto "{0}" teve ordem {1} alterada para {2} com Irmão "{3}"'.format(
        assunto.titulo, irmao.ordem,
        assunto.ordem,
        irmao.titulo
    )
    reversion.set_user(request.user)

    reversion.set_comment(msg)

    return JsonResponse({'success': True}, safe=False)


@login_required
def vincular_assuntos(request, atendimento_numero):
    assuntos = simplejson.loads(request.body)
    atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero)
    atendimento.assuntos.clear()
    for assunto in assuntos:
        atendimento.assuntos.add(assunto)
    atendimento.save()
    return JsonResponse({'success': True, 'assuntos': assuntos})


@never_cache
@login_required
@permission_required('atendimento.add_assunto')
@permission_required('atendimento.change_assunto')
@permission_required('atendimento.delete_assunto')
def assuntos_listar(request):
    angular = 'AssuntoCtrl'
    return render(request=request, template_name="atendimento/assunto/listar.html", context=locals())


@login_required
@transaction.atomic
def salvar_atividade(request, atendimento_numero):

    if request.is_ajax():
        dados = simplejson.loads(request.body)
    else:
        dados = request.POST

    if 'atendimentos' in request.POST:
        atendimentos = request.POST.getlist('atendimentos')
    else:
        atendimentos = [atendimento_numero]

    resposta = None
    agora = datetime.now()

    for atendimento_numero in atendimentos:

        atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero)

        atividade = AtendimentoDefensor(
            origem=atendimento,
            cadastrado_por=request.user.servidor,
            tipo=AtendimentoDefensor.TIPO_ATIVIDADE
        )

        if dados.get('finalizar'):
            atividade.finalizado_por = request.user.servidor.defensor
            atividade.data_finalizado = agora
        elif dados.get('reabrir'):
            atividade.finalizado_por = None
            atividade.data_finalizado = None
            atividade.data_atendimento = agora
            atendimento.data_atendimento = None
            atendimento.atendido_por = None
            atendimento.historico = None

        if atendimento.defensoria.nucleo.multidisciplinar:
            form = AtividadeForm(dados, instance=atividade)
        else:
            form = AtividadeDefensorForm(dados, instance=atividade)

        if form.is_valid():

            participantes = []

            # Se multidisciplinar, exije a seleção de pelo menos um participante
            if atendimento.defensoria.nucleo.multidisciplinar or atendimento.defensoria.nucleo.diligencia:

                participantes = request.POST.getlist('participantes')

                if not participantes:
                    resposta = {
                        'success': False,
                        'message': u'Erro ao salvar a atividade, verifique se há participante selecionado!'}
                    break

            atividade = form.save()

            # Adiciona participantes na atividade
            for servidor_id in participantes:

                # Verifica a partir da lotação dos participantes qual é o seu cargo
                atuacao = Atuacao.objects.filter(
                    Q(defensor__servidor__id=servidor_id) &
                    Q(data_inicial__lte=atividade.data_atendimento) &
                    (
                      Q(data_final=None) |
                      Q(data_final__gte=atividade.data_atendimento)
                    )
                ).only('cargo__id').first()

                cargo_id = None

                if atuacao:
                    cargo_id = atuacao.cargo_id

                AtendimentoParticipante.objects.create(
                    atendimento=atividade,
                    servidor_id=servidor_id,
                    cargo_id=cargo_id
                )

            # Valida valor do multiplicador de atividade
            if atendimento.multiplicador < 1 or not atendimento.qualificacao.multiplica_estatistica:
                atendimento.multiplicador = 1

            # Se flag 'finalizar' foi passada, registra a resposta do pedido de apoio como realizada
            if dados.get('finalizar'):

                # Copia informações da atividade para a resposta do pedido de apoio
                atendimento.historico = atividade.historico
                atendimento.atendido_por = request.user.servidor
                atendimento.data_atendimento = agora

                # Se for diligência salva o diligente que finalizou a atividade
                if atendimento.eh_diligencia:
                    defensor_id = Defensor.objects.filter(servidor=request.user.servidor).values('id').first()

                    if not atendimento.defensor_id == defensor_id['id']:
                        atendimento.defensor_id = defensor_id['id']

                atendimento.save()

                tarefa = None
                resposta = None

                tarefa = atualiza_tarefa_atendimento_origem(
                    atendimento=atendimento,
                    resposta=atividade.historico,
                    servidor=request.user.servidor,
                    finalizar=True
                )

                if 'documentos' in request.POST:

                    for documento in request.POST.getlist('documentos'):

                        # vincula documento ao atendimento de resposta de apoio
                        doc_original = AtendimentoDocumento.objects.get(id=documento)
                        doc_original.id = None
                        doc_original.atendimento = atendimento
                        doc_original.save()

                        # vincula documento à tarefa (se existir)
                        if tarefa and resposta:
                            # vincula arquivo a resposta da tarefa
                            if doc_original.arquivo:
                                resposta.documento = doc_original
                                resposta.save()
                            # vincula documento online a tarefa
                            elif doc_original.documento_online:
                                tarefa.documentos.add(doc_original.documento_online)

            elif dados.get('reabrir'):

                atendimento.save()

                atualiza_tarefa_atendimento_origem(
                    atendimento=atendimento,
                    resposta='Solicitação de apoio reaberta',
                    servidor=request.user.servidor,
                    reabrir=True
                )

                # recupera documento do pedido que também esteja vinculado a um processo
                if atendimento.origem:

                    documento = atendimento.origem.documento_set.exclude(
                        documento_online__core_documentos=None
                    ).first()

                    # se existir vinculo com processo, devolve para setor solicitante
                    if documento:

                        processo = documento.documento_online.core_documentos.first().processo
                        evento = processo.eventos.ativos().tipo_encaminhamento().ordem_decrescente().first()
                        sucesso, evento = processo.encaminhar(setor_encaminhado=evento.setor_criacao)

                        if evento:

                            evento.historico = atendimento.historico
                            evento.save()

                            # adiciona documentos da resposta da diligência
                            for documento in atendimento.documento_set.ativos():
                                CoreDocumento.objects.create(
                                    processo=processo,
                                    evento=evento,
                                    documento=documento.documento_online,
                                    arquivo=documento.arquivo,
                                    nome=documento.nome,
                                    tipo=CoreTipoDocumento.objects.first(),  # todo: tipo padrao
                                )

            # limpa árvore de atendimento para atualização de dados
            if hasattr(atendimento.at_inicial, 'arvore'):
                atendimento.at_inicial.arvore.ativo = False
                atendimento.at_inicial.arvore.save()

            resposta = {'success': True, 'atividade': Util.object_to_dict(atividade)}

        else:

            resposta = {
                'success': False,
                'message': u'Erro ao salvar a atividade, verifique se todos campos foram preenchidos corretamente!'}
            break

    if request.is_ajax():

        resposta = JsonResponse(resposta)

    else:

        if not resposta.get('success'):
            messages.error(request, resposta.get('message'))

        if dados.get('next'):
            resposta = redirect(dados.get('next'))
        else:
            resposta = redirect('{}#/atividades'.format(reverse('atendimento_atender', args=[atendimento.numero])))

    return resposta


@login_required
def get_resumo_atividade(request, atendimento_numero):

    atendimento = AtendimentoDefensor.objects.filter(
        numero=atendimento_numero,
        tipo=Atendimento.TIPO_NUCLEO,
        remarcado=None,
        ativo=True).first()

    if atendimento:

        if atendimento.realizado:
            situacao = 'Realizado'
        elif atendimento.atividades.exists():
            situacao = 'Em andamento'
        elif atendimento.participantes.exists():
            situacao = 'Distribuído'
        else:
            situacao = 'Agendado'

        resposta = {
            'situacao': situacao,
            'atividades': [{
                'data_atendimento': atividade.data_atendimento,
                'qualificacao': atividade.qualificacao.titulo,
                'historico': atividade.historico,
            } for atividade in atendimento.atividades.order_by('-data_atendimento')],
            'documentos': [{
                'id': documento.id,
                'nome': documento.nome,
                'arquivo': {
                    'url': documento.arquivo.url,
                } if documento.arquivo else None,
                'documento_online': {
                    'identificador_versao': documento.documento_online.identificador_versao,
                    'url': reverse('documentos:validar-detail', kwargs={'slug': documento.documento_online.pk_uuid})
                } if documento.documento_online else None,
            } for documento in atendimento.documentos.filter(atendimento=atendimento)]
        }

        return JsonResponse({'success': True, 'resumo': resposta})

    return JsonResponse({'success': False})


class VincularDocumentoTarefa(VincularDocumentoBaseView):
    model = Tarefa
    documents_field_name = 'documentos'

    def vinculate(self):
        with transaction.atomic():
            super(VincularDocumentoTarefa, self).vinculate()  # salvei tarefa

            # colocar try except
            try:
                atendimento = AtendimentoDefensor.objects.get(id=self.object.atendimento_id)

                self.object = atendimento.defensoria
                self.documents_field_name = 'documentos'
                try:
                    # vincula documento em atendimento.models.
                    super(VincularDocumentoTarefa, self).vinculate()
                except Exception as e:
                    logger.error(e)

                try:
                    atendimento_documento, criado = AtendimentoDocumento.objects.get_or_create(
                        atendimento=atendimento.at_inicial,
                        documento_online=self.document_object,
                        defaults={
                            'cadastrado_por': self.request.user.servidor,
                            'nome': self.document_object.assunto
                        }
                    )
                except Exception as e:
                    logger.error(e)

            except AtendimentoDefensor.DoesNotExist as e:
                logger.error(e)


class AcompanhamentoIndex(TemplateView):
    template_name = 'atendimento/acompanhamento/index.html'

    def get_context_data(self, **kwargs):
        contexto = super(AcompanhamentoIndex, self).get_context_data(**kwargs)

        if hasattr(self.request.user.servidor, 'defensor'):
            defensor = self.request.user.servidor.defensor
            atuacoes_lst = defensor.atuacoes().filter(
                defensoria__evento=None
            ).vigentes()

        else:

            atuacoes_lst = Atuacao.objects.none()

        contexto['atuacoes_lst'] = atuacoes_lst
        contexto['Atuacao'] = Atuacao
        return contexto


class AcompanhamentoPainel(ListView):
    template_name = 'atendimento/acompanhamento/painel.html'
    context_object_name = 'atendimentos_lst'
    paginate_by = 15

    def get_queryset(self):

        # qs = super(AcompanhamentoIndex, self).get_queryset(request, *args, **kwargs)
        painel = self.kwargs.get('painel')

        if painel == 'sem-peca':
            atendimentos_lst = self.get_atendimento_sem_peca_queryset()
        elif painel == 'peca-digitada':
            atendimentos_lst = self.get_atendimento_peca_digitada_queryset()
        elif painel == 'peca-assinada':
            atendimentos_lst = self.get_atendimento_peca_assinada_queryset()
        elif painel == 'peticionado':
            atendimentos_lst = self.get_atendimento_peticionado_queryset()
        elif painel == "sem-peca-juridica":
            atendimentos_lst = self.get_atendimento_sem_peca_judicial_queryset()
        elif painel == "peticionado-juridica":
            atendimentos_lst = self.get_atendimento_peticionado_judicial_queryset()
        else:
            atendimentos_lst = AtendimentoDefensor.objects.none()

        return atendimentos_lst

    def get(self, request, *args, **kwargs):
        response_original = super(AcompanhamentoPainel, self).get(request, *args, **kwargs)

        return response_original

    def get_atendimento_queryset(self):

        defensoria = self.kwargs.get('defensoria_id')

        atendimentos = AtendimentoDefensor.objects.select_related(
            'qualificacao__area'
        ).annotate(
            processos_judiciais=Sum(
                Case(
                    When(
                        parte__processo__tipo__in=[Processo.TIPO_FISICO, Processo.TIPO_EPROC, Processo.TIPO_PAD],
                        parte__ativo=True,
                        then=Value(1)
                        ),
                    default=Value(0),
                    output_field=IntegerField()))
        ).filter(
            ~Q(data_atendimento=None) &
            Q(Q(tipo=Atendimento.TIPO_INICIAL) | Q(tipo=Atendimento.TIPO_RETORNO)) &
            Q(ativo=True)
        ).order_by(
            '-data_atendimento', 'numero'
        )

        if defensoria:
            atendimentos = atendimentos.filter(
                defensoria=defensoria
            )

        return atendimentos

    def get_atendimento_sem_peca_queryset(self):
        return self.get_atendimento_queryset().annotate(
            pecas=Sum(
                Case(
                    When(
                        ~Q(documento__documento_online=None) &
                        Q(documento__ativo=True),
                        then=Value(1)
                        ),
                    default=Value(0),
                    output_field=IntegerField())),
        ).filter(
            pecas=0,
            processos_judiciais=0
        )

    def get_atendimento_peca_digitada_queryset(self):
        return self.get_atendimento_queryset().filter(
            Q(documento__documento_online__esta_assinado=False) &
            Q(documento__ativo=True) &
            Q(processos_judiciais=0)
        ).distinct()

    def get_atendimento_peca_assinada_queryset(self):
        return self.get_atendimento_queryset().filter(
            Q(documento__documento_online__esta_assinado=True) &
            Q(documento__ativo=True) &
            Q(processos_judiciais=0)
        ).distinct()

    def get_atendimento_peticionado_queryset(self):
        return self.get_atendimento_queryset().filter(
            processos_judiciais__gt=0
        ).distinct()

    def get_atendimento_peticionado_judicial_queryset(self):
        start_date = datetime.today() - timedelta(days=30)
        end_date = datetime.today()
        q = Q(
                Q(exibir_no_painel_de_acompanhamento=True) &
                Q(parte__processo__data_cadastro__range=[start_date, end_date]) &
                Q(processos_judiciais__gt=0)
            )
        return self.get_atendimento_queryset().filter(q).distinct()

    def get_atendimento_sem_peca_judicial_queryset(self):
        q = Q(
                Q(exibir_no_painel_de_acompanhamento=True) &
                Q(retorno__isnull=True) &
                Q(processos_judiciais=0)
            )
        return self.get_atendimento_queryset().filter(q)

    def get_context_data(self, **kwargs):
        contexto = super(AcompanhamentoPainel, self).get_context_data(**kwargs)
        tipo_painel_de_acompanhamento = Defensoria.PAINEL_PADRAO
        painel = self.kwargs.get('painel')
        defensoria_id = self.kwargs.get('defensoria_id')
        exibir_botao_ocultar = False
        if defensoria_id:
            defensoria = Defensoria.objects.get(id=defensoria_id)
            tipo_painel_de_acompanhamento = defensoria.tipo_painel_de_acompanhamento

        if tipo_painel_de_acompanhamento == Defensoria.PAINEL_SIMPLIFICADO:
            # sem_peca = self.get_atendimento_sem_peca_queryset()
            sem_peca_juridica_count = self.get_atendimento_sem_peca_judicial_queryset().count()
            # peticionado = self.get_atendimento_peticionado_queryset()
            peticionado_juridica_count = self.get_atendimento_peticionado_judicial_queryset().count()

            dados_painel_totais = [
                {
                    'texto': 'Atendimentos Aguardando Peça Processual Judicial',
                    'valor': sem_peca_juridica_count,
                    'icone': 'fas fa-clock',
                    'cor': 'bg-red',
                    'url': reverse(
                        'atendimento_acompanhamento_defensoria_painel',
                        kwargs={'defensoria_id': defensoria.id, 'painel': 'sem-peca-juridica'}),
                    'selecionado': painel == "sem-peca-juridica"
                },
                {
                    'texto': 'Atendimentos com Peça Judiciais Protocolada nos Últimos 30 dias',
                    'valor': peticionado_juridica_count,
                    'icone': 'fas fa-check-circle',
                    'cor': 'bg-blue',
                    'url': reverse(
                        'atendimento_acompanhamento_defensoria_painel',
                        kwargs={'defensoria_id': defensoria.id, 'painel': 'peticionado-juridica'}),
                    'selecionado': painel == "peticionado-juridica",
                },
            ]
        else:
            # sem_peca = self.get_atendimento_sem_peca_queryset()
            sem_peca_count = self.get_atendimento_sem_peca_queryset().count()

            # peca_digitada = self.get_atendimento_peca_digitada_queryset()
            peca_digitada_count = self.get_atendimento_peca_digitada_queryset().count()

            # peca_assinada = self.get_atendimento_peca_assinada_queryset()
            peca_assinada_count = self.get_atendimento_peca_assinada_queryset().count()

            # peticionado = self.get_atendimento_peticionado_queryset()
            peticionado_count = self.get_atendimento_peticionado_queryset().count()

            dados_painel_totais = [
                {
                    'texto': 'Atendimentos sem Peça',
                    'valor': sem_peca_count,
                    'icone': 'fas fa-clock',
                    'cor': 'bg-red',
                    'url': reverse(
                        'atendimento_acompanhamento_defensoria_painel',
                        kwargs={'defensoria_id': defensoria.id, 'painel': 'sem-peca'}),
                    'selecionado': painel == "sem-peca",
                },
                {
                    'texto': 'Peças Digitadas',
                    'valor': peca_digitada_count,
                    'icone': 'fas fa-file-alt',
                    'cor': 'bg-yellow',
                    'url': reverse(
                        'atendimento_acompanhamento_defensoria_painel',
                        kwargs={'defensoria_id': defensoria.id, 'painel': 'peca-digitada'}),
                    'selecionado': painel == "peca-digitada",
                },
                {
                    'texto': 'Peças Assinadas',
                    'valor': peca_assinada_count,
                    'icone': 'fas fa-edit',
                    'cor': 'bg-blue',
                    'url': reverse(
                        'atendimento_acompanhamento_defensoria_painel',
                        kwargs={'defensoria_id': defensoria.id, 'painel': 'peca-assinada'}),
                    'selecionado': painel == "peca-assinada",
                },
                {
                    'texto': 'Peças Protocoladas',
                    'valor': peticionado_count,
                    'icone': 'fas fa-check-circle',
                    'cor': 'bg-green',
                    'url': reverse(
                        'atendimento_acompanhamento_defensoria_painel',
                        kwargs={'defensoria_id': defensoria.id, 'painel': 'peticionado'}),
                    'selecionado': painel == "peticionado",
                },
            ]

        if painel == 'sem-peca-juridica':
            exibir_botao_ocultar = True

        contexto['defensoria'] = defensoria
        contexto['painel'] = painel
        contexto['exibir_botao_ocultar'] = exibir_botao_ocultar
        contexto['totais'] = dados_painel_totais
        contexto['Atendimento'] = AtendimentoDefensor
        return contexto


def atendimento_indeferimento_form(request, atendimento_numero, classe_tipo, form_id, form_action):

    atendimento = get_object_or_404(AtendimentoDefensor, numero=atendimento_numero, ativo=True)

    classes = CoreClasse.objects.ativos().order_by(
        'nome_norm'
    ).distinct(
        'nome_norm'
    ).filter(
        tipo=classe_tipo
    )

    q = Q(ativo=True)
    q &= Q(all_atuacoes__tipo=Atuacao.TIPO_TITULARIDADE)
    q &= Q(all_atuacoes__ativo=True)

    if classe_tipo == CoreClasse.TIPO_IMPEDIMENTO:
        q &= Q(nucleo__indeferimento_pode_receber_impedimento=True)
    elif classe_tipo == CoreClasse.TIPO_SUSPEICAO:
        q &= Q(nucleo__indeferimento_pode_receber_suspeicao=True)
    elif classe_tipo == CoreClasse.TIPO_NEGACAO:
        q &= Q(nucleo__indeferimento_pode_receber_negacao=True)

    setores = Defensoria.objects.filter(
        q
    ).order_by(
        'numero',
        'nome',
        'comarca__nome'
    )

    return render(
        request,
        template_name="atendimento/atender_modal_indeferimento_form.html",
        context={
            'atendimento': atendimento,
            'classes': classes,
            'setores': setores,
            'form_id': form_id,
            'form_action': form_action,
        })


@login_required
def atendimento_indeferimento_impedimento_form(request, atendimento_numero):
    from indeferimento.forms import NovoImpedimentoForm

    atendimento = get_object_or_404(AtendimentoDefensor, numero=atendimento_numero, ativo=True)

    return render(
        request,
        template_name="atendimento/atender_modal_indeferimento_form.html",
        context={
            'atendimento': atendimento,
            'form': NovoImpedimentoForm(atendimento=atendimento),
            'form_id': 'ImpedimentoForm',
            'form_action': reverse('indeferimento:novo_impedimento'),
        })


@login_required
def atendimento_indeferimento_suspeicao_form(request, atendimento_numero):
    from indeferimento.forms import NovaSuspeicaoForm

    atendimento = get_object_or_404(AtendimentoDefensor, numero=atendimento_numero, ativo=True)

    return render(
        request,
        template_name="atendimento/atender_modal_indeferimento_form.html",
        context={
            'atendimento': atendimento,
            'form': NovaSuspeicaoForm(atendimento=atendimento),
            'form_id': 'SuspeicaoForm',
            'form_action': reverse('indeferimento:nova_suspeicao'),
        })


@login_required
def atendimento_indeferimento_negacao_procedimento_form(request, atendimento_numero):
    from indeferimento.forms import NovaNegacaoProcedimentoForm

    atendimento = get_object_or_404(AtendimentoDefensor, numero=atendimento_numero, ativo=True)

    return render(
        request,
        template_name="atendimento/atender_modal_indeferimento_form.html",
        context={
            'atendimento': atendimento,
            'form': NovaNegacaoProcedimentoForm(atendimento=atendimento),
            'form_id': 'NegacaoProcedimentoForm',
            'form_action': reverse('indeferimento:nova_negacao_procedimento'),
        })


@login_required
def atendimento_indeferimento_negacao_form(request, atendimento_numero):
    """Utilizado para a renderização da modal de Indeferimento dentro da página de Atendimento"""

    from indeferimento.forms import NovaNegacaoForm

    atendimento = get_object_or_404(AtendimentoDefensor, numero=atendimento_numero, ativo=True)

    return render(
        request,
        template_name="atendimento/atender_modal_indeferimento_form.html",
        context={
            'atendimento': atendimento,
            'form': NovaNegacaoForm(atendimento=atendimento),
            'form_id': 'NegacaoForm',
            'form_action': reverse('indeferimento:nova_negacao'),
        })


@login_required
def atendimento_visualizacao_body(request, atendimento_numero):

    atendimento = get_object_or_404(AtendimentoDefensor, numero=atendimento_numero, ativo=True)

    return render(
        request,
        template_name="atendimento/atender_modal_visualizacao_body.html",
        context={
            'atendimento': atendimento,
        })


@login_required
def listar_forma_atendimento_defensor(request):

    formasAtendimento = FormaAtendimento.objects.vigentes_defensor()

    arr = []
    for formaAtendimento in formasAtendimento:
        arr.append({
            'id': formaAtendimento.id,
            'nome': formaAtendimento.nome,
        })

    return JsonResponse(arr, safe=False)


@login_required
@permission_required('atendimento.add_atendimento')
def salvar_oficio(request, atendimento_numero):
    if request.is_ajax():
        dados = simplejson.loads(request.body)
    else:
        dados = request.POST

    if dados:

        atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero)

        anotacao_oficio = AtendimentoDefensor.objects.create(
            origem=atendimento,
            inicial=atendimento.at_inicial,
            cadastrado_por=request.user.servidor,
            atendido_por=request.user.servidor,
            data_atendimento=datetime.now(),
            tipo=AtendimentoDefensor.TIPO_OFICIO,
            oficio=True,
            detalhes=atendimento.detalhes
        )

        if request.FILES:

            documento = AtendimentoDocumento(
                atendimento=anotacao_oficio,
                data_enviado=datetime.now(),
                enviado_por=request.user.servidor)

            form = DocumentoForm(request.POST, request.FILES, instance=documento)

            if form.is_valid():
                form.save()

        if hasattr(atendimento.at_inicial, 'arvore'):
            atendimento.at_inicial.arvore.ativo = False
            atendimento.at_inicial.arvore.save()

        if request.is_ajax():
            return JsonResponse({'success': True, 'anotacao': Util.object_to_dict(anotacao_oficio)})

    else:

        msg = 'Erro ao salvar oficio!'

        if request.is_ajax():
            return JsonResponse({'success': False, 'message': msg})
        else:
            messages.error(request, msg)

    if request.POST.get('next'):
        return redirect(request.POST['next'])
    else:
        return redirect('atendimento_atender', atendimento_numero)


class DocumentoAtendimentoGedViewSet(mixins.UpdateModelMixin,
                                     mixins.RetrieveModelMixin,
                                     mixins.ListModelMixin,
                                     DetailSerializerMixin,
                                     GenericViewSet):

    serializer_class = DocumentoAtendimentoSerializer
    queryset = DocumentoAtendimento.objects.all()
    serializer_detail_class = DocumentoAtendimentoSerializer
    permission_classes = [IsAuthenticated]

    def partial_update(self, request, *args, **kwargs):
        documento = DocumentoAtendimento.objects.get(id=kwargs['pk'])
        documento_ged = documento.documento_online
        defensoria = Defensoria.objects.get(id=request.data['defensoria'])
        documento_ged.assinaturas.filter(
            grupo_assinante=documento_ged.grupo_dono,
        ).update(
            grupo_assinante_nome=defensoria.nome,
            grupo_assinante=defensoria
        )
        documento_ged.grupo_dono = defensoria
        documento_ged.save()
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


@never_cache
@login_required
def listar_vulnerabilidades(request, atendimento_numero):
    vulnerabilidades = {
        'json': {
            'possui_vulnerabilidade': False,
            'vulnerabilidade': []
        }
    }
    if request.is_ajax():
        data = request.body
        atendimento_id = data.decode("utf-8")

        if settings.SIGLA_UF.upper() == 'AM':
            try:
                with connection.cursor() as cursor:
                    cursor.callproc('vul_consultar', [request.user.id, 'SOLAR', atendimento_id])
                    dados = cursor.fetchone()[0]
                    vulnerabilidades = simplejson.loads(dados)
            except Exception as err:
                return JsonResponse({'error': str(err)}, status=500)
        else:
            lista_vulnerabilidades = TipoVulnerabilidade.objects.ativos().values('id', 'nome', 'descricao')
            vulnerabilidades_atendimento = list(
                    AtendimentoVulnerabilidade.objects.filter(
                        atendimento=atendimento_id,
                        ).distinct().values_list('vulnerabilidade_id', flat=True)
                )
            for v in lista_vulnerabilidades:
                v['status'] = True if v['id'] in vulnerabilidades_atendimento else False
                v['vulnerabilidade_id'] = v['id']
                vulnerabilidades['json']['vulnerabilidade'].append(v)
            vulnerabilidades['json']['possui_vulnerabilidade'] = True if len(vulnerabilidades_atendimento) > 0 else False  # noqa: E501

        vulnerabilidades['mensagem'] = config.MENSAGEM_VULNERABILIDADE_DIGITAL
    return JsonResponse(vulnerabilidades)


@never_cache
@login_required
def salvar_vulnerabilidades(request, atendimento_numero):
    dados_vulnerabilidade = []
    response = {}
    status = None

    if request.is_ajax():
        data = simplejson.loads(request.body)
        atendimento_id = data['atendimento_id']

        dados_vulnerabilidade = [
            {
                'status': vul['status'],
                'vulnerabilidade_id': vul['vulnerabilidade_id']
            } for vul in data['vulnerabilidades']
        ]

        if settings.SIGLA_UF.upper() == 'AM':
            dados_vulnerabilidade = str(dados_vulnerabilidade).replace("'", '"')
            try:
                with connection.cursor() as cursor:
                    cursor.callproc('vul_salvar', [request.user.id, 'SOLAR', atendimento_id, dados_vulnerabilidade])
                    data = cursor.cursor.fetchone()[0]
                    log_db = simplejson.loads(data)
                    sucesso = log_db['sucesso'].upper() == "S"
                    response = {'error': not sucesso, 'msg': log_db['motivo']}
                    status = 500 if response['error'] else 200
            except Exception as err:
                response = {'error': True, 'msg': err}
                status = 500
        else:
            ids_vul_existentes = list(AtendimentoVulnerabilidade.objects.filter(
                atendimento_id=atendimento_id).values_list('vulnerabilidade_id', flat=True))

            for vul_atendimento in dados_vulnerabilidade:
                # se a vulnerabilidade está marcada e ainda não existir no banco, ela é adicionada
                if vul_atendimento['status'] and vul_atendimento['vulnerabilidade_id'] not in ids_vul_existentes:
                    AtendimentoVulnerabilidade.objects.create(
                        atendimento_id=atendimento_id,
                        vulnerabilidade_id=vul_atendimento['vulnerabilidade_id']
                    )
                # se a vulnerabilidade está desmarcada e existe no banco, é removida do banco
                elif not vul_atendimento['status'] and vul_atendimento['vulnerabilidade_id'] in ids_vul_existentes:
                    AtendimentoVulnerabilidade.objects.filter(
                        atendimento_id=atendimento_id,
                        vulnerabilidade_id=vul_atendimento['vulnerabilidade_id']
                    ).delete()
            response = {'error': False}
            status = 200
    return JsonResponse(response, status=status)


class PastaDocumentoViewSet(ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = PastaDocumento.objects.all()
    serializer_class = PastaDocumentoSerializer

    def perform_create(self, serializer):
        """
            Atualiza o atendimento para inicial caso seja um atendimento de retorno
        """
        atendimento_inicial = serializer.validated_data['atendimento'].inicial
        if atendimento_inicial:
            serializer.save(atendimento=atendimento_inicial)
        else:
            serializer.save()

    def get_queryset(self):
        queryset = self.queryset
        atendimento = self.request.query_params.get('atendimento')
        if not atendimento:
            return queryset
        atendimento = Atendimento.objects.filter(id=int(atendimento)).first()
        atendimento_inicial = atendimento.inicial or atendimento
        return queryset.filter(atendimento=atendimento_inicial)
