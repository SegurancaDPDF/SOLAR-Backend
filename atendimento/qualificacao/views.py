# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import json as simplejson
import re

# Bibliotecas de terceiros
import reversion
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import redirect, render

# Solar
from atendimento.atendimento.forms import QualificacaoModalForm
from atendimento.atendimento.models import Defensor as AtendimentoDefensor
from atendimento.atendimento.models import Atendimento, Qualificacao
from contrib.models import Util, Area
from api.api_v1.utils import restringir_qualificacao


@login_required
@permission_required('atendimento.view_qualificacao')
def buscar(request, atendimento_numero=None):
    """
    Busca de qualificações
    :param request:
    :return:
    """
    if request.method == 'POST':

        data = simplejson.loads(request.body)

        if data['query'] or data['area']:

            if atendimento_numero:
                atendimento = AtendimentoDefensor.objects.filter(numero=atendimento_numero).first()
            else:
                atendimento = None

            qualificacoes = Qualificacao.objects.pedidos().ativos().filter(
                exibir_em_atendimentos=True,
                orgao_encaminhamento__isnull=True
            )

            if data['query']:
                qualificacoes = qualificacoes.filter(titulo_norm__icontains=Util.normalize(data['query']))

            if data['area']:
                qualificacoes = qualificacoes.filter(area=data['area']['id'])

            qualificacoes = qualificacoes.order_by(
                'titulo_norm', 'area__nome'
            ).values(
                'id', 'titulo', 'area__nome', 'nucleo__nome', 'especializado__nome',
                'texto', 'perguntas', 'documentos', 'defensorias'
            )
            defensorias_id = request.user.servidor.defensor.defensorias.values_list('id', flat=True)
            qualificacoes = restringir_qualificacao(qualificacoes, defensorias_id)
            if (atendimento and atendimento.tipo != Atendimento.TIPO_LIGACAO and
                    not request.user.has_perm('atendimento.encaminhar_atendimento_para_qualquer_area')):
                qualificacoes = qualificacoes.filter(
                    area__in=atendimento.defensoria.areas.all()
                )

            return JsonResponse(list(qualificacoes), safe=False)
        return JsonResponse({}, safe=False)
    else:
        return redirect('index', )


@login_required
@permission_required('atendimento.view_qualificacao')
@reversion.create_revision(atomic=False)
def index(request, ligacao_numero=None):
    request.session['qualificacao_id'] = None
    titulo = ''

    if request.GET.get('next'):
        next = request.GET.get('next')

    if request.method == 'POST':

        form = QualificacaoModalForm(request.POST)

        if form.is_valid():
            qualificacao = form.save(commit=False)
            qualificacao.save()

            reversion.set_user(request.user)
            reversion.set_comment(Util.get_comment_save(request.user, qualificacao, True))

    form = QualificacaoModalForm()

    if ligacao_numero:

        ligacao = Atendimento.objects.get(numero=ligacao_numero)

        if ligacao.tipo != Atendimento.TIPO_LIGACAO:
            request.session['atendimento_id'] = ligacao.id
        else:
            request.session['ligacao_id'] = ligacao.id

        if request.session.get('atendimento_processo_numero'):
            atendimento_processo = AtendimentoDefensor.objects.filter(
                numero=request.session.get('atendimento_processo_numero')
            ).first()
            if atendimento_processo:
                titulo = atendimento_processo.processo.acao
        elif ligacao.qualificacao:
            titulo = ligacao.qualificacao.titulo

    angular = 'BuscarQualificacaoModel'

    return render(request=request, template_name="atendimento/qualificacao/index.html", context=locals())


@login_required
@permission_required('atendimento.view_qualificacao')
def qualificar(request, qualificacao_id):
    """
    Armazena id da qualificação e redireciona para próxima etapa
    :param request:
    :param qualificacao_id:
    :return:
    """

    request.session['qualificacao_id'] = qualificacao_id
    request.session['processo_id'] = None

    processo_numero = request.GET.get('processo_numero')
    processo_grau = request.GET.get('processo_grau')

    if processo_numero:
        from processo.processo.models import Processo
        from processo.processo.tasks import procapi_atualizar_processo

        processo_numero_puro = re.sub('[^0-9]', '', processo_numero)

        # Cria/Recupera cadastro do processo
        processo, _ = Processo.objects.get_or_create(
            numero_puro=processo_numero_puro,
            grau=processo_grau,
            defaults={
                'tipo': Processo.TIPO_EPROC,
                'numero': processo_numero,
                'cadastrado_por': request.user.servidor,
                'ativo': True
            })

        # Cria tarefa no celery para atualizar dados do processo
        procapi_atualizar_processo.apply_async(kwargs={
            'numero': processo_numero_puro,
            'grau': processo_grau
        }, queue='sobdemanda')

        request.session['processo_id'] = processo.id

    if request.GET.get('next'):
        # redireciona para a pagina especificada
        return redirect(request.GET.get('next'))
    else:
        # redireciona para o agendamento
        return redirect('agendamento_index')


@login_required
def listar(request, penal=False, nucleo_id=None, tipo=Qualificacao.TIPO_PEDIDO):

    if request.method == 'POST' and request.is_ajax():
        data = simplejson.loads(request.body)
    else:
        data = {'penal': penal, 'nucleo': nucleo_id, 'tipo': tipo}

    qualificacoes = Qualificacao.objects.filter(ativo=True)

    if 'penal' in data and data['penal']:
        qualificacoes = qualificacoes.filter(area__penal=True)

    if 'nucleo' in data and data['nucleo']:
        qualificacoes = qualificacoes.filter(nucleo=data['nucleo'])

    if 'tipo' in data and data['tipo']:
        qualificacoes = qualificacoes.filter(tipo=data['tipo'])

    qualificacoes = qualificacoes.order_by(
        'titulo_norm', 'area__nome'
    ).distinct(
        'titulo_norm', 'area__nome'
    ).values(
        'id', 'titulo', 'area', 'tipo', 'multiplica_estatistica'
    )

    areas = {}
    for area in Area.objects.filter(ativo=True).order_by('nome').values('id', 'nome'):
        areas[area['id']] = area

    return JsonResponse({'qualificacoes': list(qualificacoes), 'areas': areas}, safe=False)


@login_required
def listar_nucleo(request, nucleo_id):
    return listar(request, nucleo_id=nucleo_id)


@login_required
@permission_required('atendimento.view_qualificacao')
def visualizar(request):
    """
    Retorna JSON com dados da qualificação solicitada
    :param request:
    :return:
    """

    if request.method == 'POST':

        data = simplejson.loads(request.body)
        retorno = {}

        if data['id'] != '':
            q = Qualificacao.objects.get(id=data['id'])

            retorno = {
                'id': q.id,
                'area': q.area.nome,
                'area_id': q.area_id,
                'titulo': q.titulo,
                'texto': '<br>'.join(q.texto.split('\n')) if q.texto else None,
                'perguntas': '<br>'.join(q.perguntas.split('\n')) if q.perguntas else None,
                'documentos': '<br>'.join(q.documentos.split('\n')) if q.documentos else None}

        return JsonResponse(retorno)
