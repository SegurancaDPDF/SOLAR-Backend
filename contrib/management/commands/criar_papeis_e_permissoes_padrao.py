# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from django.core.management.base import BaseCommand
from contrib.services import PapelService


class Command(BaseCommand):
    help = "Cria Papéis e Grupos de Permissão Padrão"

    def handle(self, *args, **options):
        service = PapelService()
        service.criar_grupos()
        service.criar_papeis()
