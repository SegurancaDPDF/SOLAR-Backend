from django.contrib import admin
from .models import Salario, Inpc
from django.utils.html import format_html


# registra a classe Salario no painel de administração do Django
@admin.register(Salario)
class SalarioAdmin(admin.ModelAdmin):
    # define quais campos serão exibidos na lista de exibição no painel de administração
    list_display = ['id', 'ano', 'salario_minimo']

    # função para exibir o valor do salário mínimo formatado em um elemento HTML personalizado
    def salario_minimo(self, obj: Salario) -> str:
        valor = str(obj.valor)
        return format_html(
            "<div style='display:flex; width:6.9em; flex-direction:column; align-items: flex-end;'>{}</div>", valor)


# registra a classe Inpc no painel de administração do Django
@admin.register(Inpc)
class InpcAdmin(admin.ModelAdmin):
    # define quais campos serão exibidos na lista de exibição no painel de administração
    list_display = ('id', 'ano_mes', 'inpc')

    # função para exibir o valor do índice INPC formatado em um elemento HTML personalizado
    def inpc(self, obj: Inpc) -> str:
        valor = str(obj.valor)
        return format_html(
            "<div style='display:flex; width:2em; flex-direction:column; align-items: flex-end;'>{}</div>", valor)