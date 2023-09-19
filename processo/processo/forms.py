# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
from datetime import date, datetime, time

from django import forms
from django.db.models import Q
from django.db.models.functions import Length
from django.forms.utils import ErrorList

# Bibliotecas de terceiros
from constance import config
from dateutil.relativedelta import relativedelta
from redis import ConnectionError

# Solar
from atendimento.atendimento.models import Defensor as AtendimentoDefensor
from contrib.forms import BootstrapForm
from contrib.models import Defensoria
from defensor.models import Defensor
from evento.models import Evento
from procapi_client.services import APIOrgaoJulgador
from processo.honorarios.models import Analise, Honorario

# Modulos locais
from .models import (
    Audiencia,
    DocumentoFase,
    Fase,
    FaseTipo,
    Manifestacao,
    OutroParametro,
    Parte,
    ParteHistoricoSituacao,
    Prioridade,
    Processo
)


class AtendimentoForm(BootstrapForm):

    class Meta:
        model = AtendimentoDefensor
        fields = ['defensor', 'defensoria', 'nucleo', 'qualificacao']


class ProcessoForm(BootstrapForm):

    class Meta:
        model = Processo
        fields = ['tipo', 'numero', 'chave', 'acao', 'comarca', 'vara', 'area', 'grau']
        widgets = {
            'comarca': forms.Select(attrs={'class': 'span12', 'data-form': 'select2'}),
            'acao': forms.Select(attrs={'class': 'span12', 'data-form': 'select2'}),
            'vara': forms.Select(attrs={'class': 'span12', 'data-form': 'select2'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProcessoForm, self).__init__(*args, **kwargs)

        # coloca o atributo 'ng-model' em todos campos
        for field in self.fields:
            self.fields[field].widget.attrs['ng-model'] = 'processo.' + field


class ProcessoParteForm(BootstrapForm):
    defensoria = forms.ModelChoiceField(
        empty_label=None,
        required=False,
        queryset=Defensoria.objects.filter(ativo=True).order_by('comarca__nome', 'numero'),
        widget=forms.Select(attrs={'class': 'span12', 'data-form': 'select2'}))

    class Meta:
        model = Parte
        fields = ['parte', 'defensor_cadastro', 'defensor', 'defensoria_cadastro', 'defensoria']
        widgets = {
            'parte': forms.RadioSelect(choices=Parte.LISTA_TIPO),
            'defensor_cadastro': forms.Select(attrs={'class': 'span12', 'data-form': 'select2'}),
            'defensor': forms.Select(attrs={'class': 'span12', 'data-form': 'select2'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProcessoParteForm, self).__init__(*args, **kwargs)

        # coloca o atributo 'ng-model' em todos campos
        for field in self.fields:
            self.fields[field].widget.attrs['ng-model'] = 'parte.' + field


class RealizarAudienciaForm(forms.ModelForm):
    class Meta:
        model = Audiencia
        fields = [
            'defensor_cadastro',
            'custodia',
            'descricao',
            'data_protocolo',
            'audiencia_status',
            'audiencia_realizada'
        ]

    def is_valid(self):

        if super(RealizarAudienciaForm, self).is_valid():

            hoje = date.today()

            data_protocolo = self.cleaned_data['data_protocolo'].date()
            defensoria_protocolo = self.data['defensoria']

            evento_desbloqueio = Evento.objects.filter(
                tipo=Evento.TIPO_PERMISSAO,
                defensoria=defensoria_protocolo,
                data_autorizacao__isnull=False,
                data_ini__lte=data_protocolo,
                data_fim__gte=data_protocolo,
                data_validade__gte=hoje,
                ativo=True
            ).exists()

            # Se tem desbloqueio válido então deixa registrar
            if evento_desbloqueio and data_protocolo <= hoje:
                return True
            # Se não realiza outras validações já implementadas
            elif data_protocolo:

                hoje = date.today()

                if data_protocolo > hoje:
                    self._errors['data_protocolo'] = ErrorList([
                        u'A data deve ser menor que "{0:%d/%m/%Y}"'.format(hoje + relativedelta(days=1))
                    ])
                else:
                    return True

        return False


class HonorarioFaseForm(forms.ModelForm):

    class Meta:
        model = Honorario
        fields = ['possivel', 'valor_estimado', 'defensor', 'defensoria']


class AnaliseFaseForm(forms.ModelForm):

    class Meta:
        model = Analise
        fields = ['motivo']


class FaseForm(forms.ModelForm):

    class Meta:
        model = Fase
        fields = ['tipo', 'processo', 'parte', 'defensoria', 'defensor_cadastro', 'defensor_substituto', 'descricao',
                  'data_protocolo', 'data_termino_protocolo']

    def clean_data_termino_protocolo(self):

        value = self.cleaned_data['data_termino_protocolo']

        # Sobrescreve valor da data de término caso não esteja habilitado
        if not config.EXIBIR_DATA_HORA_TERMINO_CADASTRO_AUDIENCIA:
            value = None

        return value

    def is_valid(self):

        if super(FaseForm, self).is_valid():

            if self.cleaned_data['data_protocolo']:

                hoje = date.today()

                data_protocolo = self.cleaned_data['data_protocolo'].date()
                defensoria_protocolo = self.cleaned_data['defensoria']

                evento_desbloqueio = Evento.objects.filter(
                    tipo=Evento.TIPO_PERMISSAO,
                    defensoria=defensoria_protocolo,
                    data_autorizacao__isnull=False,
                    data_ini__lte=data_protocolo,
                    data_fim__gte=data_protocolo,
                    data_validade__gte=hoje,
                    ativo=True
                ).exists()

                # Se tem desbloqueio válido então deixa registrar
                if evento_desbloqueio:
                    return True
                # Se não realiza outras validações já implementadas
                else:

                    dia_um = date(hoje.year, hoje.month, 1)

                    if hoje.day <= config.DIA_LIMITE_CADASTRO_FASE:
                        dia_um -= relativedelta(months=1)

                    if data_protocolo < dia_um:
                        self._errors['data_protocolo'] = ErrorList([
                            u'A data deve ser maior que "{0:%d/%m/%Y}"'.format(dia_um - relativedelta(days=1))
                        ])
                    elif data_protocolo > hoje:
                        self._errors['data_protocolo'] = ErrorList([
                            u'A data deve ser menor que "{0:%d/%m/%Y}"'.format(hoje + relativedelta(days=1))
                        ])
                    else:
                        return True

        return False


class AudienciaForm(forms.ModelForm):

    class Meta:
        model = Audiencia
        fields = ['tipo', 'processo', 'parte', 'defensoria', 'defensor_cadastro', 'defensor_substituto', 'descricao',
                  'data_protocolo', 'data_termino_protocolo', 'audiencia_status', 'audiencia_realizada', 'custodia']

    def clean_data_termino_protocolo(self):

        value = self.cleaned_data['data_termino_protocolo']

        # Sobrescreve valor da data de término caso não esteja habilitado
        if not config.EXIBIR_DATA_HORA_TERMINO_CADASTRO_AUDIENCIA:
            value = None

        return value

    def is_valid(self):

        if super(AudienciaForm, self).is_valid():

            hoje = date.today()

            if self.cleaned_data['audiencia_status'] == Audiencia.AUDIENCIA_MARCADA:

                if self.cleaned_data['data_protocolo'].date() < hoje:
                    self._errors['data_protocolo'] = ErrorList([
                        u'A data deve ser maior que "{0:%d/%m/%Y}"'.format(hoje - relativedelta(days=1))
                    ])
                else:
                    return True

            else:

                dia_um = date(hoje.year, hoje.month, 1)

                data_protocolo = self.cleaned_data['data_protocolo'].date()
                defensoria_protocolo = self.cleaned_data['defensoria']

                evento_desbloqueio = Evento.objects.filter(
                    tipo=Evento.TIPO_PERMISSAO,
                    defensoria=defensoria_protocolo,
                    data_autorizacao__isnull=False,
                    data_ini__lte=data_protocolo,
                    data_fim__gte=data_protocolo,
                    data_validade__gte=hoje,
                    ativo=True
                ).exists()
                # Se tem desbloqueio vigente, deixa cadastrar
                if evento_desbloqueio:
                    return True

                if hoje.day <= config.DIA_LIMITE_CADASTRO_FASE:
                    dia_um -= relativedelta(months=1)

                if self.cleaned_data['data_protocolo'].date() < dia_um:
                    self._errors['data_protocolo'] = ErrorList([
                        u'A data deve ser maior que "{0:%d/%m/%Y}"'.format(dia_um - relativedelta(days=1))
                    ])
                elif self.cleaned_data['data_protocolo'].date() > hoje:
                    self._errors['data_protocolo'] = ErrorList([
                        u'A data deve ser menor que "{0:%d/%m/%Y}"'.format(hoje + relativedelta(days=1))
                    ])
                else:
                    return True

        return False


class BuscarManifestacaoForm(forms.Form):

    usa_defensor = True
    usa_defensoria = True

    # Tratamento de Erros do Redis Durante Build no CI/CD Gitlab
    try:
        usa_defensor = config.VINCULAR_NA_DISTRIBUICAO_AVISO_A_DEFENSOR_AUTOMATICAMENTE
        usa_defensoria = config.VINCULAR_NA_DISTRIBUICAO_AVISO_A_DEFENSORIA_AUTOMATICAMENTE
    except ConnectionError:
        # Ignora erro propositalmente
        pass
    except NameError:
        # Ignora erro propositalmente
        pass

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
        widget=forms.Select(attrs={
            'class': 'span3 ativar-select2',
            'disabled': not usa_defensoria
        }),
        empty_label='< TODAS DEFENSORIAS >',
        queryset=Defensoria.objects.ativos()
    )

    responsavel = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'span3 ativar-select2'
        }),
        empty_label='< TODOS RESPONSÁVEIS >',
        queryset=Defensor.objects.select_related('servidor').order_by('servidor__nome')
    )

    situacao = forms.ChoiceField(
        choices=((None, '< TODAS SITUAÇÕES >'),) + Manifestacao.LISTA_SITUACAO,
        required=False,
        widget=forms.Select(
            attrs={'class': 'span2 ativar-select2'}))

    def clean_situacao(self):
        value = self.cleaned_data['situacao']

        if value and value.isdigit():
            value = int(value)
        else:
            value = None

        return value

    def __init__(self, *args, **kwargs):

        # Obtém dados do usuário logado
        usuario = kwargs.pop('usuario', None)

        super().__init__(*args, **kwargs)

        # Se usuário não tem permissão para ver todos atendimentos, restringe informações de acordo com suas lotações
        if not usuario.has_perm(perm='atendimento.view_all_atendimentos'):
            self.fields['setor_responsavel'].queryset = usuario.servidor.defensor.defensorias
            self.fields['responsavel'].queryset = usuario.servidor.defensor.lista_lotados


class BuscarProcessoForm(forms.Form):

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
                'placeholder': 'Data Inicial',
                'title': 'Data Inicial da Movimentação Processual',
                'bs-tooltip': ''}))

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
                'placeholder': 'Data Final',
                'title': 'Data Final da Movimentação Processual',
                'bs-tooltip': ''}))

    filtro = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'ng-model': 'filtro.filtro',
                'ng-change': 'validar()',
                'class': 'span3',
                'placeholder': 'Nº do processo, nome ou CPF/CNPJ do assistido...'}))

    defensor = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(
            attrs={
                'ng-model': 'filtro.defensor',
                'ng-change': 'validar()',
                'class': 'span3'}
        ),
        empty_label='< TODOS DEFENSORES >',
        queryset=Defensor.objects.filter(eh_defensor=True, ativo=True)
    )

    defensoria = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(
            attrs={
                'ng-model': 'filtro.defensoria',
                'ng-change': 'validar()',
                'class': 'span3'}
        ),
        empty_label='< TODAS DEFENSORIAS >',
        queryset=Defensoria.objects.ativos()
    )

    situacao = forms.ChoiceField(
        choices=((None, '<TODAS SITUAÇÕES>'),) + ParteHistoricoSituacao.LISTA_STATUS_ACOMPANHAMENTO,
        required=False,
        widget=forms.Select(
            attrs={
                'ng-model': 'filtro.situacao',
                'ng-change': 'validar()',
                'class': 'span2'
            }
        )
    )

    def is_valid(self):
        if super(BuscarProcessoForm, self).is_valid():
            if self.cleaned_data['data_ini'] or \
                    self.cleaned_data['data_fim'] or \
                    self.cleaned_data['defensor'] or \
                    self.cleaned_data['defensoria'] or \
                    self.cleaned_data['situacao'] or \
                    self.cleaned_data['filtro']:
                return True
        return False

    def clean_data_fim(self):
        data_fim = self.cleaned_data.get('data_fim', None)
        if data_fim:
            data_fim = datetime.combine(data_fim, time.max)
        return data_fim

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not config.ATIVAR_ACOMPANHAMENTO_PROCESSO:
            self.fields['situacao'].widget = forms.HiddenInput()


class BuscarProcessoAudienciaForm(forms.Form):
    data_ini = forms.DateField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'ng-model': 'filtro.data_ini',
                'ng-change': 'validar()',
                'autocomplete': 'off',
                'class': 'span1 datepicker',
                'placeholder': 'Data Inicial',
                'data-date-format': 'dd/mm/yy'}))

    data_fim = forms.DateField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'ng-model': 'filtro.data_fim',
                'ng-change': 'validar()',
                'autocomplete': 'off',
                'class': 'span1 datepicker',
                'placeholder': 'Data Final',
                'data-date-format': 'dd/mm/yy'}))
    defensor = forms.ChoiceField(
        required=False,
        widget=forms.Select())

    defensoria = forms.ChoiceField(
        required=False,
        widget=forms.Select())

    filtro = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'ng-model': 'filtro.filtro',
                'class': 'span3',
                'placeholder': 'Nº do processo...'}))

    def __init__(self, *args, **kwargs):
        super(BuscarProcessoAudienciaForm, self).__init__(*args, **kwargs)

        defensores = [['', '< TODOS DEFENSORES >']]
        # TODO: For em queryset executa a query
        # Verificar possivel gargalo de desempenho
        for defensor in Defensor.objects.filter(ativo=True).order_by('servidor__nome').values_list('id', 'servidor__nome'):  # noqa
            defensores.append([defensor[0], defensor[1]])

        self.fields['defensor'].choices = defensores

        defensorias = [['', '< TODAS DEFENSORIAS >']]

        for defensoria in Defensoria.objects.filter(ativo=True, nucleo=None).order_by('comarca__nome', 'numero').values_list('id', 'nome'):  # noqa
            defensorias.append([defensoria[0], defensoria[1]])

        for defensoria in Defensoria.objects.filter(ativo=True).exclude(nucleo=None).order_by('nucleo__nome', 'comarca__nome').values_list('id', 'nome'):  # noqa
            defensorias.append([defensoria[0], defensoria[1]])

        self.fields['defensoria'].choices = defensorias


class DocumentoFaseForm(forms.ModelForm):

    class Meta:
        model = DocumentoFase
        exclude = ['fase', 'tipo', 'ativo', 'data_enviado', 'enviado_por']


class ChoiceFieldNoValidation(forms.ChoiceField):
    def validate(self, value):
        pass


class MultipleChoiceFieldNoValidation(forms.MultipleChoiceField):
    def validate(self, value):
        pass


class ProcessoPeticionamentoForm(forms.ModelForm):
    acao_form = ChoiceFieldNoValidation(
        label='Classe',
        required=True,
        widget=forms.Select(attrs={
            'class': 'input-xxlarge ativar-select2',
        })
    )
    assunto_principal_form = ChoiceFieldNoValidation(
        label='Assunto Principal',
        required=True,
        widget=forms.Select(attrs={
            'class': 'input-xxlarge ativar-select2',
        })
    )
    assuntos_secundarios_form = MultipleChoiceFieldNoValidation(
        label='Assuntos Secundários',
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'input-xxlarge ativar-select2',
        })
    )
    competencia_mni = ChoiceFieldNoValidation(
        label='Competência Judicial',
        required=False,
        widget=forms.Select(attrs={
            'class': 'input-xxlarge ativar-select2',
        })
    )
    tipo_fase = forms.ModelChoiceField(
        label='Tipo do Evento',
        required=True,
        queryset=FaseTipo.objects.ativos().filter(judicial=True),
        widget=forms.Select(attrs={
            'class': 'input-xxlarge ativar-select2',
            'required': True,
        })
    )
    outros_parametros_form = forms.ModelMultipleChoiceField(
        label='Outros Parâmetros',
        required=False,
        queryset=OutroParametro.objects.ativos(),
        widget=forms.CheckboxSelectMultiple()
    )

    prioridades = forms.ModelMultipleChoiceField(
        label='Prioridades',
        required=False,
        queryset=Prioridade.objects.ativos().filter(disponivel_para_peticionamento=True),
        widget=forms.CheckboxSelectMultiple()
    )

    class Meta:
        model = Processo
        fields = [
            'comarca',
            'competencia_mni',
            'acao_form',
            'assunto_principal_form',
            'assuntos_secundarios_form',
            'nivel_sigilo',
            'originario',
            'tipo_fase',
            'valor_causa',
            'calculo_judicial',
            'prioridades',
            'outros_parametros_form',
            'intervencao_mp'
        ]
        widgets = {
            'comarca': forms.Select(attrs={
                'class': 'input-xxlarge ativar-select2',
                'required': True,
            }),
            'acao_form': forms.Select(attrs={
                'class': 'input-xxlarge ativar-select2',
                'required': True,
            }),
            'originario': forms.Select(attrs={
                'class': 'input-xxlarge ativar-select2',
                'required': False,
            }),
            'nivel_sigilo': forms.Select(attrs={
                'class': 'input-xxlarge ativar-select2',
                'required': True,
            }),
            'valor_causa': forms.NumberInput(attrs={
                'onkeyup': 'valorCausa(this.value)',
                'placeholder': 'Ex: 1929,55',
                'required': True,
            })
        }

    def __init__(self, atendimento, editavel, *args, **kwargs):

        sistema_webservice = kwargs.pop('sistema_webservice')

        super(ProcessoPeticionamentoForm, self).__init__(*args, **kwargs)

        if not editavel:
            for field in self.fields:
                self.fields[field].widget.attrs['disabled'] = True

        self.fields['comarca'].queryset = self.fields['comarca'].queryset.filter(
            ativo=True,
            codigo_eproc__isnull=False)

        self.fields['competencia_mni'].choices = (
            [['', '---------']]
        )

        self.fields['acao_form'].choices = (
            [['', '---------']]
        )

        self.fields['assunto_principal_form'].choices = (
            [['', '---------']]
        )

        # Exibe processos originários que tenham exatamente 20 digitos conforme padrão CNJ
        processos_originarios = atendimento.processos.annotate(
            numero_puro_len=Length('numero_puro')
        ).filter(
            pre_cadastro=False,
            numero_puro_len__in=[20]
        )

        if '2G' not in sistema_webservice and 'SEEU' not in sistema_webservice:
            processos_originarios = processos_originarios.filter(
                vara__codigo_eproc__in=APIOrgaoJulgador().obter_codigos_vara_por_sistema_webservice(
                    sistema=sistema_webservice
                )
            )

        self.fields['originario'].queryset = processos_originarios

        # Filtra tipos de fase processual vinculadas ao sistema webservice
        self.fields['tipo_fase'].queryset = self.fields['tipo_fase'].queryset.filter(
            Q(tipos_de_evento__sistema_webservice__nome=sistema_webservice) &
            (
                Q(tipos_de_evento__disponivel_em_peticao_avulsa=True) |
                Q(tipos_de_evento__disponivel_em_peticao_com_aviso=True)
            )
        )
