# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from django.contrib import admin

from core.admin import EventoAdmin, TipoEventoAdmin

from . import models

# Essa classe é usada para personalizar a administração do modelo AtividadeExtraordinaria.


class AtividadeExtraordinariaAdmin(EventoAdmin):
    pass

# Essa classe é usada para personalizar a administração do modelo AtividadeExtraordinariaTipo.


class AtividadeExtraordinariaTipoAdmin(TipoEventoAdmin):
    pass

# Registra os modelos junto ao admin do Django, usando as classes  para personalizar a administração.


admin.site.register(models.AtividadeExtraordinaria, AtividadeExtraordinariaAdmin)
admin.site.register(models.AtividadeExtraordinariaTipo, AtividadeExtraordinariaTipoAdmin)
