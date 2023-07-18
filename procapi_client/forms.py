# django
from django import forms

# project
from contrib.models import Comarca, Defensoria, DefensoriaVara, Vara
from defensor.models import Defensor

# application
from . import models

# Classes de formulário para coletar dados dos usuários como listar e distribuir avisos ou exibir um painel de avisos.


class ListDistribuirAvisosForm(forms.Form):
    sistema_webservice = forms.ModelChoiceField(required=False, queryset=models.SistemaWebService.objects.ativos())
    comarca = forms.ModelChoiceField(required=False, queryset=Comarca.objects.all())
    vara = forms.ModelChoiceField(required=False, queryset=Vara.objects.all())
    defensor = forms.ModelChoiceField(required=False, queryset=Defensor.objects.all())
    paridade = forms.ChoiceField(required=False, choices=DefensoriaVara.LISTA_PARIDADE)
    defensoria = forms.ModelChoiceField(required=False, queryset=Defensoria.objects.all())
    page = forms.IntegerField(required=False)


class PainelDeAvisosForm(forms.Form):
    sistema_webservice = forms.ModelChoiceField(required=False, queryset=models.SistemaWebService.objects.ativos())
    defensoria = forms.ModelChoiceField(required=False, queryset=Defensoria.objects.all())
    responsavel = forms.ModelChoiceField(required=False, queryset=Defensor.objects.all())
