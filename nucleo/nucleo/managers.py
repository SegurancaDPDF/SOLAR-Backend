# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

# Bibliotecas de terceiros
from django.db.models import Q, Manager

from contrib.managers import BaseQuerySet


class NucleoQuerySet(BaseQuerySet):
    # define métodos de consulta específicos para Núcleos relacionados ao usuário Defensor
    def menu(self, defensor):
        # filtra os Núcleos com base nas datas de atuação e participação em eventos do Defensor
        agora = datetime.now()
        return self.filter(
            (
                Q(defensoria__all_atuacoes__defensor=defensor) &
                (
                    (
                        Q(defensoria__all_atuacoes__data_inicial__lte=agora) &
                        Q(defensoria__all_atuacoes__data_final=None)
                    ) |
                    (
                        Q(defensoria__all_atuacoes__data_inicial__lte=agora) &
                        Q(defensoria__all_atuacoes__data_final__gte=agora)
                    )
                ) &
                Q(defensoria__all_atuacoes__ativo=True) &
                Q(defensoria__evento=None) &
                ~Q(plantao=True)
            ) |
            (
                Q(defensoria__evento__participantes=defensor.servidor) &
                Q(defensoria__evento__data_inicial__lte=agora) &
                Q(defensoria__evento__data_final__gte=(agora-timedelta(days=agora.day))) &
                Q(defensoria__evento__ativo=True)
            )
        ).distinct()

    def menu_plantao(self, defensor):
        # filtra os Núcleos de Plantão com base nas datas de atuação do Defensor
        return self.filter(
            Q(defensoria__all_atuacoes__defensor=defensor) &
            (
                (
                    Q(defensoria__all_atuacoes__data_inicial__lte=datetime.now()) &
                    Q(defensoria__all_atuacoes__data_final=None)
                ) |
                (
                    Q(defensoria__all_atuacoes__data_inicial__lte=datetime.now()) &
                    Q(defensoria__all_atuacoes__data_final__gte=datetime.now())
                )
            ) &
            Q(defensoria__all_atuacoes__ativo=True) &
            Q(plantao=True)
        ).distinct()


class NucleoManager(Manager.from_queryset(NucleoQuerySet)):
    pass
