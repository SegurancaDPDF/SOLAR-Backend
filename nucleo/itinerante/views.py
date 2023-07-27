# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import json as simplejson
import logging
from datetime import date, datetime, time

# Bibliotecas de terceiros
import reversion
from django.conf import settings
from django.db.models import Q, Prefetch
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Solar
from atendimento.atendimento.models import Defensor as AtendimentoDefensor
from relatorios.models import Local, Relatorio

# Modulos locais
from contrib.models import Defensoria, Estado, Municipio, Servidor, Util
from defensor.models import Atuacao
from evento.models import Agenda
from .forms import EventoForm
from .models import Evento

logger = logging.getLogger(__name__)


@login_required
def index(request):

    if request.user.is_superuser or request.user.has_perm(perm='itinerante.auth_evento'):
        diretoria = None
    else:
        diretoria = request.user.servidor.coordenadoria()

    endereco_initial = {
        'estado': Estado.objects.get(uf__iexact=settings.SIGLA_UF)
    }

    relatorios = Relatorio.objects.filter(
        papeis=request.user.servidor.papel,
        locais__pagina=Local.PAG_ITINERANTE_INDEX
    ).ativos()

    angular = 'ItineranteCtrl'

    return render(request=request, template_name="itinerante/index.html", context=locals())


@login_required
@reversion.create_revision(atomic=False)
def autorizar(request):

    resposta = {'success': False}

    if request.method == 'POST':

        dados = simplejson.loads(request.body)

        if request.user.is_superuser or request.user.has_perm(perm='itinerante.auth_evento'):

            try:

                evento = Evento.objects.get(id=dados['id'])
                evento.autorizar(request.user.servidor)

                criar_lotacao_servidores(evento=evento, cadastrado_por=request.user.servidor)

                reversion.set_user(request.user)
                reversion.set_comment(Util.get_comment_save(request.user, evento, False))

                resposta = {'success': True}

            except Exception as e:
                erro = 'Erro ao autorizar evento %s \n %s ' % (dados['id'], e)
                resposta = {'success': False, 'error': erro}
                logger.error(erro)

    return JsonResponse(resposta)


def criar_lotacao_servidores(evento, cadastrado_por):

    # procura participantes que sao defensores
    defensores = evento.participantes.filter(defensor__ativo=True)
    horarios = '{{"{categoria}":[["00:00"],["00:00"],["00:00"],["00:00"],["00:00"],["00:00"],["00:00"]]}}'

    if evento.defensoria.categorias_de_agendas.exists():
        horarios = horarios.format(
            categoria=evento.defensoria.categorias_de_agendas.first().id
        )

    # cria atuacoes no itinerante para defensores/assessores
    for participante in defensores:

        # verifica se atuacao ja existe
        atuacao = evento.atuacoes.filter(defensor=participante.defensor).first()
        tipo_atuacao = Atuacao.TIPO_ACUMULACAO if participante.defensor.eh_defensor else Atuacao.TIPO_LOTACAO

        if not atuacao:
            atuacao = Atuacao(
                defensor=participante.defensor,
                tipo=tipo_atuacao
            )

        atuacao.defensoria = evento.defensoria
        atuacao.data_inicial = evento.data_inicial
        atuacao.data_final = datetime.combine(evento.data_final, time.max)
        atuacao.ativo = True
        atuacao.save()

        if participante.defensor.eh_defensor:

            # cria/atualiza agenda extrapauta para atuacao no itinerante
            agendas = atuacao.agendas.filter(ativo=True)
            if agendas:
                agendas.update(
                    titulo=evento.titulo,
                    data_ini=evento.data_inicial,
                    data_fim=evento.data_final,
                    horarios=None,
                    conciliacao=horarios
                )
            else:
                agenda = Agenda(
                    titulo=evento.titulo,
                    tipo=Agenda.TIPO_PERMISSAO,
                    atuacao=atuacao,
                    data_ini=evento.data_inicial,
                    data_fim=evento.data_final,
                    comarca=atuacao.defensoria.comarca,
                    defensor=atuacao.defensor,
                    cadastrado_por=cadastrado_por,
                    horarios=None,
                    conciliacao=horarios
                )
                agenda.save()

        evento.atuacoes.add(atuacao)

    # desativa atuacoes de defensores que nao estao mais vinculados ao itinerante
    evento.atuacoes.exclude(defensor__servidor__in=defensores).update(ativo=False)


@login_required
def distribuir(request):

    if request.method == 'POST':

        evento = Evento.objects.filter(
            data_inicial__lte=date.today(),
            data_final__gte=date.today(),
            participantes=request.user.servidor,
            ativo=True).first()

        data_ini = date.today()
        data_fim = datetime.combine(data_ini, time.max)

        defensores = []
        atendimentos = []

        if evento:

            for servidor in evento.participantes.filter(ativo=True, defensor__eh_defensor=True).exclude(defensor=None):
                defensores.append({
                    'id': servidor.defensor.id,
                    'nome': servidor.nome})

            atendimentos_lst = AtendimentoDefensor.objects.filter(
                Q(ativo=True) &
                Q(remarcado=None) &
                Q(defensoria=evento.defensoria) &
                Q(defensor__in=[(v['id']) for v in defensores]) &
                Q(data_agendamento__range=[data_ini, data_fim])
            ).order_by('data_agendamento', 'data_atendimento')

            for atendimento in atendimentos_lst:
                atendimentos.append({
                    'id': atendimento.id,
                    'numero': atendimento.numero,
                    'tipo': atendimento.LISTA_TIPO[atendimento.tipo][1],
                    'data_agendamento': atendimento.data_agendamento.strftime('%Y-%m-%dT%H:%M:00-03:00'),
                    'agenda': 'Extra' if atendimento.extra else 'Pauta',
                    'requerente': atendimento.requerente.pessoa.nome if atendimento.requerente else None,
                    'requerido': atendimento.requerido.pessoa.nome if atendimento.requerido else None,
                    'defensor': atendimento.defensor_id,
                    'defensoria': {'id': atendimento.defensoria.id, 'nome': atendimento.defensoria.nome},
                    'area': atendimento.qualificacao.area.nome,
                    'pedido': atendimento.qualificacao.titulo,
                    'responsavel': atendimento.responsavel.id if atendimento.responsavel else None,
                    'atendido': True if atendimento.data_atendimento else False,
                    'retornos_pendentes': True if atendimento.retornos_pendentes.count() else False
                })

        return JsonResponse({
            'defensores': defensores,
            'atendimentos': atendimentos})

    else:

        angular = 'DistribuicaoCtrl'

        return render(request=request, template_name="itinerante/distribuir.html", context=locals())


@login_required
@reversion.create_revision(atomic=False)
def excluir(request):
    if request.method == 'POST':

        dados = simplejson.loads(request.body)
        success = True

        try:

            evento = Evento.objects.get(id=dados['id'])
            evento.excluir(request.user.servidor)

            for atuacao in evento.atuacoes.all():
                atuacao.excluir(request.user.servidor)
                for agenda in atuacao.agendas.all():
                    agenda.excluir(request.user.servidor)

            reversion.set_user(request.user)
            reversion.set_comment(Util.get_comment_delete(request.user, evento))

        except Exception as e:
            erro = 'Erro ao excluir evento %s \n %s ' % (dados['id'], e)
            logger.error(erro)
            success = False

        return JsonResponse({'success': success})

    return JsonResponse({'success': False})


@login_required
def distribuir_salvar(request):
    dados = simplejson.loads(request.body)

    for item in dados:
        AtendimentoDefensor.objects.filter(id=item['id']).update(
            defensor=item['defensor'],
            distribuido_por=request.user.servidor,
            data_distribuido=datetime.now())

    return JsonResponse({'success': True})


@login_required
def listar(request):

    eventos = Evento.objects.all().select_related(
        'defensoria',
        'municipio__comarca__coordenadoria',
        'cadastrado_por__usuario',
        'autorizado_por__usuario',
        'excluido_por__usuario',
    ).prefetch_related(
        Prefetch(
            'participantes',
            queryset=Servidor.objects.select_related(
                'defensor',
            )
        )
    )

    if not request.user.is_superuser and not request.user.has_perm(perm='itinerante.auth_evento'):
        diretoria = request.user.servidor.coordenadoria()
        eventos = eventos.filter(
            Q(municipio__comarca=diretoria) |
            Q(municipio__comarca__coordenadoria=diretoria))

    if request.method == 'POST':
        filtro = simplejson.loads(request.body)

        if 'ativo' in filtro:
            eventos = eventos.filter(ativo=filtro['ativo'])

        if 'autorizado' in filtro:
            if filtro['autorizado']:
                eventos = eventos.exclude(autorizado_por=None)
            else:
                eventos = eventos.filter(autorizado_por=None)

        if 'encerrado' in filtro:
            if filtro['encerrado']:
                eventos = eventos.filter(data_final__lt=date.today()).order_by('-data_final')
            else:
                eventos = eventos.filter(data_final__gte=date.today()).order_by('data_inicial')

    resposta = []
    for evento in eventos:
        resposta.append({
            'id': evento.id,
            'titulo': evento.titulo,
            'data_inicial': Util.date_to_json(evento.data_inicial),
            'data_final': Util.date_to_json(evento.data_final),
            'municipio': {
                'id': evento.municipio.id,
                'comarca': {
                    'diretoria': evento.municipio.comarca.coordenadoria.nome if evento.municipio.comarca.coordenadoria else evento.municipio.comarca.nome,  # noqa
                    'nome': evento.municipio.comarca.nome,
                } if evento.municipio.comarca else None,
                'nome': evento.municipio.nome
            },
            'defensoria': {
                'id': evento.defensoria.id,
                'nome': evento.defensoria.nome
            },
            'participantes': [{
                'id': participante.id,
                'nome': participante.nome,
                'defensor': participante.defensor.id if hasattr(participante, 'defensor') else None,
                'eh_defensor': participante.defensor.eh_defensor if hasattr(participante, 'defensor') else None,
            } for participante in evento.participantes.all()],
            'data_cadastro': Util.date_to_json(evento.data_cadastro),
            'cadastrado_por': evento.cadastrado_por.usuario.username if evento.cadastrado_por else None,
            'data_autorizacao': Util.date_to_json(evento.data_autorizacao),
            'autorizado_por': evento.autorizado_por.usuario.username if evento.autorizado_por else None,
            'data_exclusao': Util.date_to_json(evento.data_exclusao),
            'excluido_por': evento.excluido_por.usuario.username if evento.excluido_por else None,
            'autorizado': True if evento.autorizado_por else False,
            'encerrado': evento.data_final < date.today(),
            'ativo': evento.ativo,
        })

    return JsonResponse(resposta, safe=False)


@login_required
@reversion.create_revision(atomic=False)
def salvar(request):

    if request.method == 'POST':

        dados = simplejson.loads(request.body)

        if 'id' in dados and dados['id']:
            evento = Evento.objects.get(id=dados['id'])
        else:
            evento = Evento(cadastrado_por=request.user.servidor)

        # Carrega e valida municipio
        municipio = Municipio.objects.filter(id=dados['municipio']['id']).first()

        if not municipio:
            return JsonResponse({'success': False, 'errors': ['Localidade inválida!']})

        # converte json string para date
        dados['data_inicial'] = Util.json_to_date(dados['data_inicial'])
        dados['data_final'] = Util.json_to_date(dados['data_final'])

        # Carrega e valida defensoria itnerante
        if dados['defensoria']['id']:
            defensoria = Defensoria.objects.get(id=dados['defensoria']['id'])

        if not defensoria:
            return JsonResponse({
                'success': False,
                'errors': ['Não existe núcleo itinerante atendendo essa localidade!']
            })

        dados['municipio'] = municipio.id
        dados['defensoria'] = defensoria.id

        for index, participante in enumerate(dados['participantes']):

            dados['participantes'][index] = participante['id']

            q = Evento.objects.filter(
                participantes=participante['id'],
                data_inicial__lte=dados['data_final'],
                data_final__gte=dados['data_inicial'],
                ativo=True
            ).exclude(
                id=evento.id
            )

            # Verifica se participante está em outro evento no mesmo período
            ja_existe = q.exists()

            if ja_existe:
                return JsonResponse({
                    'success': False,
                    'errors': [u'{} não pode participar desde evento pois já está vinculado a outro evento no mesmo período! [id:{}]'.format(participante['nome'], q.first().id)]  # noqa: E501
                })

        form = EventoForm(dados, instance=evento)
        errors = []

        if form.is_valid():

            novo = (evento.id is None)
            evento = form.save()

            if evento.data_autorizacao:
                criar_lotacao_servidores(evento=evento, cadastrado_por=request.user.servidor)

            reversion.set_user(request.user)
            reversion.set_comment(Util.get_comment_save(request.user, evento, novo))

            return JsonResponse({'success': True, 'id': evento.id})

        else:
            errors.append([(k, v[0]) for k, v in form.errors.items()])
            return JsonResponse({'success': False, 'errors': errors})

    return JsonResponse({'success': False})
