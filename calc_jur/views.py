# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from .models import Salario, Inpc
from django.conf import settings
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
from math import floor
from constance import config


@login_required
def index(request):
    sigla_uf = settings.SIGLA_UF.upper()
    URL_CARTILHA_EXEC_PENAL = config.URL_CARTILHA_EXEC_PENAL
    return render(request, 'calc_jur/index.html', context=locals())


@login_required
def get_salarios(request):
    salarios = {}
    for s in Salario.objects.order_by('ano'):
        salarios[s.ano] = s.valor
    # data = serializers.serialize("json", salarios_dict)
    return JsonResponse(salarios)


@login_required
def get_inpc(request, ano_mes):
    # if request.is_ajax():
    inpc = {}
    indice = Inpc.objects.filter(ano_mes=ano_mes).first()
    if indice:
        inpc[indice.ano_mes] = indice.valor
    else:
        inpc[ano_mes] = 0
    return JsonResponse(inpc)


@login_required
def calcular_penal(request):
    req = json.load(request)
    duracao = {
        'anos': int(req['duracao_anos']),
        'meses': int(req['duracao_meses']),
        'dias': int(req['duracao_dias'])
    }
    interrupcao = {
        'anos': int(req['interrup_anos_remidos']),
        'meses': int(req['interrup_meses_remidos']),
        'dias': int(req['interrup_dias_remidos'])
    }
    detracao = {
        'anos': int(req['detracao_anos']),
        'meses': int(req['detracao_meses']),
        'dias': int(req['detracao_dias']),
    }
    fracao = {
        'numerador': int(req['fracao_numerador']),
        'denominador': int(req['fracao_denominador'])
    }
    percentual = int(req['span_percentual'])
    dias_remidos = int(req['dias_remidos'])
    dias_remidos_is_checked = req['dias_remidos_is_checked']

    inicio_pena = convert_str_to_date(req['inicio_pena'])
    inicio_pena = ajustar_inicio_pena(inicio_pena)

    termino_pena = calcular_termino_pena(inicio_pena, duracao, interrupcao, detracao, dias_remidos)

    dados_para_calcular_fracao = {
        'inicio_pena': inicio_pena,
        'termino_pena': termino_pena,
        'dias_remidos_is_checked': dias_remidos_is_checked,
        'dias_remidos': dias_remidos,
    }
    # frações
    fracao_1_2 = calcular_fracoes_pena(float(1/2), dados_para_calcular_fracao)
    fracao_1_3 = calcular_fracoes_pena(float(1/3), dados_para_calcular_fracao)
    fracao_3_5 = calcular_fracoes_pena(float(3/5), dados_para_calcular_fracao)
    fracao_2_5 = calcular_fracoes_pena(float(2/5), dados_para_calcular_fracao)
    fracao_1_6 = calcular_fracoes_pena(float(1/6), dados_para_calcular_fracao)
    fracao_personalizada = calcular_fracoes_pena(
        float(fracao['numerador']/fracao['denominador']),
        dados_para_calcular_fracao
    )
    fracao_porcentual = calcular_fracoes_pena(
        float(percentual/100),
        dados_para_calcular_fracao
    )

    data = {
        "termino_pena": termino_pena.strftime("%d/%m/%Y"),
        "fracao_1_2": fracao_1_2,
        "fracao_1_3": fracao_1_3,
        "fracao_3_5": fracao_3_5,
        "fracao_2_5": fracao_2_5,
        "fracao_1_6": fracao_1_6,
        "fracao_personalizada": fracao_personalizada,
        "dias_remidos_is_checked": dias_remidos_is_checked,
        "span_percentual": fracao_porcentual
    }
    return JsonResponse(data)


def ajustar_inicio_pena(inicio_pena):
    # regredindo um dia da pena, pois o primeiro dia da pena já conta em qualquer cálculo de dias cumpridos
    return (inicio_pena - relativedelta(days=1))


def convert_str_to_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d')


def calcular_termino_pena(inicio_pena, duracao, interrupcao, detracao, dias_remidos):
    # inicializando término da pena
    termino_pena = inicio_pena

    # acrescentando duracao pena em anos
    termino_pena += relativedelta(years=+duracao['anos'])
    # acrescentando duracao pena em meses
    termino_pena += relativedelta(months=+duracao['meses'])
    # acrescentando duracao pena em dias
    termino_pena += relativedelta(days=+duracao['dias'])

    # acrescentando interrupções (fuga por)
    termino_pena += relativedelta(years=+interrupcao['anos'])
    termino_pena += relativedelta(months=+interrupcao['meses'])
    termino_pena += relativedelta(days=+interrupcao['dias'])

    # subtraindo detração da pena (detração é o período que ele passou preso antes da condenação)
    termino_pena += relativedelta(years=-detracao['anos'])
    termino_pena += relativedelta(months=-detracao['meses'])
    termino_pena += relativedelta(days=-detracao['dias'])

    # subtrai dias remidos
    termino_pena -= timedelta(days=dias_remidos)

    return termino_pena


def calcular_fracoes_pena(fracao, data):
    delta = data['termino_pena'] - data['inicio_pena']
    total_dias = delta.days

    # remove dias remidos após o cálculo das frações, caso dias_remidos_is_checked for verdadeiro
    if data['dias_remidos_is_checked']:
        total_dias = total_dias + data['dias_remidos']
        # descobrindo e aplicando fracao da pena - arrendonda para baixo
        total_dias = total_dias * fracao
        total_dias = floor(total_dias)

        total_dias = total_dias - data['dias_remidos']
    # senão, remove dias remidos antes do cálculo. termino_pena já vem com os dias remidos descontados.
    else:
        total_dias = total_dias * fracao
        total_dias = floor(total_dias)

    # extraindo do total_dias a descricao por extenso da pena

    # para o cálculo penal, um ano tem 360 dias
    anos = total_dias // 360
    # um mês tem 30 dias
    meses = (total_dias - (anos * 360)) // 30
    dias = total_dias - (anos * 360) - (meses * 30)

    # extraindo do total_dias a data de fim da fração
    termino_fracao = data['inicio_pena'] + relativedelta(days=+total_dias)

    return f"{termino_fracao.strftime('%d/%m/%Y')} ( {anos} anos, {meses} meses, {dias} dias)"
