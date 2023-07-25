
from django import forms
from contrib.models import Defensoria, DefensoriaVara, Vara
from procapi_client.models import SistemaWebService
from contrib.forms import BootstrapForm


class BuscarFaseTipoForm(forms.Form):
    # formulário de busca para filtrar fases processuais com base no nome da fase e sistema
    # campos do formulário com seus respectivos widgets e opções
    sistema = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'span2 ativar-select2'}),
        empty_label='< Selecione um sistema >',
        queryset=SistemaWebService.objects.ativos()
    )

    filtro = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'span4',
                'placeholder': 'Nome da fase processual...'})
        )


class BuscarDefensoriaVaraForm(forms.Form):
    # formulário de busca para filtrar Defensorias e Varas com base em diferentes critérios
    # campos do formulário com seus respectivos widgets e opções
    defensoria = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'span3 ativar-select2'}),
        empty_label='< Selecione uma defensoria >',
        queryset=Defensoria.objects.filter(ativo=True)
    )

    vara = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'span3 ativar-select2'}),
        empty_label='< Selecione uma vara >',
        queryset=Vara.objects.filter(ativo=True)
    )

    paridade = forms.ChoiceField(
        choices=((None, '< Selecione uma paridade >'),) + DefensoriaVara.LISTA_PARIDADE,
        required=False,
        widget=forms.Select(
            attrs={'class': 'span2 ativar-select2'}))

    def clean_paridade(self):
        # converte o valor para inteiro se for um dígito, caso contrário, retorna None
        value = self.cleaned_data['paridade']

        if value and value.isdigit():
            value = int(value)
        else:
            value = None

        return value


class CadastrarDefensoriaVaraForm(BootstrapForm):   
    # herda da classe BootstrapForm para utilizar a estilização do Bootstrap

    class Meta:
        model = DefensoriaVara
        fields = ['defensoria', 'vara', 'paridade', 'distribuicao_automatica']
        widgets = {
            'defensoria': forms.Select(attrs={'class': 'span6 ativar-select2'}),
            'vara': forms.Select(attrs={'class': 'span6 ativar-select2'}),
            'paridade': forms.Select(attrs={'class': 'span6 ativar-select2'}),
            'parte': forms.Select(attrs={'class': 'span6 ativar-select2'})
        }
