# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import json as simplejson
import math
import re
import uuid
from copy import copy
from datetime import date, datetime, time, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import F, Max, Prefetch, Q
from django.db.models.functions import Length
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.generic import RedirectView, TemplateView

import reversion
# Bibliotecas de terceiros
from constance import config
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

# Solar
from atendimento.atendimento.models import Acesso, Atendimento
from atendimento.atendimento.models import Defensor as AtendimentoDefensor
from atendimento.atendimento.models import Documento as DocumentoAtendimento
from atendimento.atendimento.models import Pessoa as AtendimentoPessoa
from contrib import constantes
from contrib.models import Defensoria, Servidor, Util
from contrib.utils import validar_cnpj, validar_cpf
from defensor.models import Defensor
from evento.models import Evento

# Modulos locais
from .forms import (
    AtendimentoForm,
    AudienciaForm,
    BuscarProcessoAudienciaForm,
    BuscarProcessoForm,
    DocumentoFaseForm,
    FaseForm,
    HonorarioFaseForm,
    RealizarAudienciaForm
)
from .models import (
    Acao,
    Audiencia,
    DocumentoFase,
    Fase,
    FaseTipo,
    Manifestacao,
    Parte,
    ParteHistoricoSituacao,
    Processo
)
from .services import ProcessoService


@login_required
@permission_required('processo.view_processo')
def acessar(request):
    if request.method == 'POST':

        request.session['id_eproc'] = request.POST['id_eproc']
        request.session['senha_eproc'] = request.POST['senha_eproc']

        return redirect(request.POST['next'])

    else:

        if 'id_eproc' in request.session:
            del request.session['id_eproc']

        if 'senha_eproc' in request.session:
            del request.session['senha_eproc']

        return redirect(request.GET['next'])


@login_required
@permission_required('processo.delete_parte')
def excluir_parte(request, processo_numero, parte_id):

    partes = Parte.objects.filter(
        id=parte_id,
        processo__numero_puro=processo_numero,
        ativo=True
    )

    for parte in partes:
        parte.excluir(excluido_por=request.user.servidor)

    if request.GET.get('next'):
        messages.success(request, u'Processo excluído com sucesso!')
        return redirect(request.GET.get('next'))
    else:
        return JsonResponse({'error': False})


@login_required
@permission_required('processo.change_parte')
def transferir_parte(request):

    if request.method == 'POST':

        parte_id = request.POST.get('parte')
        atendimento_numero_destino = request.POST.get('atendimento_numero_destino')

        if atendimento_numero_destino and parte_id:
            parte = Parte.objects.filter(id=parte_id).only('id').first()

            atendimento_numero_destino = atendimento_numero_destino.replace('.', '')
            atendimento_destino = AtendimentoDefensor.objects.filter(
                numero=atendimento_numero_destino,
                ativo=True
            ).only(
                'id'
            ).first()

            sucesso = False

            if atendimento_destino and parte:
                sucesso = parte.transferir_atendimento(atendimento_destino.id, request.user)

            if sucesso:
                messages.success(request, u'Processo transferido com sucesso!')
                return redirect(
                    '{}#/processos/'.format(reverse('atendimento_atender', args=[atendimento_numero_destino]))
                )
            else:
                messages.error(request, u'Erro ao transferir processo. Verifique o Atendimento de destino!')
                return redirect(request.META.get('HTTP_REFERER', '/'))


@never_cache
@login_required
def get_json_permissao_processo_botoes(request, parte_id):
    """Utilizado para o tratamento de renderização dos botões das ações da aba Processo da Ficha de Atendimento.
            Botão de transferir parte.
        """

    sucesso = False
    pode_transferir_parte = False

    if parte_id:
        parte = Parte.objects.filter(id=parte_id).only('id').first()

        if parte:
            pode_transferir_parte = parte.permissao_transferir(request.user)
            sucesso = True

    permissao_botoes_acoes = {
        'pode_transferir_parte': pode_transferir_parte
    }

    return JsonResponse({
        'sucesso': sucesso,
        'permissao_botoes': permissao_botoes_acoes
    })


@login_required
@permission_required('processo.delete_fase')
def excluir_fase(request, fase_id):

    request.session['fase_id'] = None

    fase = Fase.objects.filter(id=fase_id, ativo=True).first()

    if fase:
        fase.excluir(request.user.servidor)

    if request.GET.get('next'):

        if fase is not None:
            messages.success(request, u'Fase processual excluída com sucesso!')
        else:
            messages.error(request, u'Erro ao excluir: fase processual não existe!')

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    else:

        return JsonResponse({'error': fase is None, 'success': fase is not None})


@login_required
@permission_required('processo.delete_documentofase')
def excluir_documento_fase(request, documento_id):
    try:
        documento = DocumentoFase.objects.get(id=documento_id, ativo=True)
        documento.excluir()
        error = False
    except ObjectDoesNotExist:
        error = True

    if request.GET.get('next'):

        if error:
            messages.error(request, u'Erro ao excluir: documento não existe!')
        else:
            messages.success(request, u'Documento excluído com sucesso!')

        return redirect(request.GET.get('next'))

    else:

        return JsonResponse({'error': error})


@login_required
@reversion.create_revision(atomic=False)
@permission_required('processo.add_processo')
def salvar(request):

    if request.method == 'POST':

        if request.is_ajax():
            dados = simplejson.loads(request.body)
        else:
            dados = request.POST

        from .services import salvar_processo

        try:
            sucesso, processo, parte, atendimento = salvar_processo(dados, request.user.servidor, request.user)

        except IntegrityError:
            messages.error(request, u'Não foi possível salvar o processo! Informações inconsistentes.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        if sucesso:

            if request.is_ajax():
                return JsonResponse({'success': True, 'processo': processo.id, 'parte': parte.id})

            if 'next' in dados:
                return redirect(dados['next'])
            else:
                if atendimento.tipo == Atendimento.TIPO_PROCESSO:
                    return redirect('recepcao_atendimento', atendimento.numero)
                else:
                    return redirect(request.META.get('HTTP_REFERER', '/'))

    if request.is_ajax():
        return JsonResponse({'success': False})
    else:
        if not config.ATIVAR_ESAJ:
            messages.error(request, u'Não foi possível salvar o processo! Informações inconsistentes.')
        return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@reversion.create_revision(atomic=False)
@permission_required('processo.add_processo')
def salvar_extra(request):
    if request.method == 'POST':

        atendimento = None
        numero_processo_de_origem = None
        dados = request.POST

        if 'numero_processo' in dados and dados.get('numero_processo') != '':
            numero_processo_de_origem = dados.get('numero_processo')

        if 'atendimento_numero' in dados:
            atendimento = get_object_or_404(AtendimentoDefensor, numero=dados.get('atendimento_numero'))
        else:

            dados_atendimento = {
                'defensor': dados.get('defensor'),
                'defensoria': dados.get('defensoria'),
                'modificado_por': request.user.servidor,
            }

            atendimento = AtendimentoDefensor(tipo=Atendimento.TIPO_PROCESSO, cadastrado_por=request.user.servidor)

            form = AtendimentoForm(dados_atendimento, instance=atendimento)

            if form.is_valid():
                atendimento = form.save()
                Acesso.conceder_publico(atendimento, None)

        if atendimento:

            if dados.get('id'):

                processo = Processo.objects.get(id=dados.get('id'))
                processo.acao_id = dados.get('acao')

                if settings.SIGLA_UF.upper() == 'RN':
                    processo.area_id = dados.get('area')

                reversion.set_user(request.user)
                reversion.set_comment(Util.get_comment_save(request.user, processo, False))

            else:
                # gera um número aleatório para gravar no banco
                numero_temporario = str(uuid.uuid4())

                dados_processo = {
                    'numero': numero_temporario,
                    'numero_puro': numero_temporario,
                    'tipo': Processo.TIPO_EXTRA,
                    'comarca': atendimento.comarca,
                    'area_id': atendimento.qualificacao.area_id if atendimento.qualificacao else None,
                    'acao_id': dados.get('acao'),
                    'ativo': True
                }

                if settings.SIGLA_UF.upper() == 'RN':
                    dados_processo['area_id'] = dados.get('area')

                processo = Processo.objects.create(**dados_processo)

                defensor_id = dados.get('defensor') if dados.get('defensor') else None

                parte = Parte.objects.create(
                    processo=processo,
                    atendimento=atendimento,
                    defensoria=atendimento.defensoria,
                    defensoria_cadastro=atendimento.defensoria,
                    defensor_id=defensor_id,
                    defensor_cadastro_id=defensor_id,
                    ativo=True)

                # Gera número sequencial único para processos extrajudiciais
                numero = processo.gerar_numero(parte)
                numero_puro = processo.gerar_numero_inteiro(numero)

                # Se o número de processo extrajudicial de origem foi informado, usa para exibição
                if numero_processo_de_origem:
                    numero = numero_processo_de_origem
                    # Concatena número gerado com número de exibição para permitir buscas
                    numero_puro = ''.join((numero_puro, processo.gerar_numero_inteiro(numero_processo_de_origem, 20)))

                processo.numero = numero
                processo.numero_puro = numero_puro
                processo.save()

                reversion.set_user(request.user)
                reversion.set_comment(Util.get_comment_save(request.user, parte, True))

            if dados.get('next'):
                return redirect(dados.get('next'))
            else:
                if atendimento.tipo == Atendimento.TIPO_PROCESSO:
                    return redirect('recepcao_atendimento', atendimento.numero)
                else:
                    return redirect(request.META.get('HTTP_REFERER', '/'))

    messages.error(request, u'Não foi possível salvar o processo! Informações inconsistentes.')
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@permission_required('processo.add_fase')
def salvar_fase(request):
    from processo.honorarios.models import Honorario

    if request.method == 'POST':

        if request.is_ajax():
            dados = simplejson.loads(request.body)
        else:
            dados = request.POST.copy()

        if 'atendimento' in dados and dados['atendimento']:
            atendimento = Atendimento.objects.get(numero=dados['atendimento'])
            dados['parte'] = atendimento.processo_parte.id

        if 'id' in dados and dados['id']:

            fase = Fase.objects.get(id=dados['id'])
            dados['processo'] = fase.processo_id
            dados['parte'] = fase.parte_id

            if fase.automatico:
                dados['data_protocolo'] = fase.data_protocolo

        if 'tipo' in dados and dados['tipo']:
            tipo = FaseTipo.objects.get(id=dados['tipo'])
        else:
            tipo = FaseTipo.objects.none()

        if 'custodia' not in dados or not tipo.audiencia or dados['audiencia_realizada'] == 'false':
            dados['custodia'] = Audiencia.CUSTODIA_NAO_APLICA

        if tipo and tipo.audiencia:
            if 'id' in dados and dados['id']:
                form = AudienciaForm(dados, instance=Audiencia.objects.get(id=dados['id']))
            else:
                form = AudienciaForm(dados, instance=Audiencia(cadastrado_por=request.user.servidor))
        else:
            if 'id' in dados and dados['id']:
                form = FaseForm(dados, instance=Fase.objects.get(id=dados['id']))
            else:
                form = FaseForm(dados, instance=Audiencia(cadastrado_por=request.user.servidor))

        if form.is_valid():

            fase = form.save(commit=False)

            if tipo.audiencia and fase.audiencia_realizada:
                fase.baixado_por = request.user.servidor
                fase.data_baixa = datetime.now()

            fase.save()

            if tipo.sentenca:

                if hasattr(fase, 'honorario'):
                    form = HonorarioFaseForm(dados, instance=fase.honorario, prefix='honorario')
                else:
                    honorario = Honorario(fase=fase, cadastrado_por=request.user.servidor)
                    form = HonorarioFaseForm(dados, instance=honorario, prefix='honorario')

                if form.is_valid():
                    form.save()

            if request.is_ajax():
                return JsonResponse({'success': True, 'id': fase.id})
            else:
                request.session['fase_id'] = fase.id
                messages.success(request, u'Fase Processual Cadastrada com sucesso!')

        else:

            if request.is_ajax():
                return JsonResponse({'success': False, 'errors': [({'field': k, 'message': v[0]}) for k, v in form.errors.items()]})  # noqa: E501
            else:
                messages.error(request, u'Não foi possível salvar a Fase Processual!')
                for k, v in form.errors.items():
                    messages.error(request, u'{0}: {1}'.format(k, v[0]))

        if request.POST.get('next'):
            return redirect(request.POST.get('next'))

    if request.GET.get('next'):
        return redirect(request.GET.get('next'))


@login_required
@permission_required('processo.add_documentofase')
def salvar_documento_fase(request):
    if request.method == 'POST':

        salvar_documento_fase_pre(request)
        return redirect(request.POST['next'])

    else:
        raise Http404


@login_required
@permission_required('processo.add_documentofase')
def salvar_documento_fase_pre(request, fase=None):
    if fase is None:
        fase = Fase.objects.get(id=request.POST.get('fase'))
        request.session['fase_id'] = fase.id

    if request.method == 'POST':

        if request.FILES or request.POST.get('documento_ged'):
            if request.FILES:
                documento = DocumentoFase(fase=fase)
                documento.enviado_por = Servidor.objects.get(usuario_id=request.user.id)
                form = DocumentoFaseForm(request.POST, request.FILES, instance=documento)
                form.documento_online = None
                if form.is_valid():
                    form.save()
            if request.POST.get('documento_ged'):
                documento_atendimento = DocumentoAtendimento.objects.get(id=request.POST.get('documento_ged'))
                documento_online = DocumentoFase(fase=fase)
                documento_online.enviado_por = Servidor.objects.get(usuario_id=request.user.id)
                request.POST = request.POST.copy()
                request.POST['nome'] = documento_atendimento.nome
                form_ged = DocumentoFaseForm(request.POST, instance=documento_online)
                if form_ged.is_valid():
                    data = form_ged.save(commit=False)
                    data.documento_atendimento = documento_atendimento
                    data.save()
            messages.success(request, u'Documento anexado com sucesso!')
            return True
        else:
            messages.error(request, 'Não foi possível anexar arquivos! Verifique se todos os dados foram informados corretamente.')  # noqa: E501
            return None

    messages.error(request,
                   u'Não foi possível anexar arquivos! Verifique se todos os dados foram informados corretamente.')
    return None


@login_required
@permission_required('processo.view_documentofase')
def listar_documento_fase(request):
    pass


@never_cache
@login_required
@permission_required('processo.view_fase')
def listar_fases(request, processo_numero):

    grau = request.GET.get('grau')
    processo = Processo.objects.filter(numero_puro=processo_numero, grau=grau, ativo=True).first()

    fases = []
    for fase in processo.lista_fases().order_by('-data_protocolo', '-data_cadastro'):

        # Se tipo audiencia, carrega objeto da audiencia
        if hasattr(fase, 'audiencia') and fase.tipo.audiencia:
            fase = Audiencia.objects.get(id=fase.id)

        registro = Util.object_to_dict(fase, {})
        fases.append(registro)

        # Carrega dados adicionais
        registro['tipo'] = {'id': fase.tipo.id, 'nome': fase.tipo.nome} if fase.tipo else None

        registro['defensoria'] = {
            'id': fase.defensoria.id,
            'nome': fase.defensoria.nome,
            'codigo': fase.defensoria.codigo,
        } if fase.defensoria else None

        registro['defensor_cadastro'] = {'id': fase.defensor_cadastro.id,
                                         'nome': fase.defensor_cadastro.nome} if fase.defensor_cadastro else None

        # Carrega dados do substituto, se houver
        if fase.defensor_substituto:
            registro['defensor_substituto'] = {'id': fase.defensor_substituto.id,
                                               'nome': fase.defensor_substituto.nome}

        registro['bloqueado'] = fase.bloqueado

        documentos_list = []
        for documento in fase.documentos():
            documentos_list.append({
                'id': documento.id,
                'fase': documento.fase_id,
                'tipo': documento.tipo_id,
                'arquivo': documento.arquivo.name if documento.arquivo else '',
                'arquivo_url': documento.arquivo.url if documento.arquivo else '',
                'documento_atendimento': {
                    'id': documento.documento_atendimento_id,
                    'nome': documento.documento_atendimento.nome,
                    'arquivo': documento.documento_atendimento.arquivo.name if documento.documento_atendimento.arquivo else '', # noqa
                    'arquivo_url': documento.documento_atendimento.arquivo.url if documento.documento_atendimento.arquivo else '', # noqa
                    'documento_online': {
                        'pk_uuid': documento.documento_atendimento.documento_online.pk_uuid,
                        'assunto': documento.documento_atendimento.documento_online.assunto,
                    } if documento.documento_atendimento.documento_online else None,
                } if documento.documento_atendimento else None,
                'nome': documento.nome,
                'eproc': documento.eproc,
                'ativo': documento.ativo,
                'data_enviado': documento.data_enviado,
                'enviado_por': documento.enviado_por_id,
            })
        registro['documentos'] = documentos_list
        registro['peticao_inicial'] = (fase == processo.peticao_inicial)

        if fase.cadastrado_por:
            registro['cadastrado_por'] = {'id': fase.cadastrado_por.id,
                                          'nome': fase.cadastrado_por.nome,
                                          'username': fase.cadastrado_por.usuario.username}

        if fase.parte:
            registro['parte'] = {
                'id': fase.parte.id,
                'atendimento': fase.parte.atendimento.numero,
                'requerente': fase.parte.atendimento.requerente.nome if fase.parte.atendimento.requerente else None
            }

    return JsonResponse(fases, safe=False)


@login_required
def listar_fase_tipo(request):
    cache_key = 'processo.listar_fase_tipo:'
    # TODO: verificar tipo de cache_data - fabio.cb
    cache_data = cache.get(cache_key)

    if not cache_data:
        cache_data = Util.json_serialize(FaseTipo.objects.ativos().distinct('nome').order_by('nome'))
        cache.set(cache_key, cache_data, 60 * 60 * 24 * 30)  # cache 1 mes

    return JsonResponse(cache_data, safe=False)


@login_required
@permission_required('processo.change_audiencia')
def realizar_audiencia(request, audiencia_id):

    if request.method == 'POST':

        dados = simplejson.loads(request.body)
        audiencia = Audiencia.objects.filter(id=audiencia_id, ativo=True).first()

        if audiencia is not None:
            form = RealizarAudienciaForm(dados, instance=audiencia)

            if form.is_valid():
                audiencia = form.save(commit=False)
            else:
                return JsonResponse({'success': False, 'errors': [({'field': k, 'message': v[0]}) for k, v in form.errors.items()]})  # noqa: E501

            audiencia.realizar(
                descricao=dados['descricao'],
                custodia=dados['custodia'],
                baixado_por=request.user.servidor,
            )

            return JsonResponse({'error': False, 'success': True})

    return JsonResponse({'error': True, 'success': False})


@login_required
@permission_required('processo.change_audiencia')
@reversion.create_revision(atomic=False)
def remanejar_audiencia(request):

    if request.method == 'POST' and request.is_ajax():

        dados = simplejson.loads(request.body)

        for registro in dados['registros']:

            audiencia = Audiencia.objects.get(id=registro)

            if not audiencia.audiencia_realizada:
                audiencia.defensor_cadastro_id = dados['defensor_cadastro']
                audiencia.save()

        reversion.set_user(request.user)
        reversion.set_comment('Audiência remanejada por {0}'.format(request.user.get_full_name()))

        return JsonResponse({'error': False, 'success': True})

    return JsonResponse({'error': True, 'success': False})


@never_cache
@login_required
@permission_required('processo.view_audiencia')
def listar_audiencias(request):

    if request.method == 'POST':

        registros = []
        numero_registros = 25
        filtro = simplejson.loads(request.body)
        form = BuscarProcessoAudienciaForm(filtro)

        if form.is_valid():

            filtro_numero = re.sub('[^0-9]', '', form.cleaned_data['filtro'])

            if form.cleaned_data['data_ini'] and form.cleaned_data['data_fim']:

                data_ini = form.cleaned_data['data_ini']
                data_fim = form.cleaned_data['data_fim']
                data_fim = datetime.combine(data_fim, time.max)

                if data_ini <= data_fim.date():

                    lista_audiencias = Audiencia.objects.filter(
                        Q(data_protocolo__gte=data_ini) &
                        Q(data_protocolo__lte=data_fim) &
                        Q(ativo=True) &
                        Q(tipo__audiencia=True)
                    ).values(
                        'id',
                        'tipo',
                        'tipo__nome',
                        'descricao',
                        'processo__numero',
                        'processo__numero_puro',
                        'processo__grau',
                        'processo__vara__nome',
                        'processo__vara__codigo_eproc',
                        'processo__area__nome',
                        'processo__acao__nome',
                        'processo__comarca_id',
                        'processo__comarca__nome',
                        'parte__atendimento__id',
                        'parte__atendimento__inicial_id',
                        'parte__atendimento__numero',
                        'parte__defensoria__nome',
                        'parte__defensoria__codigo',
                        'data_protocolo',
                        'data_termino_protocolo',
                        'defensoria',
                        'defensoria__nome',
                        'defensoria__codigo',
                        'defensor_cadastro',
                        'defensor_cadastro__servidor__nome',
                        'audiencia_status',
                        'audiencia_realizada',
                    ).order_by('data_protocolo', 'processo__numero')

                    if filtro.get('defensor'):

                        defensor = Defensor.objects.filter(id=filtro.get('defensor')).first()

                        # Se o id passado foi de um defensor, filtra por todas audiências vinculadas a ele
                        if defensor.eh_defensor:
                            lista_audiencias = lista_audiencias.filter((
                                Q(defensor_cadastro=defensor) |
                                Q(defensor_substituto=defensor)
                            ))
                        # Se assessor, filtra audiêcias de todas as defensorias onde está lotado
                        else:
                            lista_audiencias = lista_audiencias.filter(
                                Q(defensoria__in=set(defensor.atuacoes(vigentes=True).values_list('defensoria_id', flat=True)))  # noqa: E501
                            )

                    if filtro.get('defensoria'):

                        defensoria = Defensoria.objects.get(id=filtro.get('defensoria'))

                        lista_audiencias = lista_audiencias.filter(
                            Q(defensoria=defensoria) |
                            (
                                Q(defensoria=None) &
                                (
                                    Q(parte__defensoria=defensoria) |
                                    (
                                        Q(parte__defensoria=None) &
                                        Q(processo__comarca=defensoria.comarca)
                                    )
                                )
                            )
                        )

                    if filtro_numero:
                        lista_audiencias = lista_audiencias.filter(
                            Q(processo__numero_puro__icontains=filtro_numero)
                        )

                    primeiro = filtro.get('pagina') * numero_registros
                    ultimo = primeiro + numero_registros

                    if filtro.get('pagina') == 0:
                        filtro['total'] = lista_audiencias.count()
                        filtro['paginas'] = math.ceil(float(filtro.get('total')) / numero_registros)

                    lista_audiencias = lista_audiencias[primeiro:ultimo]

                    hoje = datetime(date.today().year, date.today().month, 1)

                    for audiencia in lista_audiencias:

                        # TODO: Criar nova coluna nome de exição para substituir o tratamento abaixo
                        if audiencia['processo__vara__nome']:
                            audiencia['processo__vara__nome'] = re.sub('Juízo d(a|o) ', '', audiencia['processo__vara__nome'])  # noqa: E501

                        inicial = audiencia['parte__atendimento__id']
                        if audiencia['parte__atendimento__inicial_id']:
                            inicial = audiencia['parte__atendimento__inicial_id']

                        pessoas = AtendimentoPessoa.objects.filter(
                            atendimento=inicial,
                            tipo=AtendimentoPessoa.TIPO_REQUERENTE,
                            responsavel=True,
                            ativo=True
                        ).values('pessoa_id', 'pessoa__nome', 'tipo', 'responsavel')[:1]

                        audiencia['pessoas'] = list(pessoas)
                        audiencia['editavel'] = audiencia['data_protocolo'] >= hoje

                        registros.append(audiencia)

        servidor = request.user.servidor
        supervisores = None
        defensorias = None

        if hasattr(servidor, 'defensor'):
            supervisores = list(servidor.defensor.lista_supervisores.values_list('id', flat=True))
            defensorias = list(servidor.defensor.defensorias.values_list('id', flat=True))

        return JsonResponse(
            {
                'usuario': {
                    'comarca': int(request.session.get('comarca', request.user.servidor.comarca_id)),
                    'defensor': servidor.defensor.id if hasattr(servidor, 'defensor') else None,
                    'supervisores': supervisores,
                    'defensorias': defensorias,
                },
                'registros': registros,
                'pagina': filtro.get('pagina'),
                'paginas': filtro.get('paginas', 0),
                'ultima': filtro.get('pagina') == filtro.get('paginas') - 1 if filtro.get('paginas') else True,
                'total': filtro.get('total'),
            }, safe=False)

    form = BuscarProcessoAudienciaForm(request.GET)
    angular = 'BuscarAudienciaCtrl'

    hoje = date.today()
    diaMin = date(hoje.year, hoje.month, 1)

    evento_desbloqueio = Evento.get_desbloqueio_vigente_por_usuario(usuario=request.user.servidor.defensor).first()
    if (evento_desbloqueio is not None):
        diaMin = date(evento_desbloqueio.data_ini.year,
                      evento_desbloqueio.data_ini.month,
                      evento_desbloqueio.data_ini.day
                      )
    else:
        diaMin = date(hoje.year, hoje.month, 1)
    if hoje.day <= config.DIA_LIMITE_CADASTRO_FASE:
        diaMin -= relativedelta(months=1)

    return render(request=request, template_name="processo/audiencias.html", context=locals())


@login_required
@permission_required('processo.view_processo')
def listar(request):

    if request.method == 'POST' and request.is_ajax():

        numero_registros = 25
        filtro = simplejson.loads(request.body)
        form = BuscarProcessoForm(filtro)

        if form.is_valid():

            filtro_texto = form.cleaned_data['filtro'].strip()

            filtro_norm = Util.normalize(filtro_texto)
            filtro_numero = re.sub('[^0-9]', '', filtro_texto)
            filtro_cpf = False

            q = Q(ativo=True)

            # Verifica se número é um CPF/CNPJ válido
            if len(filtro_numero) == 11 and validar_cpf(filtro_numero):
                filtro_cpf = True
            elif len(filtro_numero) == 14 and validar_cnpj(filtro_numero):
                filtro_cpf = True

            if filtro_numero and not filtro_cpf:  # NUMERO DE PROCESSO:

                lista_processos = Processo.objects.filter(
                    numero_puro__icontains=filtro_numero,
                    ativo=True,
                    parte__ativo=True,
                    parte__atendimento__ativo=True
                ).values_list(
                    'id',
                    'numero',
                    'comarca__nome',
                    'area__nome',
                    'vara__nome',
                    'vara__codigo_eproc',
                    'acao__nome',
                    'numero_puro',
                    'grau',
                ).order_by(
                    'numero_puro'
                )

            else:

                if filtro_cpf:  # CPF ou CNPJ do Assistido

                    q &= Q(pessoa__cpf=filtro_numero)

                elif filtro_norm:  # Nome do Assistido

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

                # TODO implementar Bloqueio de Maria

                # busca por defensoria a partir da atuação do defensor
                if form.cleaned_data['defensor']:
                    defensor = form.cleaned_data['defensor']
                    q &= Q(atendimento__defensor__parte__defensoria__in=defensor.defensorias.values_list('id', flat=True))  # noqa: E501

                # busca por defensoria
                if form.cleaned_data['defensoria']:
                    q &= Q(atendimento__defensor__parte__defensoria=form.cleaned_data['defensoria'])

                if form.cleaned_data['data_ini'] and form.cleaned_data['data_fim']:
                    q &= Q(atendimento__defensor__parte__processo__fases__data_protocolo__range=[
                        form.cleaned_data['data_ini'],
                        form.cleaned_data['data_fim']
                    ])

                q &= Q(atendimento__ativo=True)
                q &= Q(atendimento__defensor__parte__ativo=True)
                q &= Q(atendimento__defensor__parte__processo__ativo=True)

                lista_processos = AtendimentoPessoa.objects.filter(q).values_list(
                    'atendimento__defensor__parte__processo__id',
                    'atendimento__defensor__parte__processo__numero',
                    'atendimento__defensor__parte__processo__comarca__nome',
                    'atendimento__defensor__parte__processo__area__nome',
                    'atendimento__defensor__parte__processo__vara__nome',
                    'atendimento__defensor__parte__processo__vara__codigo_eproc',
                    'atendimento__defensor__parte__processo__acao__nome',
                    'atendimento__defensor__parte__processo__numero_puro',
                    'atendimento__defensor__parte__processo__grau',
                ).order_by(
                    'atendimento__defensor__parte__processo__numero_puro'
                )

                if config.ATIVAR_ACOMPANHAMENTO_PROCESSO and form.cleaned_data['situacao']:
                    situacao = int(form.cleaned_data['situacao'])
                    if situacao in [status[0] for status in ParteHistoricoSituacao.LISTA_STATUS_ACOMPANHAMENTO]:
                        lista_processos = lista_processos.filter(
                            Q(atendimento__defensor__parte__situacao_atual=situacao)
                        )

            lista_processos = lista_processos.distinct()

            primeiro = filtro['pagina'] * numero_registros
            ultimo = primeiro + numero_registros

            if filtro['pagina'] == 0:
                filtro['total'] = lista_processos.count()
                filtro['paginas'] = math.ceil(float(filtro['total']) / numero_registros)

            lista_processos = lista_processos[primeiro:ultimo]

            lista_processos = [
                {
                    'id': v[0],
                    'numero': v[1],
                    'comarca__nome': v[2],
                    'area__nome': v[3],
                    'vara__nome': v[4],
                    'vara__codigo_eproc': v[5],
                    'acao__nome': v[6],
                    'numero_puro': v[7],
                    'grau': v[8],
                } for v in lista_processos]

            processos = []
            for processo in lista_processos:

                partes = Parte.objects.filter(
                    Q(processo=processo['id']) &
                    Q(ativo=True) &
                    (
                        (
                            Q(atendimento__partes__ativo=True) &
                            Q(atendimento__partes__responsavel=True) &
                            Q(atendimento__partes__tipo=AtendimentoPessoa.TIPO_REQUERENTE) &
                            Q(atendimento__inicial=None)
                        ) |
                        (
                            Q(atendimento__inicial__partes__ativo=True) &
                            Q(atendimento__inicial__partes__responsavel=True) &
                            Q(atendimento__inicial__partes__tipo=AtendimentoPessoa.TIPO_REQUERENTE) &
                            ~Q(atendimento__inicial=None)
                        ) |
                        (
                            Q(atendimento__partes=None) &
                            Q(atendimento__inicial__partes=None)
                        )
                    )
                ).values(
                    'id',
                    'parte',
                    'situacao_atual',
                    'defensoria__nome',
                    'atendimento__numero',
                    'atendimento__tipo',
                    'atendimento__partes__pessoa__id',
                    'atendimento__partes__pessoa__nome',
                    'atendimento__partes__pessoa__apelido',
                    'atendimento__partes__pessoa__nome_social',
                    'atendimento__partes__pessoa__tipo',
                    'atendimento__inicial__numero',
                    'atendimento__inicial__tipo',
                    'atendimento__inicial__partes__pessoa__id',
                    'atendimento__inicial__partes__pessoa__nome',
                    'atendimento__inicial__partes__pessoa__apelido',
                    'atendimento__inicial__partes__pessoa__nome_social',
                    'atendimento__inicial__partes__pessoa__tipo',
                )

                processo['partes'] = []
                for parte in partes:

                    requerente_id = None
                    requerente_nome = None
                    requerente_nome_social = None
                    requerente_apelido = None

                    numero = parte['atendimento__numero']
                    if numero is None:
                        numero = parte['atendimento__inicial__numero']

                    tipo = parte['atendimento__tipo']
                    if tipo is None:
                        tipo = parte['atendimento__inicial__tipo']

                    # preenche o tipo_pessoa para preenchimento de nome social e nome fantasia
                    requerente_tipo_pessoa = parte['atendimento__partes__pessoa__tipo']
                    if requerente_tipo_pessoa is None:
                        requerente_tipo_pessoa = parte['atendimento__inicial__partes__pessoa__tipo']

                    # tratamento para mostrar nome em caso de Pessoa Física ou Jurídica
                    if requerente_tipo_pessoa == constantes.TIPO_PESSOA_FISICA:
                        # preenchimento de dados de Pessoa Física

                        requerente_nome = requerente_nome = parte['atendimento__partes__pessoa__nome']
                        if not requerente_nome:
                            requerente_nome = requerente_nome = parte['atendimento__inicial__partes__pessoa__nome']

                        requerente_nome_social = parte['atendimento__partes__pessoa__nome_social']
                        if not requerente_nome_social:
                            requerente_nome_social = parte['atendimento__inicial__partes__pessoa__nome_social']

                    else:
                        # preenchimento de dados de Pessoa Jurídica

                        requerente_nome = parte['atendimento__partes__pessoa__nome']
                        if not requerente_nome:
                            requerente_nome = parte['atendimento__inicial__partes__pessoa__nome']

                        requerente_apelido = parte['atendimento__partes__pessoa__apelido']
                        if not requerente_apelido:
                            requerente_apelido = parte['atendimento__inicial__partes__pessoa__apelido']

                    requerente_id = parte['atendimento__partes__pessoa__id']
                    if requerente_id is None:
                        requerente_id = parte['atendimento__inicial__partes__pessoa__id']

                    processo['partes'].append({
                        'id': parte['id'],
                        'parte': parte['parte'],
                        'situacao_atual': parte['situacao_atual'],
                        'defensoria': parte['defensoria__nome'],
                        'atendimento': {
                            'numero': numero,
                            'tipo': tipo,
                            'requerente': {
                                'id': requerente_id,
                                'nome': requerente_nome,
                                'apelido': requerente_apelido,
                                'nome_social': requerente_nome_social,
                                'tipo': requerente_tipo_pessoa
                            },
                        },
                    })

                processos.append(processo)

        else:

            processos = []

        return JsonResponse(
            {
                'processos': processos,
                'pagina': filtro['pagina'],
                'paginas': filtro['paginas'] if 'paginas' in filtro else 0,
                'ultima': filtro['pagina'] == filtro['paginas'] - 1 if 'paginas' in filtro else True,
                'total': filtro['total'],
                'LISTA': {
                    'PARTE': dict(Parte.LISTA_TIPO),
                }
            }, safe=False)

    form = BuscarProcessoForm(request.GET)

    angular = 'BuscarProcessoCtrl'

    sigla_uf = settings.SIGLA_UF.upper()

    ativar_acompanhamento_processo = config.ATIVAR_ACOMPANHAMENTO_PROCESSO

    sistemas_webservices_procapi = []

    if config.ATIVAR_PROCAPI:
        from procapi_client.services import APISistema
        sistemas_webservices_procapi = APISistema().listar_todos()

    return render(request=request, template_name="processo/listar.html", context=locals())


@never_cache
@login_required
def get_json(request, processo_numero):

    eproc_json = None
    processo_json = None
    grau = request.GET.get('grau')
    pode_preencher_classe_comarca_vara = False

    processos = Processo.objects.filter(numero_puro=processo_numero, ativo=True).order_by('id')

    if grau and grau.isdigit():
        processos = processos.filter(grau=grau)

    if processos:

        processo = processos[0]

        processo_json = Util.object_to_dict(processo, {})
        processo_json['keys'] = copy(processo_json)
        processo_json['partes'] = []
        processo_json['assuntos'] = []
        processo_json['comarca'] = {'id': processo.comarca.id,
                                    'nome': processo.comarca.nome} if processo.comarca else None
        processo_json['vara'] = {'id': processo.vara.id, 'nome': processo.vara.nome} if processo.vara else None
        processo_json['area'] = {'id': processo.area.id, 'nome': processo.area.nome} if processo.area else None
        processo_json['acao'] = {'id': processo.acao.id, 'nome': processo.acao.nome} if processo.acao else None
        processo_json['tipo'] = {'id': processo.tipo, 'nome': processo.LISTA_TIPO[processo.tipo][1]}

        for item in processo.processoassunto_set.all():
            processo_json['assuntos'].append({
                'codigo_cnj': item.assunto.codigo_cnj,
                'nome': item.assunto.nome,
                'principal': item.principal

            })

        processo_json['tipos_status'] = {

            'EM_ANDAMENTO': ParteHistoricoSituacao.STATUS_EM_ANDAMENTO,
            'SOBRESTADO': ParteHistoricoSituacao.STATUS_SOBRESTADO,
            'FINALIZADO': ParteHistoricoSituacao.STATUS_FINALIZADO
        }

        for parte in Parte.objects.filter(processo=processo, ativo=True).order_by('data_cadastro'):

            parte_json = Util.object_to_dict(parte, {})

            parte_json['keys'] = Util.object_to_dict(Parte.objects.get(id=parte.id), {})
            parte_json['parte'] = {'tipo': parte.parte, 'nome': parte.LISTA_TIPO[parte.parte][1]}

            if parte.atendimento:
                parte_json['atendimento'] = parte.atendimento.numero
                parte_json['atendimento_inicial'] = parte.atendimento.at_inicial.numero
                parte_json['requerente'] = parte.atendimento.requerente.pessoa.nome if parte.atendimento.requerente else None  # noqa: E501
                parte_json['requerido'] = parte.atendimento.requerido.pessoa.nome if parte.atendimento.requerido else None  # noqa: E501

            parte_json['cadastrado_por'] = {'id': parte.cadastrado_por.id,
                                            'nome': parte.cadastrado_por.nome} if parte.cadastrado_por else None
            parte_json['defensor'] = {'id': parte.defensor.id, 'nome': parte.defensor.nome} if parte.defensor else None
            parte_json['defensoria'] = {'id': parte.defensoria.id, 'nome': parte.defensoria.nome} if parte.defensoria else None  # noqa: E501
            parte_json['defensor_cadastro'] = {'id': parte.defensor_cadastro.id, 'nome': parte.defensor_cadastro.nome} if parte.defensor_cadastro else None  # noqa: E501
            parte_json['defensoria_cadastro'] = {'id': parte.defensoria_cadastro.id, 'nome': parte.defensoria_cadastro.nome} if parte.defensoria_cadastro else None  # noqa: E501
            parte_json['bloqueado'] = True if not processo.pre_cadastro and parte.data_cadastro.date() < date(date.today().year, date.today().month, 1) else False  # noqa: E501

            parte_json['prisoes'] = list(processo.prisoes.filter(parte=parte, ativo=True).values_list('id', flat=True))

            processo_json['partes'].append(parte_json)

        eproc_json = {
            'data': datetime.now(),
            'sucesso': True,
            'mensagem': None,
            'processo': None,
            'existe': True
        }

    else:

        processo = Processo(numero=processo_numero, grau=grau)

        if processo.get_tipo() == Processo.TIPO_EPROC and config.ATIVAR_PROCAPI:

            usuario_requisicao = None
            if config.PROCAPI_ATIVAR_INFORMAR_PERFIL_PROJUDI:
                usuario_requisicao = request.user.servidor.defensor.usuario_eproc

            servico = ProcessoService(processo, request)
            sucesso, resposta = servico.api.consultar(
                usuario_requisicao=usuario_requisicao
            )

            # Verificação Padrão
            existe = sucesso

            # Caso aconteça alguma indisponibilidade no MNI ou
            # O processo não foi localidade por motivo de a DPE não estar habilitado e ser sigiloso
            # Então permite realizar cadastro mesmo assim, caso esteja habilitado este comportamento
            # No painel de configurações do SOLAR
            if (not existe and config.PERMITE_CADASTRAR_PROCESSO_NAO_LOCALIZADO_OU_COM_ERRO_WEBSERVICE_DO_TJ and ('server error' in resposta.lower() or 'não encontrado' in resposta.lower())):  # noqa: E501
                existe = True
                pode_preencher_classe_comarca_vara = True

            eproc_json = {
                'data': datetime.now(),
                'sucesso': sucesso,
                'mensagem': resposta if not sucesso else None,
                'mensagens': servico.api.messages,
                'processo': resposta if sucesso else None,
                'existe': existe,
            }

    resposta = {
        'error': (processo_json is None),
        'eproc': eproc_json,
        'processo': processo_json,
        'ATIVAR_ESAJ': config.ATIVAR_ESAJ,
        'pode_preencher_classe_comarca_vara': pode_preencher_classe_comarca_vara,
        'ativar_acompanhamento_processo': config.ATIVAR_ACOMPANHAMENTO_PROCESSO,
    }

    return JsonResponse(resposta)


@login_required
def get_json_fase(request, fase_id):
    try:
        fase = Fase.objects.get(id=fase_id, ativo=True)
    except ObjectDoesNotExist:
        return JsonResponse({'error': True})

    return JsonResponse({'error': False, 'fase': Util.object_to_dict(fase)})


@login_required
def listar_acao(request):
    cache_key = 'processo.listar_acao:'
    # TODO: verificar tipo de cache_data - fabio.cb
    cache_data = cache.get(cache_key)

    if not cache_data:
        cache_data = Util.json_serialize(Acao.objects.filter(ativo=True).order_by('nome'))
        cache.set(cache_key, cache_data, 60 * 60 * 24 * 30)  # cache 1 mes

    return JsonResponse(cache_data, safe=False)


@login_required
def set_pendentes_relogio(request):

    if request.GET.get('closed') == 'true':
        request.session['processo_pendente_relogio'] = datetime.now() + timedelta(minutes=5)
    else:
        request.session['processo_pendente_relogio'] = datetime.now()

    return JsonResponse({}, safe=False)


@login_required
def get_pendentes_por_defensor(request, defensor_id):

    hora_agora = datetime.now()
    hora_expiracao = request.session.get('processo_pendente_relogio', datetime.now())

    if hora_expiracao > hora_agora:
        hora_expiracao = (hora_expiracao - hora_agora).seconds
    else:
        hora_expiracao = 0

    cache_key = 'processo_pendentes_defensor:{0}'.format(defensor_id)
    cache_data = cache.get(cache_key)
    cache_data_mes = cache.get(cache_key + ':mes')
    cache_data_vara = cache.get(cache_key + ':vara')

    if not cache_data or not cache_data_mes or not cache_data_vara:

        cache_data = []

        defensor = Defensor.objects.get(id=defensor_id)

        if defensor.eh_defensor:
            defensores = [defensor.id]
        else:
            defensores = list(defensor.lista_supervisores.values_list('id', flat=True))

        processos = Processo.objects.filter(
            situacao=Processo.SITUACAO_MOVIMENTO,
            pre_cadastro=True,
            ativo=True,
            parte__defensor__in=defensores,
            parte__ativo=True,
        ).annotate(
            max_data_protocolo=Max('fases__data_protocolo')
        ).values_list(
            'numero_puro',
            'acao__nome',
            'comarca__nome',
            'vara__codigo_eproc',
            'parte_pre_cadastro',
            'max_data_protocolo',
            'vara__codigo_eproc',
            'acao__penal',
            'chave',
            'grau'
        )

        processos = processos.filter(fases__data_protocolo__gte=date(date.today().year, 1, 1))

        varas = Processo.objects.filter(
            situacao=Processo.SITUACAO_MOVIMENTO,
            pre_cadastro=True,
            ativo=True,
            parte__defensor__in=defensores,
            parte__ativo=True,
            fases__data_protocolo__gte=F('comarca__data_implantacao')
        ).order_by(
            'comarca__nome', 'vara__nome'
        ).values_list(
            'vara__codigo_eproc',
            'vara__nome'
        ).distinct(
            'comarca__nome',
            'vara__codigo_eproc',
            'vara__nome'
        )

        meses = {}

        for processo in processos:
            mes = None
            if processo[5]:
                mes = processo[5].strftime('%Y%m')
                if mes not in meses:
                    meses[mes] = processo[5].strftime('%m/%Y')

            nome = processo[4] if processo[4] else 'Nome não informado'
            cache_data.append({
                'numero': processo[0],
                'acao': processo[1],
                'comarca': processo[2],
                'vara': processo[3],
                'parte_nome': nome.replace("'", '').replace('"', ''),
                'ultima_movimentacao': processo[5],
                'penal': processo[7],
                'chave': processo[8],
                'grau': processo[9],
                'mes_referencia': mes
            })

        cache_data_mes = []
        for mes in meses:
            cache_data_mes.append({'key': mes, 'value': meses[mes]})

        cache_data_vara = []
        for vara in varas:
            cache_data_vara.append({'id': vara[0], 'nome': vara[1]})

        cache.set(cache_key, cache_data)
        cache.set(cache_key + ':mes', cache_data_mes)
        cache.set(cache_key + ':vara', cache_data_vara)
    data = {
        'hora_expiracao': hora_expiracao,
        'processos': cache_data,
        'meses': cache_data_mes,
        'varas': cache_data_vara
    }
    return JsonResponse(data=data, safe=True)


def numero_processos_com_atualizacao_pendentes(request):
    agora = timezone.now()
    if request.user.is_authenticated:
        processos = Processo.objects.annotate(
            numero_len=Length('numero_puro')
        ).filter(
            tipo=Processo.TIPO_EPROC,
            numero_len=20,
            atualizado=False,
            ativo=True
        )

        total_nao_atualizado = processos.count()
        total_atualizando = processos.filter(
            atualizando=True
        ).count()

        ret = JsonResponse(
            data={
                'total_nao_atualizado': total_nao_atualizado,
                'total_atualizando': total_atualizando,
                'dt_consulta': agora
            }
        )
    else:
        ret = JsonResponse(
            data={
                'not_authenticated': True,
                'total_nao_atualizado': None,
                'total_atualizando': None,
                'dt_consulta': agora
            },
            status=401,
        )

    return ret


class IdentificarView(RedirectView):
    '''
    Identifica processo pelo número e cpf/cnpj da parte e redireciona para página de acompanhamento
    '''
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        numero = self.request.GET.get('numero')
        grau = self.request.GET.get('grau')
        aviso = self.request.GET.get('aviso')
        cpf = self.request.GET.get('cpf')
        tab = self.request.GET.get('tab', 'eproc')

        # Se número do processo e cpf/cnpj do assistido foram informados, procura por parte correspondente
        # Se existe parte, retorna URL da aba do processo no atendimento
        parte = self.__obter_processo_parte(
            numero_processo=numero,
            grau_processo=grau,
            numero_documento=cpf
        )

        if parte and tab and aviso:
            # Opção de ver peticionamento
            # Verifica se parte tem manifestação vinculada ao aviso ou com situação em análise
            manifestacao = Manifestacao.objects.filter(
                Q(parte=parte) &
                (
                    Q(avisos__numero=aviso) &
                    Q(situacao=Manifestacao.SITUACAO_ANALISE)
                )
            ).ativos().first()

            # Se existe manifestação vinculada, redireciona pra página de peticionamento
            if manifestacao:
                messages.warning(self.request, '<b>Já existe um peticionamento para este processo!</b> \
                                                Selecione o prazo desejado e clique em "Peticionar".')
                return reverse('peticionamento:visualizar', kwargs={'pk': manifestacao.id})

            # Senão tem manifestação, redireciona pra aba de documentos do atendimento relacionado ao processo
            messages.warning(self.request, '<b>Não existe um peticionamento para este processo!</b> \
                                            Selecione um documento GED e clique em "Peticionar".')
            return '{}#/{}'.format(
                reverse('atendimento_atender', args=[parte.atendimento.numero]),
                tab
            )
        elif parte and tab and not aviso:
            # Opção de ver processo da aba especificada
            return '{}#/{}/{}/grau/{}'.format(
                reverse('atendimento_atender', args=[parte.atendimento.numero]),
                tab,
                parte.processo.numero_puro,
                parte.processo.grau,
            )
        elif not parte:
            # Opção de visualizar processo do MNI.
            return reverse('processo_visualizar', kwargs={'processo_numero': numero, 'processo_grau': grau})

        # Caso não de match em nehnuma consulta anterior, buscar processo na lista de procesos.
        return '{}?filtro={}'.format(reverse('processo_listar'), numero)

    def __obter_processo_parte(self, numero_processo, grau_processo, numero_documento=None):
        """
            Função para obtenção da das partes do processo.

            Parêmetro
            ---------

            numero_processo : str
                Número puro do processo.

            numero_documento : str
                Número do documento da parte destinatária da intimação(Geralmente CPF e RG)

            Retorno
            -------
            Parte -> A parte destinatária da intimação.
        """

        parte = Parte.objects.filter(
            Q(processo__numero_puro=numero_processo) &
            Q(processo__grau=grau_processo) &
            (
                (
                    Q(atendimento__partes__ativo=True) &
                    Q(atendimento__partes__tipo=AtendimentoPessoa.TIPO_REQUERENTE) &
                    (
                        Q(atendimento__partes__pessoa__cpf=numero_documento) |
                        Q(atendimento__partes__pessoa__rg_numero=numero_documento)
                    )
                ) |
                (
                    Q(atendimento__inicial__partes__ativo=True) &
                    Q(atendimento__inicial__partes__tipo=AtendimentoPessoa.TIPO_REQUERENTE) &
                    (
                        Q(atendimento__inicial__partes__pessoa__cpf=numero_documento) |
                        Q(atendimento__inicial__partes__pessoa__rg_numero=numero_documento)
                    )
                )
            )
        ).first()

        return parte


@login_required
def salvar_situacao_parte(request):
    try:
        if request.is_ajax() and request.method == 'POST':
            data = simplejson.loads(request.body)

            processo_parte_id = data['processo_parte_id']
            status = data['tipo_status']
            data_inicio = datetime.strptime(data['data_inicio'], '%d/%m/%Y') if data['data_inicio'] else None
            data_fim = datetime.combine(parse(data['data_fim']), time.max) if data['data_fim'] else None
            motivo = data['motivo']

            hoje = datetime.today()

            if data_inicio and data_inicio.date() != hoje.date():
                raise Exception('Data do cliente é diferente da data do servidor')

            parte = Parte.objects.get(id=processo_parte_id)

            # desativa o último status salvo
            ultima_situacao_parte = ParteHistoricoSituacao.objects.filter(
                parte__id=parte.id,
                desativado_em__isnull=True
            ).order_by('id').last()

            if ultima_situacao_parte:
                ultima_situacao_parte.desativado_em = hoje
                ultima_situacao_parte.desativado_por = request.user
                ultima_situacao_parte.save()

            # adiciona um novo status para a parte do processo
            nova_situacao_parte = ParteHistoricoSituacao.objects.create(
                parte=parte,
                status=status,
                motivo=motivo,
                inicio_sobrestamento=data_inicio,
                fim_sobrestamento=data_fim,
            )

            # atualiza a situacao_atual da Parte do processo
            if nova_situacao_parte:
                parte.situacao_atual = nova_situacao_parte.status
                parte.save()

            return JsonResponse({
                'success': True,
                'novo_status': nova_situacao_parte.status
            })
        else:
            raise Exception('Request failed')
    except simplejson.JSONDecodeError:
        return JsonResponse({'success': False, 'msg': 'Os dados recebidos são inválidos'})
    except ObjectDoesNotExist:
        return JsonResponse({'success': False, 'msg': 'Informações inconsistente. Tente novamente!'})
    except Exception as ex:
        return JsonResponse({'success': False, 'msg': ex.args[0]})


@login_required
def get_partes_processos(request):

    parte_info = {}
    lista_parte_info = []
    hoje = datetime.today()
    data_inicio_acompanhamento = hoje - timedelta(days=config.DIAS_ACOMPANHAMENTO_PROCESSO)

    if request.method == 'POST' and request.is_ajax():
        defensor = request.user.servidor.defensor
        ids_defensorias = set(
            defensor.atuacoes(vigentes=True).values_list('defensoria_id', flat=True)
        )

        partes = Parte.objects.filter(
            Q(defensoria__id__in=ids_defensorias) &
            (
                Q(data_cadastro__gte=data_inicio_acompanhamento) |
                Q(modificado_em__gte=data_inicio_acompanhamento)
            ) &
            Q(atendimento__ativo=True) &
            Q(ativo=True)
        ).select_related(
            'processo',
            'processo__acao',
            'atendimento',
            'defensoria'
        ).prefetch_related(
            Prefetch('historico_situacao', queryset=ParteHistoricoSituacao.objects.filter(
                desativado_em__isnull=True,
            ).order_by('-cadastrado_em'), to_attr='historico'),
            Prefetch('atendimento__partes', AtendimentoPessoa.objects.select_related(
                'pessoa'
            ).filter(responsavel=True).order_by('id'), to_attr='parte_requerente')
        )

        for parte in partes:

            atrasado = (
                True
                if parte.historico and
                parte.historico[0].status == ParteHistoricoSituacao.STATUS_SOBRESTADO and
                parte.historico[0].fim_sobrestamento < hoje
                else False
            )

            parte_info = {
                'id': parte.id,
                'situacao_atual': parte.situacao_atual,
                'atrasado': atrasado,
                'situacao': {
                    'fim_sobrestamento': parte.historico[0].fim_sobrestamento if parte.historico else None,
                    'cadastrado_em': parte.historico[0].cadastrado_em if parte.historico else None,
                    'motivo': parte.historico[0].motivo if parte.historico else None
                },
                'processo': {
                    'numero': parte.processo.numero,
                    'numero_puro': parte.processo.numero_puro,
                    'acao_nome': parte.processo.acao.nome if parte.processo.acao else None,
                    'grau': parte.processo.grau,
                    'parte_display': parte.get_parte_display()
                },
                'atendimento': {
                    'numero': parte.atendimento.numero,
                    'requerente_nome': (parte.atendimento.parte_requerente[0].nome
                                        if parte.atendimento.parte_requerente else None)
                },
                'defensoria': {
                    'nome': parte.defensoria.nome
                }
            }
            lista_parte_info.append(parte_info)

        return JsonResponse(lista_parte_info, safe=False)

    return JsonResponse({'success': False})


class VisualizarView(TemplateView):
    template_name = 'processo/visualizar.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context.update({
            'pode_visualizar_aba': True,
            'config': config,
            'angular': 'VisualizarCtrl',
        })

        return context
