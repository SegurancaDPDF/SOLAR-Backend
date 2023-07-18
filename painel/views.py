# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import logging
from datetime import datetime

# Biblitecas de terceiros
from constance import config
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache

# Solar
from contrib.models import Servidor, Defensoria
from comarca.models import Predio

# Modulos locais
from .models import Painel
from comarca.models import Guiche

logger = logging.getLogger(__name__)


@never_cache
@login_required
def index(request):
    angular = 'PainelCtrl'
    return render(request=request, template_name="painel/index.html", context=locals())

# implementação do painel na aplicação Django.


@never_cache
@login_required
def get_senhas(request, predio):
    if request.method == 'GET' and request.is_ajax():

        senhas = Painel.objects.filter(
            cadastrado_em__date=datetime.now().date(),
            predio_id=predio
        ).order_by(
            '-modificado_em'
        )[:4]

        dados = []
        predio_obj = Predio.objects.get(id=predio, ativo=True)
        servidor = request.user.servidor

        for senha in senhas:

            a = senha.atendimento
            agenda = a.agenda

            defensoria = a.defensoria
            usuario = senha.cadastrado_por.servidor
            guiche = Guiche.objects.filter(
                usuario=usuario,
                predio=defensoria.predio,
                ativo=True
            ).first()
            if not guiche or not usuario:
                JsonResponse({'success': False})

            if predio_obj.recepcao_por_atuacao:
                lotacoes = servidor.defensor.atuacoes_vigentes()
                for lotacao in lotacoes:
                    if defensoria.id == lotacao.defensoria.id:
                        dados.append({
                            'tipo_servico': a.agenda_id,
                            'servico_nome': agenda.nome,
                            'tipo_atendimento': senha.tipo,
                            'hora': senha.modificado_em,
                            'prioridade': 1 if a.prioridade else 0,
                            'guiche_numero': guiche.numero if guiche else 0,
                            'guiche_tipo': guiche.tipo if guiche else 1,
                            'andar': guiche.andar if guiche else 0,
                            'defensoria_nome': a.at_defensor.defensoria.nome,
                            'requerente_nome': a.get_requerente().nome,
                            'success': True,
                        })
            else:
                dados.append({
                    'servico_tipo': a.agenda_id,
                    'servico_nome': agenda.nome,
                    'tipo_atendimento': senha.tipo,
                    'hora': senha.cadastrado_em,
                    'prioridade': 1 if a.prioridade else 0,
                    'guiche_numero': guiche.numero if guiche else 0,
                    'guiche_tipo': guiche.tipo if guiche else 1,
                    'andar': guiche.andar if guiche else 0,
                    'defensoria_nome': a.at_defensor.defensoria.nome,
                    'requerente_nome': a.get_requerente().nome,
                    'success': True,
                })

        return JsonResponse(dados, safe=False)

    return JsonResponse({'success': False})


@login_required
def index_get_predios(request):
    defensor = request.user.servidor.defensor
    atuacoes = defensor.atuacoes_vigentes()

    # Se tem atuação, obtem lista de todos prédios das defensorias
    if atuacoes.count():
        predios = Predio.objects.filter(defensoria__in=atuacoes.values_list('defensoria_id', flat=True)).distinct()
    # Senão, obtém lista com prédios da comarca
    else:
        predios = Predio.objects.filter(comarca=request.session.get('comarca', 0), ativo=True).order_by('nome')

    if predios.count() == 1:
        request.session['predio'] = predios.first().id
        return redirect('painel_predio_set', predios.first().id)

    # Se tiver apenas uma atuação, define ela como padrão
    atuacao = None
    if atuacoes.count() == 1:
        atuacao = atuacoes.first()

    return render(request=request, template_name="painel/predios.html", context=locals())


@login_required
def predio_set(request, predio_id):

    corregedoria = Defensoria.objects.filter(id=config.PAINEL_SENHA_CORREGEDORIA_ID).first()
    predio = predio_id
    angular = 'PainelCtrl'

    return render(request=request, template_name="painel/index.html", context=locals())
