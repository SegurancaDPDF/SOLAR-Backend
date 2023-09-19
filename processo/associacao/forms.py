
from django import forms

from contrib.forms import BootstrapForm
from contrib.models import Defensoria, DefensoriaVara, Vara
from procapi_client.models import SistemaWebService


class BuscarFaseTipoForm(forms.Form):

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
        value = self.cleaned_data['paridade']

        if value and value.isdigit():
            value = int(value)
        else:
            value = None

        return value


class CadastrarDefensoriaVaraForm(BootstrapForm):

    class Meta:
        model = DefensoriaVara
        fields = ['defensoria', 'vara', 'paridade', 'distribuicao_automatica']
        widgets = {
            'defensoria': forms.Select(attrs={'class': 'span6 ativar-select2'}),
            'vara': forms.Select(attrs={'class': 'span6 ativar-select2'}),
            'paridade': forms.Select(attrs={'class': 'span6 ativar-select2'}),
            'parte': forms.Select(attrs={'class': 'span6 ativar-select2'})
        }
