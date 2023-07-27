# -*- coding:utf-8- -*-

# Biblioteca Padrao
from datetime import datetime, date
import json as simplejson
import re

from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
from django.shortcuts import render

import math
from contrib.models import Defensoria, Util
from nucleo.nadep.forms import BuscarAtendimentoForm
from nucleo.nadep.models import Prisao, Atendimento as Visita, Aprisionamento
from nucleo.nadep.services import AnoMesDia
from processo.processo.models import Audiencia
from atendimento.atendimento.models import Atendimento
from atendimento.atendimento.forms import AnotacaoForm


@login_required
@permission_required('nadep.view_prisao')
def buscar(request):
    """ Exibe pagina com todos os presos cadastrados """

    if request.method == 'POST':

        registros = []
        numero_registros = 25
        filtro = simplejson.loads(request.body)
        form = BuscarAtendimentoForm(filtro)

        hoje = date.today()

        if form.is_valid():

            presos_list = Prisao.objects.filter(
                Q(ativo=True) &
                Q(data_baixa=None) &
                (
                    (
                        Q(tipo=Prisao.TIPO_PROVISORIO) &
                        Q(resultado_sentenca=None) &
                        Q(aprisionamentos__situacao=Aprisionamento.SITUACAO_PRESO) &
                        Q(aprisionamentos__data_final=None)
                    ) |
                    (
                        Q(tipo=Prisao.TIPO_CONDENADO) &
                        Q(data_liquidacao=None) &
                        ~Q(originada__pena=Prisao.PENA_RESTRITIVA)
                    )
                ) &
                ~Q(parte__atendimento=None)
            ).order_by(
                'pessoa__nome', 'pessoa__id', '-data_prisao'
            ).distinct(
                'pessoa__nome', 'pessoa__id'
            )

            if 'comarca' in filtro and filtro['comarca']:
                presos_list = presos_list.filter((
                    Q(parte__defensoria__comarca=filtro['comarca'])
                ))

            if 'defensoria' in filtro and filtro['defensoria']:
                presos_list = presos_list.filter(
                    Q(parte__defensoria_id=filtro['defensoria'])
                )

            if 'defensor' in filtro and filtro['defensor']:
                defensorias = Defensoria.objects.filter(
                    Q(all_atuacoes__defensor=filtro['defensor']) &
                    Q(all_atuacoes__ativo=True) &
                    (
                        (
                            Q(all_atuacoes__data_inicial__lte=datetime.now()) &
                            Q(all_atuacoes__data_final=None)
                        ) |
                        (
                            Q(all_atuacoes__data_inicial__lte=datetime.now()) &
                            Q(all_atuacoes__data_final__gte=datetime.now())
                        )
                    )
                ).distinct().values('id')

                presos_list = presos_list.filter(
                    Q(parte__defensoria__in=defensorias)
                )

            if 'filtro' in filtro and filtro['filtro']:

                filtro_numero = re.sub('[^0-9]', '', filtro['filtro'])

                if len(filtro_numero) == 11:  # CPF

                    presos_list = presos_list.filter(pessoa__cpf=filtro_numero)

                elif len(filtro_numero) > 0:  # Numero do Processo

                    presos_list = presos_list.filter(parte__processo__numero_puro=filtro_numero)

                else:

                    presos_list = presos_list.filter(
                        pessoa__nome_norm__startswith=Util.normalize(filtro['filtro']),
                    )

            if form.cleaned_data['data_ini']:
                presos_list = presos_list.filter(
                    data_prisao__gte=form.cleaned_data['data_ini']
                )

            if form.cleaned_data['data_fim']:
                presos_list = presos_list.filter(
                    data_prisao__lte=form.cleaned_data['data_fim']
                )

            primeiro = filtro['pagina'] * numero_registros
            ultimo = primeiro + numero_registros

            if filtro['pagina'] == 0:
                filtro['total'] = presos_list.count()
                filtro['paginas'] = math.ceil(float(filtro['total']) / numero_registros)

            presos_list = presos_list[primeiro:ultimo]

            presos_list = presos_list.values(
                'id',
                'tipo',
                'pessoa__id',
                'pessoa__nome',
                'estabelecimento_penal__id',
                'estabelecimento_penal__nome',
                'parte__atendimento__id',
                'parte__atendimento__numero',
            )

            last_registro = None

            for registro in presos_list:

                # Ultima Visita
                for visita in Visita.objects.filter(
                    prisao__pessoa=registro['pessoa__id'],
                    ativo=True
                ).order_by(
                    '-data_atendimento'
                ).values(
                    'numero', 'data_atendimento', 'historico', 'atendido_por__nome'
                )[:1]:
                    visita['dias_atendimento'] = AnoMesDia(dia=(hoje - visita['data_atendimento'].date()).days).__str__()  # noqa: E501
                    registro['visita'] = visita

                # Ultima Anotacao
                for anotacao in Atendimento.objects.filter(
                    inicial=registro['parte__atendimento__id'],
                    tipo=Atendimento.TIPO_ANOTACAO,
                    ativo=True
                ).order_by(
                    '-data_atendimento'
                ).values(
                    'numero', 'data_atendimento', 'historico', 'atendido_por__nome'
                )[:1]:
                    anotacao['dias_atendimento'] = AnoMesDia(dia=(hoje - anotacao['data_atendimento'].date()).days).__str__()  # noqa: E501
                    registro['anotacao'] = anotacao

                registro['prisoes'] = []
                for prisao in Prisao.objects.filter(
                    Q(pessoa=registro['pessoa__id']) &
                    Q(ativo=True) &
                    (
                        (
                            Q(tipo=Prisao.TIPO_PROVISORIO) & Q(resultado_sentenca=None)
                        ) |
                        (
                            Q(tipo=Prisao.TIPO_CONDENADO) & ~Q(originada__pena=Prisao.PENA_RESTRITIVA)
                        )
                    )
                ).order_by(
                    '-data_prisao'
                ).values(
                    'tipo',
                    'tipificacao__nome',
                    'tentado_consumado',
                    'data_prisao',
                    'processo__id',
                    'processo__numero',
                    'parte__defensoria__nome'
                ):

                    # Proxima Audiencia
                    for audiencia in Audiencia.objects.filter(
                        data_protocolo__gte=date.today(),
                        processo=prisao['processo__id'],
                        ativo=True
                    ).order_by(
                        'data_protocolo'
                    ).values_list(
                        'data_protocolo', flat=True
                    )[:1]:
                        prisao['data_audiencia'] = audiencia.date()
                        if audiencia.date() > hoje:
                            prisao['dias_audiencia'] = AnoMesDia(dia=(prisao['data_audiencia'] - hoje).days).__str__()
                        else:
                            prisao['dias_audiencia'] = AnoMesDia(dia=(hoje - prisao['data_audiencia']).days).__str__()

                    if prisao['data_prisao']:
                        prisao['dias_preso'] = AnoMesDia(dia=(hoje - prisao['data_prisao']).days).__str__()

                    registro['prisoes'].append(prisao)

                registros.append(registro)

        return JsonResponse(
            {
                'registros': registros,
                'pagina': filtro['pagina'],
                'paginas': filtro['paginas'] if 'paginas' in filtro else 0,
                'ultima': filtro['pagina'] == filtro['paginas'] - 1 if 'paginas' in filtro else True,
                'total': filtro['total'],
                'LISTA': {
                    'REGIME': dict(Prisao.LISTA_REGIME),
                    'TENTADO_CONSUMADO': dict(Prisao.LISTA_TIPO_CRIME),
                },
            }, safe=False)

    form = BuscarAtendimentoForm(request.GET)
    form_anotacao = AnotacaoForm(angular_prefix='anotacao')

    angular = 'BuscarPresoCtrl'

    return render(request=request, template_name="nadep/buscar_preso.html", context=locals())
