# -*- coding: utf-8 -*-

from datetime import datetime

# Bibliotecas de terceiros
from django.db.models import Q, QuerySet, Manager

from core.managers import AuditoriaBaseQuerySet


class BaseQuerySet(QuerySet):
    def ativos(self):
        return self.filter(ativo=True)

    def inativos(self):
        return self.filter(ativo=False)
    # adiciona os métodos ativos e inativos que filtram os objetos ativos e inativos no banco de dados


class BaseManager(Manager.from_queryset(BaseQuerySet)):
    pass
    # utiliza o BaseQuerySet como QuerySet padrão para operações no banco de dados


class BairroQuerySet(AuditoriaBaseQuerySet):
    pass


class BairroManager(Manager.from_queryset(BairroQuerySet)):
    pass


class EnderecoQuerySet(AuditoriaBaseQuerySet):
    def principais(self):
        return self.filter(principal=True)

    def secundarios(self):
        return self.filter(principal=False)
    #  adiciona os métodos principais e secundarios que filtram os endereços principais e secundários no banco de dados


class EnderecoManager(Manager.from_queryset(EnderecoQuerySet)):
    pass


class ComarcaQuerySet(BaseQuerySet):
    def coordenadorias(self):
        return self.filter(coordenadoria=None)

    def dependentes(self):
        return self.exclude(coordenadoria=None)

    def menu(self, defensor):
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
            Q(
                Q(defensoria__nucleo=None) |
                Q(defensoria__nucleo__livre=True)
            ) &
            Q(defensoria__all_atuacoes__ativo=True)
        ).distinct()
    # adiciona os métodos coordenadorias, dependentes e menu que filtram as comarcas no banco de dados


class ComarcaManager(Manager.from_queryset(ComarcaQuerySet)):
    pass


class DefensoriaQuerySet(BaseQuerySet):
    pass


class DefensoriaManager(Manager.from_queryset(DefensoriaQuerySet)):
    pass


class MenuExtraQuerySet(AuditoriaBaseQuerySet):
    pass


class MenuExtraManager(Manager.from_queryset(MenuExtraQuerySet)):
    pass


class OrientacaoSexualQuerySet(AuditoriaBaseQuerySet):
    pass


class OrientacaoSexualManager(Manager.from_queryset(OrientacaoSexualQuerySet)):
    pass


class IdentidadeGeneroQuerySet(AuditoriaBaseQuerySet):
    pass


class IdentidadeGeneroManager(Manager.from_queryset(IdentidadeGeneroQuerySet)):
    pass


class GeneroPessoaQuerySet(AuditoriaBaseQuerySet):
    pass


class GeneroPessoaManager(Manager.from_queryset(GeneroPessoaQuerySet)):
    pass
