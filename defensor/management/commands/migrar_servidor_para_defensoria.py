# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip
import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
# from django.utils import timezone

from ...models import DefensorAssessor, Atuacao
from contrib.models import Servidor


class Command(BaseCommand):
    help = "Migrar Servidor para Defensoria"

    def handle(self, *args, **options):
        cadastrado_por = Servidor.objects.get(usuario__username="fabio.cb")
        # agora = timezone.now()
        # data_inicial = datetime.datetime(year=agora.year, month=agora.month, day=agora.day)
        data_inicial = datetime.datetime(year=2017, month=8, day=2)
        agora = datetime.datetime(year=2017, month=8, day=2)

        q = Q()
        q &= Q(ativo=True)
        q &= Q(data_inicial__lte=agora)
        q &= Q(data_final__gte=agora) | Q(data_final=None)
        q &= Q(defensoria__nucleo=None) | Q(defensoria__nucleo__plantao=False)
        q &= Q(tipo__in=[Atuacao.TIPO_TITULARIDADE, Atuacao.TIPO_ACUMULACAO])

        assessores = DefensorAssessor.objects.filter(Q(ativo=True))

        novas_atuacoes = {}
        for assessor in assessores:

            supervisor = assessor.supervisor

            atuacoes = supervisor.all_atuacoes.filter(q)
            print(assessor, assessor.supervisor, atuacoes.count())

            for atuacao in atuacoes:
                dados_nova_atuacao = {
                    'cadastrado_por': cadastrado_por,
                    'tipo': Atuacao.TIPO_LOTACAO,
                    'data_inicial': data_inicial,
                    'data_final': None,
                    'defensoria_id': atuacao.defensoria_id,
                    'defensor': assessor
                }
                check = {
                    'cadastrado_por': cadastrado_por,
                    'tipo': Atuacao.TIPO_LOTACAO,
                    'data_inicial': data_inicial,
                    'defensoria_id': atuacao.defensoria_id,
                    'defensor': assessor
                }
                if not Atuacao.objects.filter(**check).exists():
                    t = tuple(dados_nova_atuacao.values())
                    if t not in novas_atuacoes:
                        nova_atuacao = Atuacao(**dados_nova_atuacao)
                        novas_atuacoes[t] = nova_atuacao
                    else:
                        print('duplicado: ')
                        print('dados_nova_atuacao')

        with transaction.atomic():
            Atuacao.objects.bulk_create(novas_atuacoes.values(), batch_size=200)

        print('{0} lotações cadastradas!'.format(len(novas_atuacoes.values())))
