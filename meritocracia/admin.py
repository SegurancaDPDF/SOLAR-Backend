from django.contrib import admin
from .models import IndicadorMeritocracia


# usada para personalizar a exibicao e o comportamento da administracao de objetos IndicadorMeritocracia.
class IndicadorMeritocraciaAdmin(admin.ModelAdmin):
    actions = None
    list_display = ['nome', 'ativo']
    filter_horizontal = ['tipos_fases_processuais', 'tipos_documentos', 'tipos_agendas', 'tipos_atividades']
    search_fields = ('nome',)
    list_filter = ('ativo', )


admin.site.register(IndicadorMeritocracia, IndicadorMeritocraciaAdmin)
