# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from datetime import date, datetime, time


from django.db import models
from django.db.models import F, Q


class DefensorQuerySet(models.QuerySet):
    def inativos(self):  # retorna os defensores inativos
        return self.filter(ativo=False)

    def ativos(self):  # retorna os defensores ativos
        return self.filter(ativo=True)

    def atuacoes_vigentes(self):
        """

        Retorna todas as atuações vigentes
        """

        q = Q(all_atuacoes__ativo=True)
        q &= Q(all_atuacoes__data_inicial__lte=datetime.now())
        q &= (
            Q(all_atuacoes__data_final=None) |
            Q(all_atuacoes__data_final__gte=datetime.now())
        )

        return self.filter(q)


class DefensorManager(models.Manager.from_queryset(DefensorQuerySet)):
    pass


class DefensorAssessorQuerySet(models.QuerySet):
    def inativos(self):
        return self.filter(ativo=False)

    def ativos(self):
        return self.filter(ativo=True)


class DefensorAssessorManager(models.Manager):
    def get_queryset(self):
        return DefensorSupervisorQuerySet(
            model=self.model,
            using=self._db
        ).select_related(
            'servidor',
            'supervisor__servidor'
        ).exclude(
            supervisor=None
        )

    def inativos(self):
        return self.get_queryset().inativos()

    def ativos(self):
        return self.get_queryset().ativos()


class DefensorSupervisorQuerySet(models.QuerySet):
    def inativos(self):
        return self.filter(ativo=False)

    def ativos(self):
        return self.filter(ativo=True)


class DefensorSupervisorManager(models.Manager):
    def get_queryset(self):
        return DefensorSupervisorQuerySet(
            model=self.model,
            using=self._db
        ).select_related(
            'servidor',
            'supervisor__servidor'
        ).filter(
            supervisor=None
        )

    def inativos(self):
        return self.get_queryset().inativos()

    def ativos(self):
        return self.get_queryset().ativos()


class AtuacaoQuerySet(models.QuerySet):

    def ativos(self):
        """Busca Atuações Ativas (vigentes e futuras)"""

        q = Q(ativo=True)
        q &= Q(data_final=None) | (Q(data_final__gte=datetime.now()) & Q(data_final__gte=F('data_inicial')))

        return self.filter(q)

    def titularidades(self):
        """Busca Atuações do tipo Titularidade"""

        from defensor.models import Atuacao
        return self.filter(tipo=Atuacao.TIPO_TITULARIDADE)

    def acumulacoes(self):
        """Busca Atuações do tipo Acumulação"""

        from defensor.models import Atuacao
        return self.filter(tipo=Atuacao.TIPO_ACUMULACAO)

    def substituicoes(self):
        """Busca Atuações do tipo Substituição"""

        from defensor.models import Atuacao
        return self.filter(tipo=Atuacao.TIPO_SUBSTITUICAO)

    def lotacoes(self):
        """Busca Atuações do tipo Lotação"""

        from defensor.models import Atuacao
        return self.filter(tipo=Atuacao.TIPO_LOTACAO)

    def nao_lotacoes(self):
        """Busca Atuações que não são do tipo Lotação"""

        from defensor.models import Atuacao
        return self.exclude(tipo=Atuacao.TIPO_LOTACAO)

    def por_tipo(self, tipo=None):
        """Busca as Atuações conforme o tipo desejado"""

        from defensor.models import Atuacao

        queryset = self.titularidades()

        if tipo == Atuacao.TIPO_ACUMULACAO:
            queryset = self.acumulacoes()

        elif tipo == Atuacao.TIPO_SUBSTITUICAO:
            queryset = self.substituicoes()

        elif tipo == Atuacao.TIPO_LOTACAO:
            queryset = self.lotacoes()

        return queryset

    def parcialmente_vigentes(self, inicio=None, termino=None):
        """

        Retorna todas as atuações que vigoraram em algum momento no período informado (vigência parcial)

        :param inicio: se inicio == None, será usada a data de hoje.
                       o horario inicio será justado automaticamente para hora 0h:0m:0s:000000ms

        :param termino: se termino == None e houver inicio, termino será inicio,
                        se termino == None e inicio == None, será usada a data de hoje.
                       o horario termino será justado automaticamente para hora 23h:59m:59s:999999ms
        :return: queryset atuacoes
        """
        if not inicio:
            inicio = date.today()
        if inicio and not termino:
            termino = inicio

        inicio = datetime.combine(inicio, time.min)
        termino = datetime.combine(termino, time.max)

        q = Q(data_inicial__lte=termino) & (
            Q(data_final=None) | (Q(data_final__gte=inicio) & Q(data_final__gt=F('data_inicial')))
            )
        return self.filter(q)

    def vigentes(self, inicio=None, termino=None, ajustar_horario=True):
        """

        Retorna todas as atuações que vigoraram durante todo o período informado (vigência integral)

        :param inicio: se inicio == None, será usada a data/hora atual.

        :param termino: se termino == None e houver inicio, termino será inicio,
                        se termino == None e inicio == None, será usada a data/hora atual.

        :param: ajustar_horario: se True, os horários serão ajustados para time.min e time.max respectivamente
                                  se False, o horário informado será mantido (hora exata)

        :return: queryset atuacoes
        """
        if not inicio:
            inicio = datetime.now()
        if inicio and not termino:
            termino = inicio

        if ajustar_horario:

            if type(inicio) is datetime:
                inicio = inicio.date()

            if type(termino) is datetime:
                termino = termino.date()

            inicio = datetime.combine(inicio, time.min)
            termino = datetime.combine(termino, time.max)

        q = Q(ativo=True)
        q &= Q(data_inicial__lte=inicio) & (Q(data_final=None) | Q(data_final__gte=termino))

        return self.filter(q)

    def vigentes_por_defensor(self, defensor, inicio=None, termino=None):
        """

        Retorna todas as Atuacoes do defensor, com data de inicio menor ou igual a inicio
        e data de termino maior ou igual a termino

        :param defensor: instancia de defensor.models.Defensor ou pk (int) para Defensor
        :param inicio: se inicio == None, será usada a data de hoje.
                       o horario inicio será justado automaticamente para hora 0h:0m:0s:000000ms

        :param termino: se termino == None e houver inicio, termino será inicio,
                        se termino == None e inicio == None, será usada a data de hoje.
                       o horario termino será justado automaticamente para hora 23h:59m:59s:999999ms
        :return: queryset atuacoes
        """
        if isinstance(defensor, int):
            q = Q(defensor_id=defensor)
        else:
            q = Q(defensor=defensor)
        queryset = self.filter(q)
        return queryset.vigentes(inicio=inicio, termino=termino)

    def vigentes_por_defensoria_e_tipo(
        self,
        defensorias=None,
        eh_defensor=True,
        inicio=None,
        termino=None,
        tipo=None
    ):
        """Retorna todas as Atuacoes da Defensoria conforme datas e se eh_defensor"""

        q = Q()

        if defensorias:
            if isinstance(defensorias, list):
                try:
                    q &= Q(defensoria__in=defensorias)
                except Exception:
                    # TODO: tratar exception
                    q &= Q(defensoria_id__in=defensorias)

            elif isinstance(defensorias, int):
                q &= Q(defensoria_id=defensorias)

            else:
                q &= Q(defensoria__in=defensorias)

        if eh_defensor is not None:
            q &= Q(defensor__eh_defensor=eh_defensor)

        queryset = self.filter(q).vigentes(inicio=inicio, termino=termino)

        from defensor.models import Atuacao

        if tipo == Atuacao.TIPO_TITULARIDADE:
            queryset = queryset.titularidades()

        elif tipo == Atuacao.TIPO_ACUMULACAO:
            queryset = queryset.acumulacoes()

        elif tipo == Atuacao.TIPO_SUBSTITUICAO:
            queryset = queryset.substituicoes()

        elif tipo == Atuacao.TIPO_LOTACAO:
            queryset = queryset.lotacoes()

        return queryset

    def vigentes_por_defensoria(
        self,
        defensorias=None,
        inicio=None,
        termino=None,
    ):

        from defensor.models import Atuacao

        # TODO: otimizar para fazer query mais simples; e não trazer Titularidade quando houver Substituição

        atuacoes_vigentes_substituicao = self.vigentes_por_defensoria_e_tipo(
            tipo=Atuacao.TIPO_SUBSTITUICAO,
            defensorias=defensorias,
            inicio=inicio,
            termino=termino
        )

        atuacoes_vigentes_acumulacao = self.vigentes_por_defensoria_e_tipo(
            tipo=Atuacao.TIPO_ACUMULACAO,
            defensorias=defensorias,
            inicio=inicio,
            termino=termino
        )

        atuacoes_vigentes_titular = self.vigentes_por_defensoria_e_tipo(
            tipo=Atuacao.TIPO_TITULARIDADE,
            defensorias=defensorias,
            inicio=inicio,
            termino=termino
        )

        lista = list(atuacoes_vigentes_titular.values_list('id', flat=True))
        lista += list(atuacoes_vigentes_substituicao.values_list('id', flat=True))
        lista += list(atuacoes_vigentes_acumulacao.values_list('id', flat=True))

        queryset = Q(id__in=lista)

        return self.filter(queryset)

    def all_select_relateds(self):
        return self.select_related(
            'defensoria',
            'defensor__servidor',
            'titular__servidor'
        )

    def comarcas(self):
        return self.values_list('defensoria__comarca_id', flat=True)

    def defensorias(self):
        return self.values_list('defensoria_id', flat=True)


class AtuacaoManager(models.Manager.from_queryset(AtuacaoQuerySet)):
    pass
