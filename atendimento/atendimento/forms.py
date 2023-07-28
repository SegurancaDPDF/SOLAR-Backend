# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from collections import OrderedDict
from datetime import date
from django.conf import settings

from django import forms
from django.urls import reverse_lazy
from django.forms.utils import ErrorList
from django_addanother.widgets import AddAnotherWidgetWrapper
from django_currentuser.middleware import get_current_user
from djdocuments.models import Documento as DocumentoOnLine, TipoDocumento as TipoDocumentoOnLine
from djdocuments.forms import (
    CriarDocumentoForm,
    TipoDocumentoTemplateModelChoiceField,
    ModeloDocumentoTemplateModelChoiceField
)


# Solar
from assistido.models import PessoaAssistida
from contrib.forms import AngularFormMixin, BootstrapForm, RequiredFiedlsMixin
from contrib.models import Defensoria
from defensor.models import Atuacao, Defensor
from evento.models import Categoria
from nucleo.itinerante.models import Evento as Itinerante
from propac.forms import DocumentoModelChoiceField

# Modulos locais
from .models import Defensor as Atendimento, FormaAtendimento
from .models import Documento, Qualificacao, Tarefa, PastaDocumento

from djdocuments.models import Documento as DocumentoGED


class PessoaAssistidaModelChoiceField(forms.ModelChoiceField):

    def __init__(self, queryset=None, empty_label="---------",
                 cache_choices=None, required=True, widget=None, label=None,
                 initial=None, help_text='', to_field_name=None, limit_choices_to=None, *args, **kwargs):

        if not queryset:
            from assistido.models import PessoaAssistida
            queryset = PessoaAssistida.objects.ativos().only('pk', 'nome')

        # TODO: Django 3.2 verificar o init
        # super(PessoaAssistidaModelChoiceField, self).__init__(queryset, empty_label, cache_choices, required, widget,
        #                                                       label, initial, help_text, to_field_name,
        #                                                       limit_choices_to, **kwargs)
        self.queryset = queryset
        self.empty_label = empty_label
        self.cache_choices = cache_choices
        self.required = required
        self.widget = widget
        self.label = label
        self.initial = initial
        self.help_text = help_text
        self.to_field_name = to_field_name
        self.limit_choices_to = limit_choices_to

    def label_from_instance(self, obj):
        return obj.nome


class CriarDocumentoOnlineParaAtendimentoForm(CriarDocumentoForm):

    pessoa = forms.ModelChoiceField(
        queryset=PessoaAssistida.objects.ativos().only('pk', 'nome'),
        label="Vincular a uma pessoa?",
        required=False
    )

    pasta = forms.ModelChoiceField(
        queryset=PastaDocumento.objects.none(),
        empty_label="(Sem pasta)",
        required=False
    )

    def __init__(self, *args, **kwargs):

        atendimento = kwargs.pop('atendimento')

        super(CriarDocumentoOnlineParaAtendimentoForm, self).__init__(*args, **kwargs)

        if atendimento:
            pks_pessoas_assistidas = tuple(atendimento.pessoas.order_by().values_list('pessoa__pk'))
            self.fields['pessoa'].queryset = self.fields['pessoa'].queryset.filter(pk__in=pks_pessoas_assistidas)

        # hack feio, para django <=1.8, para mudar a ordem dos campos
        pessoa_field = self.fields['pessoa']
        assunto_field = self.fields['assunto']
        del self.fields['pessoa']
        del self.fields['assunto']

        new_fields = OrderedDict()
        new_fields['assunto'] = assunto_field
        new_fields['pessoa'] = pessoa_field

        self.fields['pasta'].queryset = PastaDocumento.objects.filter(
            atendimento=atendimento.at_inicial
        ).only('pk', 'nome')

        for field_name in self.fields.keys():
            new_fields[field_name] = self.fields.get(field_name)

        self.fields = new_fields


class CriarDocumentoOnlineParaAtendimentoViaModeloPublicoForm(CriarDocumentoOnlineParaAtendimentoForm):
    tipo_documento = TipoDocumentoTemplateModelChoiceField(
        label='Tipo de Documento',
        queryset=TipoDocumentoOnLine.objects.all(),
    )

    modelo_documento = ModeloDocumentoTemplateModelChoiceField(
        label='Modelo de Documento',
        queryset=DocumentoOnLine.admin_objects.filter(
            esta_ativo=True,
            modelo_publico=True,
            modelo_pronto_para_utilizacao=True,

        ),
        to_field_name='pk_uuid',
    )

    def __init__(self, *args, **kwargs):

        super(CriarDocumentoOnlineParaAtendimentoViaModeloPublicoForm, self).__init__(*args, **kwargs)

        if self.initial.get('tipo_documento'):
            self.fields['tipo_documento'].queryset = self.fields['tipo_documento'].queryset.filter(
                id=self.initial.get('tipo_documento')
            )

        if self.initial.get('modelo_documento'):
            self.fields['modelo_documento'].queryset = self.fields['modelo_documento'].queryset.filter(
                pk_uuid=self.initial.get('modelo_documento')
            )


class AtendimentoDefensorForm(forms.ModelForm):
    finalizado = forms.BooleanField(required=False)

    class Meta:
        model = Atendimento
        fields = ['defensoria', 'historico', 'data_atendimento']
        widgets = {
            'historico': forms.Textarea(attrs={'show-redactor': ''}),
        }

    def __init__(self, *args, **kwargs):

        super(AtendimentoDefensorForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['ng-model'] = 'atendimento.{}'.format(field)

    def is_valid(self):

        valid = super(AtendimentoDefensorForm, self).is_valid()

        if self.instance.data_agendamento and \
                'data_atendimento' in self.cleaned_data and \
                'defensoria' in self.cleaned_data and \
                self.cleaned_data['data_atendimento'] and \
                self.cleaned_data['data_atendimento'].date() != date.today() and \
                self.cleaned_data['data_atendimento'].date() != self.instance.data_agendamento.date() or \
                self.cleaned_data['defensoria'].nucleo and \
                self.cleaned_data['defensoria'].nucleo.itinerante:

            itinerante = Itinerante.objects.filter(
                participantes=self.instance.defensor.servidor,
                defensoria=self.cleaned_data['defensoria'],
                data_inicial__lte=self.cleaned_data['data_atendimento'],
                data_final__gte=self.cleaned_data['data_atendimento'],
                ativo=True
            ).exclude(
                autorizado_por=None
            ).first()

            if itinerante:
                self.instance.comarca = itinerante.municipio.comarca
            else:
                valid = False
                self._errors['data_atendimento'] = ErrorList([
                    u'Informe uma data válida!'
                ])
        else:
            self.instance.comarca = self.cleaned_data['defensoria'].comarca

        if 'forma_atendimento' not in self.data or self.data['forma_atendimento'] is None:
            valid = False
            self._errors['forma_atendimento'] = ErrorList([
                u'Informe uma forma de atendimento!'
            ])

        return valid


class UsuarioLogadoMixin(object):
    usuario = None

    def __init__(self, *args, **kwargs):

        if self.usuario is None:
            self.usuario = get_current_user()

        super(UsuarioLogadoMixin, self).__init__(*args, **kwargs)


class FiltroDefensoresUsuarioMixin(UsuarioLogadoMixin):

    def __init__(self, *args, **kwargs):

        super(FiltroDefensoresUsuarioMixin, self).__init__(*args, **kwargs)

        if hasattr(self.usuario.servidor, 'defensor'):
            if self.usuario.servidor.defensor.eh_defensor:
                self.fields['defensor'].queryset = Defensor.objects.filter(id=self.usuario.servidor.defensor.id)
            else:
                self.fields['defensor'].queryset = self.usuario.servidor.defensor.lista_supervisores


class FiltroDefensoriasUsuarioMixin(object):

    def __init__(self, *args, **kwargs):

        super(FiltroDefensoriasUsuarioMixin, self).__init__(*args, **kwargs)

        if hasattr(self.usuario.servidor, 'defensor'):
            self.fields['defensoria'].queryset = self.usuario.servidor.defensor.defensorias


class AtuacaoBootstrapFormField(AngularFormMixin, RequiredFiedlsMixin, BootstrapForm):

    atuacao = forms.ModelChoiceField(
        label='Defensoria/Defensor',
        widget=forms.Select(attrs={'class': 'span12'}),
        queryset=Atuacao.objects.vigentes().filter(defensor__eh_defensor=True),
        required=False
    )

    def __init__(self, *args, **kwargs):

        super(AtuacaoBootstrapFormField, self).__init__(*args, **kwargs)

        # Mostra apenas as defensorias onde a pessoa logada tem atuação
        user = get_current_user()
        user_atuacoes_vigentes = user.servidor.defensor.atuacoes_vigentes().values_list('defensoria_id', flat=True)

        if user_atuacoes_vigentes:

            query_atuacoes = Atuacao.objects.vigentes_por_defensoria(defensorias=user_atuacoes_vigentes)

            # Se for defensor, mostra apenas as atuações dele
            if user.servidor.defensor.eh_defensor:
                query_atuacoes = query_atuacoes.filter(defensor=user.servidor.defensor)

        else:
            query_atuacoes = Atuacao.objects.none()

        self.fields['atuacao'].queryset = query_atuacoes

    def is_valid(self):

        valid = super(AtuacaoBootstrapFormField, self).is_valid()

        # Defensor selecionado deve atuar na defensoria selecionada
        if self.cleaned_data.get('defensor') and self.cleaned_data.get('defensoria'):
            if not self.cleaned_data.get('defensor').atuacoes_vigentes().filter(defensoria=self.cleaned_data.get('defensoria')).exists():  # noqa: E501
                valid = False
                self._errors['defensor'] = ErrorList([
                    u'O defensor selecionado não atua na defensoria selecionada!'
                ])

        return valid


class AnotacaoForm(AtuacaoBootstrapFormField):
    if settings.SIGLA_UF.upper() == 'AM':
        atuacao = forms.CharField(required=False, widget=forms.HiddenInput())
        required_fields = ['historico']
    else:
        required_fields = ['atuacao', 'qualificacao', 'historico']

    def __init__(self, *args, **kwargs):
        super(AnotacaoForm, self).__init__(*args, **kwargs)
        if not settings.SIGLA_UF.upper() == 'AM':
            self.fields['qualificacao'].queryset = Qualificacao.objects.ativos().anotacoes()

    class Meta:
        model = Atendimento
        fields = ['historico'] if settings.SIGLA_UF.upper() == 'AM' else ['atuacao', 'qualificacao', 'historico']
        widgets = {
            'historico': forms.Textarea(attrs={
                'rows': '10',
                'class': 'span12',
                'placeholder': 'Digite a anotação...'
            }),
        }
        if not settings.SIGLA_UF.upper() == 'AM':
            widgets['qualificacao'] = forms.Select(attrs={
                'class': 'span12'
            })


class NotificacaoForm(AtuacaoBootstrapFormField):

    required_fields = ['atuacao', 'qualificacao', 'historico']

    def __init__(self, *args, **kwargs):
        super(NotificacaoForm, self).__init__(*args, **kwargs)
        self.fields['qualificacao'].queryset = Qualificacao.objects.ativos().notificacoes()

    class Meta:
        model = Atendimento
        fields = ['atuacao', 'qualificacao', 'historico']
        labels = {
            'historico': 'Mensagem que será enviada:'
        }
        widgets = {
            'qualificacao': forms.Select(attrs={
                'class': 'span12'
            }),
            'historico': forms.Textarea(attrs={
                'rows': '10',
                'class': 'span12',
                'placeholder': 'Digite a mensagem que será enviada...'
            }),
        }


class NucleoPedidoForm(forms.ModelForm):
    class Meta:
        model = Atendimento
        fields = ['historico', 'nucleo']


class NucleoRespostaForm(forms.ModelForm):
    class Meta:
        model = Atendimento
        fields = ['defensoria', 'nucleo', 'qualificacao', 'data_agendamento']

    def is_valid(self):

        valid = super(NucleoRespostaForm, self).is_valid()

        if self.cleaned_data.get('data_agendamento') is None or self.cleaned_data['data_agendamento'].date() < date.today():  # noqa
            valid = False
            self._errors['data_agendamento'] = ErrorList([
                u'Informe uma data válida!'
            ])

        return valid


class AgendarNucleoDiligenciaForm(BootstrapForm):

    historico = forms.CharField(widget=forms.Textarea(attrs={'class': 'span12', 'rows': 3}))

    class Meta:
        model = Atendimento
        fields = [
            'qualificacao',
            'defensor',
            'defensoria',
            'data_agendamento',
            'historico'
        ]
        # ajustes css
        widgets = {
            'qualificacao': forms.Select(attrs={'class': 'span12'}),
            'defensor': forms.HiddenInput(),
            'defensoria': forms.Select(attrs={'class': 'span12'}),
            'data_agendamento': forms.TextInput(attrs={
                'class': 'datepicker',
                'data-date-format': 'dd/mm/yyyy',
                'data-mask': '99/99/9999',
            }),
        }

    def __init__(self, *args, **kwargs):

        super(AgendarNucleoDiligenciaForm, self).__init__(*args, **kwargs)

        self.fields['defensoria'].queryset = self.fields['defensoria'].queryset.ativos().filter(
            nucleo__diligencia=True
        )

        self.fields['qualificacao'].queryset = self.fields['qualificacao'].queryset.ativos().pedidos().filter(
            nucleo__diligencia=True
        )

    def clean_data_agendamento(self):

        data_agendamento = self.cleaned_data['data_agendamento']

        if data_agendamento.date() < date.today():
            raise forms.ValidationError("A data de agendamento não pode ser menor que hoje")

        return data_agendamento


class BuscarAtendimentoForm(forms.Form):
    TIPO_NORMAL = 0
    TIPO_ACORDO = 1
    TIPO_NUCLEO = 2

    LISTA_TIPO = (
        (0, 'Normal'),
        (1, 'Acordo'),
        (2, 'Apoio'),
    )

    SITUACAO_AGENDADO = 1
    SITUACAO_REALIZADO = 2
    SITUACAO_EXCLUIDO = 3

    LISTA_SITUACAO = (
        (SITUACAO_AGENDADO, 'Agendado'),
        (SITUACAO_REALIZADO, 'Realizado'),
        (SITUACAO_EXCLUIDO, 'Excluido')
    )

    data_ini = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'ng-model': 'filtro.data_ini',
                'ng-change': 'validar()',
                'bs-datepicker': True,
                'data-date-format': 'dd/mm/yy',
                'class': 'span12',
                'autocomplete': 'off',
                'placeholder': 'Data Inicial'}))

    data_fim = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'ng-model': 'filtro.data_fim',
                'ng-change': 'validar()',
                'bs-datepicker': True,
                'data-date-format': 'dd/mm/yy',
                'class': 'span12',
                'autocomplete': 'off',
                'placeholder': 'Data Final'}))

    filtro = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'ng-model': 'filtro.filtro',
                'ng-change': 'validar()',
                'class': 'span3',
                'placeholder': 'Nº do atendimento, nome ou CPF/CNPJ do assistido...'}))

    defensor = forms.ModelChoiceField(
        required=False,
        empty_label='< TODOS DEFENSORES >',
        # Listar também assessores para acesso via calendário de agendamentos
        queryset=Defensor.objects.select_related('servidor').filter(ativo=True),
        widget=forms.Select(
            attrs={
                'ng-model': 'filtro.defensor',
                'ng-change': 'validar()',
                'class': 'span3'}))

    defensoria = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Defensoria.objects.filter(ativo=True).order_by('nucleo__nome', 'comarca__nome', 'numero'),
        widget=forms.Select(
            attrs={
                'ng-model': 'filtro.defensoria',
                'ng-change': 'validar()',
                'class': 'span3'}))

    categoria_de_agenda = forms.ModelChoiceField(
        empty_label='< TODAS CATEGORIAS >',
        queryset=Categoria.objects.ativos(),
        required=False,
        widget=forms.Select(
            attrs={
                'ng-model': 'filtro.categoria_de_agenda',
                'ng-change': 'validar()',
                'class': 'span3'}))

    situacao = forms.ChoiceField(
        choices=((None, '< Todos >'),) + LISTA_SITUACAO,
        required=False,
        widget=forms.Select(
            attrs={
                'ng-model': 'filtro.situacao',
                'ng-change': 'validar()',
                'class': 'span2'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obs: ModelMultipleChoiceField não aceita empty_label na declaração do field
        self.fields['defensoria'].empty_label = "< TODAS DEFENSORIAS >"

    def is_valid(self):

        if super().is_valid():

            if self.cleaned_data['data_ini'] or \
                    self.cleaned_data['data_fim'] or \
                    self.cleaned_data['defensor'] or \
                    self.cleaned_data['defensoria'] or \
                    self.cleaned_data['filtro']:

                return True

        return False

    def clean_situacao(self):
        value = self.cleaned_data['situacao']

        if value and value.isdigit():
            value = int(value)
        else:
            value = None

        return value


class BuscarAtendimentoConflitoForm(forms.Form):
    data_ini = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'ng-model': 'filtro.data_ini',
                'ng-change': 'validar()',
                'bs-datepicker': True,
                'data-date-format': 'dd/mm/yy',
                'class': 'span12',
                'autocomplete': 'off',
                'placeholder': 'Data Inicial'}))

    data_fim = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'ng-model': 'filtro.data_fim',
                'ng-change': 'validar()',
                'bs-datepicker': True,
                'data-date-format': 'dd/mm/yy',
                'class': 'span12',
                'autocomplete': 'off',
                'placeholder': 'Data Final'}))

    defensor = forms.ModelChoiceField(
        required=False,
        empty_label='< TODOS DEFENSORES >',
        queryset=Defensor.objects.select_related('servidor').filter(ativo=True, eh_defensor=True),
        widget=forms.Select(
            attrs={
                'ng-model': 'filtro.defensor',
                'ng-change': 'validar()',
                'class': 'span3'}))

    categoria_de_agenda = forms.ModelChoiceField(
        empty_label='< TODAS CATEGORIAS >',
        queryset=Categoria.objects.ativos(),
        required=False,
        widget=forms.Select(
            attrs={
                'ng-model': 'filtro.categoria_de_agenda',
                'ng-change': 'validar()',
                'class': 'span3'}))

    def is_valid(self):

        if super().is_valid():

            if self.cleaned_data['data_ini'] or \
                    self.cleaned_data['data_fim'] or \
                    self.cleaned_data['defensor']:

                return True

        return False


class BuscarAtendimentoDocumentosForm(forms.Form):
    filtro = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'span11', 'placeholder': 'Nº do atendimento, nome ou cpf do assistido...'}))


# Persolalizar ModelChoiceField widget para o nome do GED da lista de escolhas de modelos
class ModeloGEDModelChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        if obj.eh_modelo:
            descricao = obj.modelo_descricao if obj.modelo_descricao else 'Descricao modelo: {}'.format(obj.pk)
            ret = f'{descricao.upper()} [ CRIADO POR: {obj.criado_por.first_name} {obj.criado_por.last_name} ]'
        else:
            ret = f'{obj.assunto} - {obj.criado_por.first_name} {obj.criado_por.last_name} <{obj.criado_por.username.lower()}>'  # noqa: E501
        return ret


class TabDocumentoForm(forms.Form):

    assunto = forms.CharField(
        required=True,
        label='Assunto do Documento',
        max_length=70,
        widget=forms.TextInput(
            attrs={
                'class': 'span5 pull-left',
                'placeholder': 'Assunto da Petição'})
    )

    modelo = ModeloGEDModelChoiceField(
        required=True,
        label='Modelo do Documento',
        to_field_name='pk_uuid',
        queryset=DocumentoGED.admin_objects.select_related(
            'criado_por',
        ).filter(
            eh_modelo=True,
            esta_ativo=True
        ).only(
            'id',
            'assunto',
            'modelo_descricao',
            'eh_modelo',
            'criado_por'
        ).order_by(
            '-eh_modelo_padrao',
            'modelo_descricao'
        ),
        widget=forms.Select(
            attrs={
                'class': 'span4 pull-left'})
    )

    def __init__(self, *args, **kwargs):
        # Obtém dados do usuário logado
        usuario = kwargs.pop('usuario', None)

        super(TabDocumentoForm, self).__init__(*args, **kwargs)

        # Query para listar os GEDs da defensoria do defensor.
        if usuario and not usuario.is_superuser:
            self.fields['modelo'].queryset = self.fields['modelo'].queryset.filter(
                grupo_dono__in=usuario.servidor.defensor.defensorias
            )


class BuscarTarefaForm(forms.Form):
    data_inicial = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'span1 datepicker',
                'autocomplete': 'off',
                'placeholder': 'Data Inicial',
                'data-date-format': 'dd/mm/yyyy'}))

    data_final = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'span1 datepicker',
                'autocomplete': 'off',
                'placeholder': 'Data Final',
                'data-date-format': 'dd/mm/yyyy'}))

    setor_responsavel = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'span3 ativar-select2'}),
        empty_label='< Selecione uma defensoria >',
        queryset=Defensoria.objects.filter(ativo=True)
    )

    responsavel = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'span3 ativar-select2'}),
        empty_label='< Selecione um responsável >',
        queryset=Defensor.objects.select_related('servidor__usuario').order_by('servidor__nome')
    )

    situacao = forms.MultipleChoiceField(
        choices=((None, '< Selecione o status >'),) + Tarefa.LISTA_STATUS_BUSCA,
        required=False,
        widget=forms.SelectMultiple(
            attrs={'class': 'span2 ativar-select2'}))

    prioridade = forms.MultipleChoiceField(
        choices=((None, '< Selecione a prioridade >'),) + Tarefa.LISTA_PRIORIDADE,
        required=False,
        widget=forms.SelectMultiple(
            attrs={'class': 'span2 ativar-select2'}))

    def clean_situacao(self):
        situacoes = self.cleaned_data['situacao']
        if isinstance(situacoes, list):
            return [int(situacao) for situacao in situacoes if situacao.isdigit()]

        return []

    def clean_prioridade(self):
        prioridades = self.cleaned_data['prioridade']
        if isinstance(prioridades, list):
            return [int(prioridade) for prioridade in prioridades if prioridade.isdigit()]

        return []

    def __init__(self, *args, **kwargs):

        # Obtém dados do usuário logado
        usuario = kwargs.pop('usuario', None)

        super(BuscarTarefaForm, self).__init__(*args, **kwargs)

        # Se usuário não tem permissão para ver todos atendimentos, restringe informações de acordo com suas lotações
        if not usuario.has_perm(perm='atendimento.view_all_atendimentos'):
            self.fields['setor_responsavel'].queryset = usuario.servidor.defensor.defensorias
            self.fields['responsavel'].queryset = usuario.servidor.defensor.lista_lotados


class DistribuirAtendimentoForm(forms.Form):
    data_ini = forms.DateField(widget=forms.DateInput(
        attrs={'class': 'span2 datepicker', 'placeholder': 'Data Inicial', 'data-date-format': 'dd/mm/yyyy'}))

    defensor = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class': 'span3'}),
        empty_label="Selecione um defensor...",
        queryset=Defensor.objects.filter(
            all_atuacoes__defensoria__nucleo__supervisionado=True,
            all_atuacoes__ativo=True,
            eh_defensor=True,
            ativo=True
        ),
        required=False
    )

    defensoria = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class': 'span3'}),
        empty_label="Selecione uma defensoria...",
        queryset=Defensoria.objects.filter(nucleo__supervisionado=True, ativo=True)
    )

    forma_atendimento = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'span2'}),
        choices=((None, 'Todas formas de atendimento'),) + FormaAtendimento.LISTA_TIPO,
        required=False,
    )

    def __init__(self, usuario, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Se não é superusuário, limita visualização para lotações do usuário
        if not usuario.has_perm(perm='atendimento.view_all_atendimentos'):
            self.fields['defensoria'].queryset = usuario.servidor.defensor.defensorias.filter(
                nucleo__supervisionado=True
            )
            self.fields['defensor'].queryset = usuario.servidor.defensor.lista_supervisores

        for field in self.fields:
            self.fields[field].widget.attrs['ng-model'] = 'filtro.' + field


class DocumentoForm(forms.ModelForm):

    documento_online = DocumentoModelChoiceField(
        required=False,
        queryset=DocumentoOnLine.objects.all(),
        widget=AddAnotherWidgetWrapper(
            forms.Select(attrs={
                'ng-model': 'documento.documento_online',
            }),
            reverse_lazy('documentos:create'),

        )
    )

    class Meta:
        model = Documento
        fields = ['documento', 'documento_online', 'arquivo', 'nome', 'pessoa', 'defensoria', 'pasta']


class DocumentoUploadForm(forms.ModelForm):

    arquivo = forms.FileField(required=True)

    class Meta:
        model = Documento
        fields = ['arquivo', 'documento']


class AgendarDocumentoForm(forms.ModelForm):

    class Meta:
        model = Documento
        fields = ['prazo_resposta', 'status_resposta']


class DocumentoRespostaForm(forms.ModelForm):

    class Meta:
        model = Documento
        fields = ['arquivo']


class QualificacaoModalForm(BootstrapForm):

    class Meta:
        model = Qualificacao
        fields = ['titulo', 'area', 'nucleo', 'especializado', 'texto', 'perguntas', 'documentos']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'span10'}),
            'area': forms.Select(attrs={'class': 'span10'}),
            'nucleo': forms.Select(attrs={'class': 'span10'}),
            'especializado': forms.Select(attrs={'class': 'span10'}),
            'texto': forms.Textarea(
                attrs={'class': 'span10',
                       'cols': '40',
                       'rows': '5',
                       'placeholder': 'Descreva a qualificação'}),
            'perguntas': forms.Textarea(
                attrs={'class': 'span10',
                       'cols': '40',
                       'rows': '5',
                       'placeholder': 'Descreva as perguntas'}),
            'documentos': forms.Textarea(
                attrs={'class': 'span10',
                       'cols': '40',
                       'rows': '5',
                       'placeholder': 'Descreva os documentos'}),
        }


class TarefaForm(forms.ModelForm):

    class Meta:
        model = Tarefa
        exclude = [
            'atendimento',
            'status',
            'ativo',
            'data_cadastro',
            'cadastrado_por',
            'data_exclusao',
            'excluido_por'
        ]


class AtividadeForm(forms.ModelForm):

    class Meta:
        model = Atendimento
        fields = ['qualificacao', 'historico', 'data_atendimento', 'multiplicador']

    def is_valid(self):

        if super(AtividadeForm, self).is_valid():

            hoje = date.today()

            if (self.cleaned_data['data_atendimento'] and
                    self.cleaned_data['data_atendimento'].date().year == hoje.year and
                    self.cleaned_data['data_atendimento'].date().month == hoje.month):
                return True

        return False


class AtividadeDefensorForm(AtividadeForm):

    class Meta:
        model = Atendimento
        fields = ['qualificacao', 'historico', 'data_atendimento', 'defensor', 'defensoria', 'multiplicador']
