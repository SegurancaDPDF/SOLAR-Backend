# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from rest_framework.permissions import BasePermission


class IsAdminUserOrIsServidorUsoInterno(BasePermission):
    """
   permite acesso apenas a usuários administradores, servidor.uso_interno=True
    """

    def has_permission(self, request, view):

        uso_interno = request.user and hasattr(request.user, 'servidor') and request.user.servidor.uso_interno
        is_staff = request.user and request.user.is_staff

        tem_permissao = uso_interno or is_staff
        return tem_permissao


class BaseDefensor(object):

    def get_defensor(self, request):
        if request.user and hasattr(request.user, 'servidor') and hasattr(request.user.servidor, 'defensor'):
            return request.user.servidor.defensor


class EstaLotadoNoSetorDoFiltroPermission(BasePermission, BaseDefensor):
    """
    Permite consultar apenas se o usuário estiver lotado no setor do filtro
    """

    def has_permission(self, request, view):

        permission = False
        defensor = self.get_defensor(request)
        defensoria = request.query_params.get('setor')

        if defensor and defensoria:
            permission = defensor.atuacoes_vigentes().filter(defensoria=defensoria).exists()

        return permission
