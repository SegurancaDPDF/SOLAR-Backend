# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from constance import config
from django import forms

# Solar
from django.core.exceptions import FieldDoesNotExist
from django.forms.utils import ErrorList
from contrib import constantes
from contrib.models import Endereco, Estado, Municipio, Telefone

# Modulos locais
from .models import Documento as DocumentoPessoa, Dependente
from .models import (
    EstruturaMoradia,
    Filiacao,
    Moradia,
    Pessoa,
    PessoaAssistida,
    Renda
)


class CamposObrigatoriosFormMixin(object):

    not_null_fields = []

    def __init__(self, required_fields, *args, **kwargs):

        ignored_fields = kwargs.pop('ignored_fields', None)
        readonly_fields = kwargs.pop('readonly_fields', None)

        super(CamposObrigatoriosFormMixin, self).__init__(*args, **kwargs)

        if not isinstance(ignored_fields, list):
            ignored_fields = []

        if not isinstance(readonly_fields, list):
            readonly_fields = []

        if isinstance(required_fields, dict):
            for field in self.fields:
                if not isinstance(self.fields[field], forms.BooleanField):

                    # verificação para campos não-nulos no banco de dados (fix: IntegrityError)
                    aceita_nulo = False

                    try:
                        model_field = self.Meta.model._meta.get_field(field)
                        aceita_nulo = model_field.null or model_field.blank
                    except FieldDoesNotExist:
                        aceita_nulo = True

                    if not aceita_nulo:

                        self.not_null_fields.append(field)
                        self.fields[field].required = True
                        self.fields[field].widget.attrs['required'] = True

                    elif field not in ignored_fields:
                        # define campo como requerido de acordo com configuracoes recebidas
                        required = True
                        html_name = '{}-{}'.format(self.prefix, field) if self.prefix else field

                        if field in required_fields:
                            required = required_fields[field]

                        self.fields[field].required = required
                        self.fields[field].widget.attrs['required'] = required

                        if not required and config.EXIBIR_NAO_POSSUI_NOS_CAMPOS_OPCIONAIS:
                            self.fields[field].widget.attrs['ng-required'] = "!nao_possui['{}']".format(html_name)
                            self.fields[field].widget.attrs['ng-disabled'] = "nao_possui['{}']".format(html_name)

                if field in readonly_fields:
                    self.fields[field].widget.attrs['readonly'] = True


class PessoaForm(forms.ModelForm):
    class Meta:
        model = Pessoa
        fields = '__all__'


class CadastrarPessoa(CamposObrigatoriosFormMixin, forms.ModelForm):
    class Meta:
        model = PessoaAssistida
        exclude = (
            'nome_norm',
            'nome_soundex',
            'moradia',
            'enderecos',
            'telefones',
            'foto',
            'qtd_pessoas',
            'deficiencias',
            'bens',
            'desativado_por',
            'desativado_em',
            'patrimonios',
            'patrimonio',
        )

    def __init__(self, *args, **kwargs):

        self.base_fields['identidade_genero'].queryset = self.base_fields['identidade_genero'].queryset.ativos()

        self.base_fields['nome'].widget = forms.TextInput(
            attrs={
                'class': 'span9',
                'upper-text': '',
                'autocomplete': 'off',
                'ng-focus': 'alertar_alteracao()'
            }
        )

        self.base_fields['orientacao_sexual'].queryset = self.base_fields['orientacao_sexual'].queryset.ativos()

        self.base_fields['nome_social'].widget = forms.TextInput(
            attrs={
                'class': 'span9',
                'upper-text': '',
                'autocomplete': 'off'
            }
        )
        self.base_fields['apelido'].widget = forms.TextInput(
            attrs={
                'class': 'span9',
                'upper-text': '',
                'autocomplete': 'off'
            }
        )
        self.base_fields['cpf'].widget = forms.TextInput(
            attrs={
                'ui-mask': '999.999.999-99',
                'cpf-cnpj-validator': '',
                'ng-change': 'buscar_cpf()'
            }
        )
        self.base_fields['data_nascimento'].widget = forms.TextInput(
            attrs={
                'mask': '99/99/9999',
                'bs-datepicker': '',
                'data-date-format': 'dd/mm/yyyy',
                'autocomplete': 'off'
            }
        )
        self.base_fields['genero'].queryset = self.base_fields['genero'].queryset.ativos()
        self.base_fields['rg_numero'].widget = forms.TextInput(
            attrs={
                'placeholder': 'Número',
                'autocomplete': 'off'
            }
        )
        self.base_fields['rg_orgao'].widget = forms.TextInput(
            attrs={
                'placeholder': 'Órgão',
                'autocomplete': 'off'
            }
        )
        self.base_fields['rg_data_expedicao'].widget = forms.TextInput(
            attrs={
                'mask': '99/99/9999',
                'bs-datepicker': '',
                'data-date-format': 'dd/mm/yyyy',
                'autocomplete': 'off'
            }
        )
        self.base_fields['certidao_numero'].widget = forms.TextInput(
            attrs={
                'class': 'span4',
                'certidao-validator': '',
                'ui-mask': '999999 99 99 9999 9 99999 999 9999999 99',
            }
        )
        self.base_fields['qtd_filhos'].widget = forms.NumberInput(
            attrs={
                'placeholder': 'Nenhum',
                'min': 0
            })

        self.base_fields['email'].widget = forms.EmailInput(
            attrs={
                'data-validate': '{required:false,email:true}',
                'class': 'noupper',
                'autocomplete': 'off',
                'style': 'width: 500px'
            }
        )
        self.base_fields['profissao'].widget = forms.TextInput(
            attrs={
                'class': 'span6',
                'bs-typeahead': 'listar_profissoes',
                'autocomplete': 'off'
            }
        )
        self.base_fields['naturalidade'].widget = forms.TextInput(
            attrs={
                'placeholder': 'Município',
                'class': 'span6',
                'bs-typeahead': 'listar_municipios',
                'autocomplete': 'off'
            }
        )
        self.base_fields['naturalidade_estado'].widget = forms.TextInput(
            attrs={
                'placeholder': 'Estado/Província',
                'bs-typeahead': 'listar_estados',
                'autocomplete': 'off'
            }
        )

        super(CadastrarPessoa, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['autocomplete'] = 'off'
            self.fields[field].widget.attrs['ng-model'] = 'pessoa.' + field

        if self.fields['cpf'].required:
            self.fields['cpf'].widget.attrs['pattern'] = '\d{3}.\d{3}.\d{3}-\d{2}'  # noqa: W605

    def is_valid(self, requerente=True):

        self.full_clean()

        if self.cleaned_data['tipo'] == constantes.TIPO_PESSOA_FISICA:

            if self.cleaned_data['declara_orientacao_sexual'] and not self.cleaned_data['orientacao_sexual']:
                self._errors['declara_orientacao_sexual'] = ErrorList(['Informe a orientação sexual.'])

            if self.cleaned_data['declara_identidade_genero'] and not self.cleaned_data['identidade_genero']:
                self._errors['declara_identidade_genero'] = ErrorList(['Informe a identidade de gênero.'])

        return super(CadastrarPessoa, self).is_valid()


class CadastrarPessoaJuridica(CamposObrigatoriosFormMixin, forms.ModelForm):
    class Meta:
        model = PessoaAssistida
        exclude = (
            'nome_norm',
            'nome_soundex',
            'moradia',
            'enderecos',
            'telefones',
            'foto',
            'qtd_pessoas',
            'deficiencias',
            'bens',
            'desativado_por',
            'desativado_em',
            'patrimonios',
            'patrimonio',
            'data_nascimento',
            'sexo',
            'nome_social',
            'rg_numero',
            'rg_orgao',
            'qtd_filhos',
            'profissao',
            'naturalidade',
            'naturalidade_estado',
            'filiacoes',
            'tipo'
        )

    def __init__(self, *args, **kwargs):

        self.base_fields['nome'].widget = forms.TextInput(
            attrs={
                'class': 'span9',
                'upper-text': '',
                'ng-focus': 'alertar_alteracao()'
            }
        )
        self.base_fields['apelido'].widget = forms.TextInput(
            attrs={
                'class': 'span9',
                'upper-text': ''
            }
        )
        self.base_fields['cpf'].widget = forms.TextInput(
            attrs={
                'ui-mask': '99.999.999/9999-99',
                'cpf-cnpj-validator': '',
                'ng-change': 'buscar_cpf()'
            }
        )

        self.base_fields['email'].widget = forms.TextInput(
            attrs={
                'data-validate': '{required:false,email:true}'
            }
        )

        super(CadastrarPessoaJuridica, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['autocomplete'] = 'off'
            self.fields[field].widget.attrs['ng-model'] = 'pessoa.' + field

        if self.fields['cpf'].required:
            self.fields['cpf'].widget.attrs['pattern'] = '\d{2}.\d{3}.\d{3}/\d{4}-\d{2}'  # noqa: W605

    def save(self, commit=True):
        # TODO verificar o que há de relacionamento que pode ser excluído

        self.instance.data_nascimento = None
        self.instance.sexo = None
        self.instance.rg_numero = None
        self.instance.rg_orgao = None

        # TODO verificar como excluir filiação na tabela relacionada
        # self.instance.filiacao_set = []

        self.instance.nome_social = None
        self.instance.declara_orientacao_sexual = False
        self.instance.orientacao_sexual = None
        self.instance.declara_identidade_genero = False
        self.instance.identidade_genero = None

        self.instance.estado_civil = None
        self.instance.qtd_filhos = None
        self.instance.qtd_pessoas = None
        self.instance.escolaridade = None
        self.instance.tipo_trabalho = None
        self.instance.qtd_estado = None

        self.instance.raca = None
        self.instance.naturalidade = None
        self.instance.naturalidade_estado = None
        self.instance.naturalidade_pais = None
        self.instance.nacionalidade = None

        self.instance.cartao_sus = False
        self.instance.plano_saude = False

        # TODO tratar deficiencias de PJ ao salvar
        # self.instance.deficiencias = None

        self.instance.profissao = None
        self.instance.moradia = None
        # self.instance.automatico = None

        return super(CadastrarPessoaJuridica, self).save(commit)


class CadastrarEndereco(CamposObrigatoriosFormMixin, forms.ModelForm):
    estado = forms.ModelChoiceField(queryset=Estado.objects.order_by('nome'), empty_label=None)

    class Meta:
        model = Endereco
        exclude = (
            'desativado_por',
            'desativado_em'
        )

    def __init__(self, *args, **kwargs):

        self.base_fields['logradouro'].widget = forms.TextInput(
            attrs={
                'class': "span6 form-control",
                'placeholder': 'Logradouro',
                'typeahead': 'i as i for i in logradouros | filter:$viewValue | limitTo:12'
            }
        )
        self.base_fields['numero'].widget = forms.TextInput(
            attrs={
                'class': "span2 form-control",
                'placeholder': 'Número'
            }
        )
        self.base_fields['complemento'].widget = forms.TextInput(
            attrs={
                'class': "span6 form-control",
                'placeholder': 'Complemento'
            }
        )
        self.base_fields['cep'].widget = forms.TextInput(
            attrs={
                'class': "span2 form-control",
                'ui-mask': '99.999-999',
                'ng-change': 'buscar_cep()',
            }
        )
        self.base_fields['bairro'].widget = forms.TextInput(
            attrs={
                'class': "span6 form-control",
                'placeholder': 'Bairro',
                'typeahead': 'i as i for i in bairros | filter:$viewValue | limitTo:12'
            }
        )
        self.base_fields['municipio'].widget = forms.Select(
            attrs={
                'class': "span6 form-control",
                'ng-options': 'i.id as i.nome for i in municipios'
            }
        )

        self.base_fields['tipo_area'].widget = forms.RadioSelect(choices=Endereco.LISTA_AREA)
        self.base_fields['tipo'].widget = forms.Select(choices=Endereco.LISTA_TIPO_ENDERECO)

        super(CadastrarEndereco, self).__init__(*args, **kwargs)

        self.fields['estado'].widget.attrs = {
            'class': "span2 form-control",
            'ng-change': 'listar_municipios()'
        }

        # carrega lista de municipios do estado selecionado
        try:
            self.fields['municipio'].queryset = Municipio.objects.filter(estado_id=kwargs['initial']['estado'])
        except Exception:
            self.fields['municipio'].queryset = Municipio.objects.none()

        # coloca o atributo 'ng-model' em todos campos
        for field in self.fields:
            self.fields[field].widget.attrs['ng-model'] = 'endereco_selecionado.' + field

        if self.fields['cep'].required:
            self.fields['cep'].widget.attrs['pattern'] = '\d{2}.\d{3}-\d{3}'  # noqa: W605

        # aplica ng-required em campos apenas se configuração ativada
        if config.ASSISTIDO_ENDERECO_VALIDAR_CEP:
            self.fields['cep'].widget.attrs['required'] = True
            self.fields['estado'].widget.attrs['disabled'] = 'disabled'
            self.fields['municipio'].widget.attrs['disabled'] = 'disabled'
            self.fields['logradouro'].widget.attrs['ng-disabled'] = '!endereco_selecionado.cep_consultado || endereco_selecionado.cep_consultado.logradouro'  # noqa: E501
            self.fields['bairro'].widget.attrs['ng-disabled'] = '!endereco_selecionado.cep_consultado || endereco_selecionado.cep_consultado.bairro'  # noqa: E501


class CadastrarFiliacao(CamposObrigatoriosFormMixin, forms.ModelForm):
    class Meta:
        model = Filiacao
        exclude = ('pessoa_assistida',)

    def __init__(self, *args, **kwargs):
        self.base_fields['tipo'].widget = forms.Select(choices=Filiacao.LISTA_TIPO)
        self.base_fields['nome'].widget = forms.TextInput(
            attrs={'class': 'span4', 'placeholder': 'Nome do(a) Pai/Mãe Biológico(a) ou Adotivo(a)'})

        super(CadastrarFiliacao, self).__init__(*args, **kwargs)

        # coloca o atributo 'ng-model' em todos campos
        for field in self.fields:
            self.fields[field].widget.attrs['ng-model'] = 'pai.' + field


class CadastrarMoradia(CamposObrigatoriosFormMixin, forms.ModelForm):
    class Meta:
        model = Moradia
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.base_fields['estrutura'].widget = forms.CheckboxSelectMultiple(choices=EstruturaMoradia.objects.all())

        super(CadastrarMoradia, self).__init__(*args, **kwargs)

        # coloca o atributo 'ng-model' em todos campos
        for field in self.fields:
            self.fields[field].widget.attrs['ng-model'] = 'pessoa.moradia.' + field


class CadastrarTelefone(forms.ModelForm):
    """ Formulario de cadastro de telefone (exclusivo para o cadastro de pessoa) """

    class Meta:
        model = Telefone
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.base_fields['tipo'].widget = forms.Select(choices=Telefone.LISTA_TIPO, attrs={'class': 'span2'})
        self.base_fields['ddd'].widget = forms.TextInput(attrs={'class': 'span2', 'ui-mask': '(99)'})
        self.base_fields['numero'].widget = forms.TextInput(attrs={'class': 'span4', 'ui-mask': '9999-9999'})

        super(CadastrarTelefone, self).__init__(*args, **kwargs)

        # coloca o atributo 'ng-model' em todos campos
        for field in self.fields:
            self.fields[field].widget.attrs['ng-model'] = 'fone.' + field


class DocumentoForm(forms.ModelForm):
    class Meta:
        model = DocumentoPessoa
        exclude = ['pessoa', 'data_enviado', 'enviado_por', 'ativo']

    def __init__(self, *args, **kwargs):
        self.base_fields['nome'].widget = forms.TextInput(
            attrs={'class': 'input-xxlarge', 'placeholder': 'Insira o nome do documento', 'data-provide': 'typeahead',
                   'autocomplete': 'off'})

        super(DocumentoForm, self).__init__(*args, **kwargs)

        # coloca o atributo 'ng-model' em todos campos
        for field in self.fields:
            self.fields[field].widget.attrs['ng-model'] = 'documento.' + field


class RendaForm(CamposObrigatoriosFormMixin, forms.ModelForm):
    class Meta:
        model = Renda
        fields = (
            'numero_membros',
            'numero_membros_economicamente_ativos',
            'ganho_mensal',
            'ganho_mensal_membros',
            'tipo_renda',
            'tem_plano_saude',
            'isento_ir',
            'previdencia',
            'tem_fins_lucrativos',
            'salario_funcionario'
        )

    def __init__(self, *args, **kwargs):

        self.base_fields['numero_membros'].widget = forms.NumberInput(
            attrs={
                'min': 1,
                'readonly': config.CALCULAR_RENDA_FAMILIAR_E_MEMBROS_ASSISTIDO,
                'ng-change': 'avaliar()'
            })
        self.base_fields['numero_membros_economicamente_ativos'].widget = forms.NumberInput(
            attrs={
                'readonly': config.CALCULAR_RENDA_FAMILIAR_E_MEMBROS_ASSISTIDO,
            })
        self.base_fields['ganho_mensal'].widget = forms.TextInput(
            attrs={
                'ng-change': 'recalcular_membros(); avaliar();',
                'mask-money': None,
                'mm-options': '{prefix:\'R$ \', allowZero: true, thousands:\'.\', decimal:\',\', affixesStay: false}',
                'title': config.MENSAGEM_RENDA_ASSISTIDO_INDIVIDUAL,
                'rel': 'tooltip',
                'data-trigger': 'focus'
            })
        self.base_fields['tipo_renda'].widget = forms.Select(
            attrs={
                'ng-change': 'avaliar()',
            })
        self.base_fields['ganho_mensal_membros'].widget = forms.TextInput(
            attrs={
                'readonly': config.CALCULAR_RENDA_FAMILIAR_E_MEMBROS_ASSISTIDO,
                'ng-change': 'avaliar()',
                'mask-money': None,
                'mm-options': '{prefix:\'R$ \', allowZero: true, thousands:\'.\', decimal:\',\', affixesStay: false}',
                'title': config.MENSAGEM_RENDA_ASSISTIDO_FAMILIAR,
                'rel': 'tooltip',
                'data-trigger': 'focus'
            })
        self.base_fields['tem_plano_saude'].widget = forms.Select(
            choices=[(1, 'Sim'), (0, 'Não')],
            attrs={
                'class': 'input-mini'})

        self.base_fields['isento_ir'].widget = forms.Select(
            choices=[(1, 'Sim'), (0, 'Não')],
            attrs={
                'class': 'input-mini'})

        self.base_fields['previdencia'].widget = forms.Select(
            choices=[(1, 'Sim'), (0, 'Não')],
            attrs={
                'class': 'input-mini'})

        # Atributos para Pessoa Jurídica
        self.base_fields['salario_funcionario'].widget = forms.TextInput(
            attrs={
                'ng-change': 'avaliar()',
                'mask-money': None,
                'mm-options': '{prefix:\'R$ \', allowZero: true, thousands:\'.\', decimal:\',\', affixesStay: false}',
                'title': config.MENSAGEM_VALOR_SALARIO_FUNCIONARIO,
                'rel': 'tooltip',
                'data-trigger': 'focus'
            })
        self.base_fields['tem_fins_lucrativos'].widget = forms.Select(
            choices=[(1, 'Sim'), (0, 'Não')],
            attrs={
                'class': 'input-mini'})

        super(RendaForm, self).__init__(*args, **kwargs)

        # coloca o atributo 'ng-model' em todos campos
        for field in self.fields:

            self.fields[field].widget.attrs['ng-model'] = 'pessoa.' + field

            if 'ng-required' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs['ng-required'] = 'true'


class CadastrarDependentes(CamposObrigatoriosFormMixin, forms.ModelForm):

    class Meta:
        model = Dependente
        exclude = ('membro',)

    def __init__(self, *args, **kwargs):
        self.base_fields['parentesco'].widget = forms.Select(choices=Dependente.GRAU_PARENTESCO)
        self.base_fields['nome'].widget = forms.TextInput(attrs={'class': 'span4', 'placeholder': 'Parentesco'})
        self.base_fields['renda'].widget = forms.TextInput(
            attrs={
                'ng-change': 'avaliar()',
                'mask-money': None,
                'mm-options': '{prefix:\'R$ \', allowZero: true, thousands:\'.\', decimal:\',\', affixesStay: false}',
                'title': config.MENSAGEM_RENDA_ASSISTIDO_INDIVIDUAL,
                'rel': 'tooltip',
                'data-trigger': 'focus'
            })

        super(CadastrarDependentes, self).__init__(*args, **kwargs)

        # coloca o atributo 'ng-model' em todos campos
        for field in self.fields:
            self.fields[field].widget.attrs['ng-model'] = 'pai.' + field
