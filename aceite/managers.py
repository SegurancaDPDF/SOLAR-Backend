# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from django.db import models


class TermoRespostaManager(models.Manager):
    def get_queryset(self):
        return super(TermoRespostaManager, self).get_queryset().filter(desativado_em=None)
