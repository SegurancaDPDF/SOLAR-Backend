# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from datetime import date, datetime, time, timedelta
from django import forms
from django.forms.utils import ErrorList
from django.db.models import Max, Q

# Solar
from contrib.forms import BootstrapForm
from contrib.models import Estado, Municipio, Comarca, Defensoria
from defensor.models import Defensor
from processo.processo.models import Parte, Processo

# Modulos locais
from .models import (
    Atendimento,
    EstabelecimentoPenal,
    Prisao,
    Aprisionamento,
    Falta,
    Remissao,
    Interrupcao,
    MudancaRegime
)


class PrisaoForm(BootstrapForm):  # classe de formulário para o modelo "Prisao"
    # campos para selecionar o estado e o município do local da prisão
    estado = forms.ModelChoiceField(queryset=Estado.objects.order_by('nome'), label='Estado do Local da Prisão',
                                    empty_label=None)
    municipio = forms.ModelChoiceField(
        Municipio.objects.filter(id__in=EstabelecimentoPenal.objects.values('endereco__municipio_id')),
        label='Município do Estabelecimento Penal')

    class Meta:
        # define o modelo associado ao formulário e os campos que serão exibidos
        model = Prisao
        fields = [
            'pessoa',
            'processo',
            'parte',
            'tipificacao',
            'tentado_consumado',
            'data_fato',
            'data_prisao',
            'estado',
            'local_prisao',
            'municipio',
            'estabelecimento_penal',
            'data_recebimento_denuncia',
            'data_pronuncia',
            'resultado_pronuncia',
            'historico_pronuncia',
            'resultado_sentenca',
        ]

        widgets = {
            # Define os widgets para cada campo
            'pessoa': forms.HiddenInput(),
            'processo': forms.HiddenInput(),
            'parte': forms.HiddenInput(),
            'tipificacao': forms.Select(attrs={'class': 'span12 duplicar', 'required': 'true'}),
            'data_fato': forms.DateInput(attrs={'class': 'datepicker', 'data-date-format': 'dd/mm/yyyy', 'required': 'true'}),  # noqa
            'data_prisao': forms.DateInput(attrs={'class': 'datepicker', 'data-date-format': 'dd/mm/yyyy', 'required': 'true'}),  # noqa
            'local_prisao': forms.Select(attrs={'class': 'span12', 'required': 'true'}),
            'municipio': forms.Select(attrs={'class': 'span12', 'required': 'true'}),
            'estabelecimento_penal': forms.Select(attrs={'class': 'span12', 'required': 'true'}),
            'data_recebimento_denuncia': forms.DateInput(
                attrs={'class': 'datepicker', 'data-date-format': 'dd/mm/yyyy'}),
            'data_pronuncia': forms.DateInput(attrs={'class': 'datepicker', 'data-date-format': 'dd/mm/yyyy'}),
            'historico_pronuncia': forms.Textarea(attrs={'class': 'span12 pronuncia_absolvido', 'rows': '3'}),
            'data_sentenca_condenatoria': forms.DateInput(
                attrs={'class': 'sentenca_condenado datepicker', 'data-date-format': 'dd/mm/yyyy'}),
            'data_transito_defensor': forms.DateInput(
                attrs={'class': 'sentenca_condenado datepicker', 'data-date-format': 'dd/mm/yyyy'}),
            'data_transito_acusacao': forms.DateInput(
                attrs={'class': 'sentenca_condenado datepicker', 'data-date-format': 'dd/mm/yyyy'}),
            'data_transito_apenado': forms.DateInput(
                attrs={'class': 'sentenca_condenado datepicker', 'data-date-format': 'dd/mm/yyyy'}),
            'resultado_sentenca': forms.Select(attrs={'class': 'span6'}),
        }

    def __init__(self, *args, **kw):

        self.base_fields['municipio'].widget = forms.Select(attrs={'class': 'span12'})

        super(PrisaoForm, self).__init__(*args, **kw)

        self.fields['estado'].widget.attrs = {'class': 'span2'}

        # carrega lista de estabelecimentos penais de acordo com o municipio informado
        try:
            self.fields['estabelecimento_penal'].queryset = EstabelecimentoPenal.objects.filter(
                endereco__municipio_id=kw['initial']['municipio'])
        except Exception:
            self.fields['estabelecimento_penal'].queryset = EstabelecimentoPenal.objects.none()

        # carrega lista de municipios do estado selecionado
        try:
            self.fields['local_prisao'].queryset = Municipio.objects.filter(estado_id=kw['initial']['estado'])
        except Exception:
            self.fields['local_prisao'].queryset = Municipio.objects.none()

        if self.instance:
            if self.instance.processo and self.instance.processo.acao and self.instance.processo.acao.inquerito:
                self.fields['resultado_sentenca'].widget.attrs['disabled'] = True

    def clean(self):  # método para realizar validações personalizadas no formulário
        cleaned_data = super(PrisaoForm, self).clean()

        prisoes = Prisao.objects.filter(
            pessoa=cleaned_data['pessoa'],
            processo=cleaned_data['processo'],
            tipificacao=cleaned_data['tipificacao'],
            data_fato=cleaned_data['data_fato'],
        ).exclude(
            id=self.instance.id
        ).exists()

        if prisoes:
            msg = u'Informe outra tipificação ou data do fato. ' \
                  u'A tipificação já foi cadastrada no processo "{0}" ' \
                  u'com a data do fato {1:%d/%m/%Y}. '.format(
                    cleaned_data['processo'],
                    cleaned_data['data_fato']
                    )

            self.add_error('tipificacao', msg)

        if cleaned_data['data_fato'] > date.today():
            self.add_error('data_fato', u'O fato não pode ser em data futura.')

        if self.cleaned_data['data_prisao'] > date.today():
            self.add_error('data_prisao', u'A prisão não pode ser em data futura.')

        if (self.cleaned_data['data_recebimento_denuncia'] and
                self.cleaned_data['data_recebimento_denuncia'] > date.today()):
            self.add_error('data_recebimento_denuncia', u'O recebimento da denúncia não pode ser em data futura.')

        if self.cleaned_data['data_pronuncia'] and self.cleaned_data['data_pronuncia'] > date.today():
            self.add_error('data_pronuncia', u'A pronúncia não pode ser em data futura.')

        return cleaned_data


class GuiaForm(BootstrapForm):  # definição da classe GuiaSalvarForm
    # campos do formulário e suas características
    class Meta:
        model = Prisao
        fields = ['data_sentenca_condenatoria',
                  'data_transito_defensor',
                  'data_transito_acusacao',
                  'data_transito_apenado',
                  'regime_inicial',
                  'fracao_pr',
                  'fracao_lc',
                  'duracao_pena_anos',
                  'duracao_pena_meses',
                  'duracao_pena_dias',
                  'multa',
                  ]

        widgets = {
            'regime_inicial': forms.Select(choices=Prisao.LISTA_REGIME),
            'fracao_pr': forms.Select(attrs={'class': 'duplicar'}),
            'fracao_lc': forms.Select(attrs={'class': 'duplicar'}),
            'duracao_pena_anos': forms.TextInput(attrs={'class': 'duplicar'}),
            'duracao_pena_meses': forms.TextInput(attrs={'class': 'duplicar'}),
            'duracao_pena_dias': forms.TextInput(attrs={'class': 'duplicar'}),
            'data_sentenca_condenatoria': forms.DateInput(attrs={'class': 'datepicker', 'data-date-format': 'dd/mm/yyyy'}),  # noqa
            'data_transito_defensor': forms.DateInput(attrs={'class': 'datepicker', 'data-date-format': 'dd/mm/yyyy'}),
            'data_transito_acusacao': forms.DateInput(attrs={'class': 'datepicker', 'data-date-format': 'dd/mm/yyyy'}),
            'data_transito_apenado': forms.DateInput(attrs={'class': 'datepicker', 'data-date-format': 'dd/mm/yyyy'}),
        }


class PrisaoSalvarForm(forms.ModelForm):

    class Meta:
        model = Prisao
        fields = ['pessoa',
                  'processo',
                  'parte',
                  'situacao',
                  'tipificacao',
                  'tentado_consumado',
                  'data_fato',
                  'data_prisao',
                  'local_prisao',
                  'estabelecimento_penal',
                  'data_recebimento_denuncia',
                  'data_pronuncia',
                  'resultado_pronuncia',
                  'historico_pronuncia',
                  'resultado_sentenca',
                  'regime_inicial',
                  'fracao_pr',
                  'fracao_lc',
                  'data_sentenca_condenatoria',
                  'data_transito_defensor',
                  'data_transito_acusacao',
                  'data_transito_apenado',
                  'duracao_pena_anos',
                  'duracao_pena_meses',
                  'duracao_pena_dias',
                  'multa',
                  ]

    def clean(self):
        cleaned_data = super(PrisaoSalvarForm, self).clean()
        if super(PrisaoSalvarForm, self).is_valid():

            prisoes = Prisao.objects.filter(
                pessoa=self.cleaned_data['pessoa'],
                processo=self.cleaned_data['processo'],
                tipificacao=self.cleaned_data['tipificacao'],
                data_fato=cleaned_data['data_fato'],
                tipo=Prisao.TIPO_CONDENADO,
            ).exclude(
                id=self.instance.id
            ).exists()

            if prisoes:
                msg = u'Informe outra tipificação ou data do fato. ' \
                      u'A tipificação já foi cadastrada no processo "{0}" ' \
                      u'com a data do fato {1:%d/%m/%Y}. '.format(
                        self.cleaned_data['processo'],
                        self.cleaned_data['data_fato']
                        )
                self.add_error('tipificacao', msg)

        if self.cleaned_data.get('data_fato') and cleaned_data['data_fato'] > date.today():
            self.add_error('data_fato', u'O fato não pode ser em data futura.')

        if self.cleaned_data.get('data_prisao') and self.cleaned_data['data_prisao'] > date.today():
            self.add_error('data_prisao', u'A prisão não pode ser em data futura.')

        if (self.cleaned_data.get('data_recebimento_denuncia') and
                self.cleaned_data['data_recebimento_denuncia'] > date.today()):
            self.add_error('data_recebimento_denuncia',
                           u'O recebimento da denúncia não pode ser em data futura.')

        if self.cleaned_data.get('data_pronuncia') and self.cleaned_data['data_pronuncia'] > date.today():
            self.add_error('data_pronuncia', u'A pronúncia não pode ser em data futura.')

        return cleaned_data


class GuiaSalvarForm(BootstrapForm):

    class Meta:
        model = Prisao
        fields = ['data_sentenca_condenatoria',
                  'data_transito_defensor',
                  'data_transito_acusacao',
                  'data_transito_apenado',
                  'regime_inicial',
                  'fracao_pr',
                  'fracao_lc',
                  'duracao_pena_anos',
                  'duracao_pena_meses',
                  'duracao_pena_dias',
                  'multa',
                  ]


class AtendimentoForm(forms.ModelForm):
    class Meta:
        model = Atendimento
        fields = (
            'prisao',
            'defensoria',
            'defensor',
            'substituto',
            'historico',
            'data_atendimento',
            'atendido_por',
            'tipo',
            'assunto',
            'parentesco_preso',
            'estabelecimento_penal',
            'qualificacao',
            'inicial',
            'origem',
            'forma_atendimento',
        )

    def __init__(self, *args, **kw):
        super(AtendimentoForm, self).__init__(*args, **kw)
        self.fields['prisao'].required = True
        self.fields['defensoria'].required = True
        self.fields['defensor'].required = True
        self.fields['data_atendimento'].required = True
        self.fields['estabelecimento_penal'].required = True
        self.fields['qualificacao'].required = True
        self.fields['forma_atendimento'].required = True

    def is_valid(self):

        valid = super(AtendimentoForm, self).is_valid()

        hoje = date.today()
        dia_um = datetime(hoje.year, hoje.month, 1)

        if self.cleaned_data['data_atendimento'] < dia_um:
            self._errors['data_atendimento'] = ErrorList([
                u'Deve ser maior que {0:%d/%m/%Y}'.format(dia_um - timedelta(days=1))
            ])
            valid = False
        elif self.cleaned_data['data_atendimento'] > datetime.combine(date.today(), time.max):
            self._errors['data_atendimento'] = ErrorList([
                u'Deve ser menor que {0:%d/%m/%Y}'.format(date.today() + timedelta(days=1))
            ])
            valid = False

        return valid


class AlterarAtendimentoForm(AtendimentoForm):
    class Meta:
        model = Atendimento
        fields = (
            'prisao',
            'defensoria',
            'defensor',
            'substituto',
            'historico',
            'data_atendimento',
            'atendido_por',
            'tipo',
            'assunto',
            'parentesco_preso',
            'estabelecimento_penal',
            'qualificacao',
            'forma_atendimento',
        )


class EstabelecimentoPenalForm(BootstrapForm):
    class Meta:
        model = EstabelecimentoPenal
        fields = ('nome', 'email', 'tipo', 'destinado_ao_sexo', 'inspecionado_pela_dpe')

    def __init__(self, *args, **kwargs):
        self.base_fields['nome'].widget = forms.TextInput(attrs={'class': 'span9', 'data-validate': '{required:true}'})
        super(EstabelecimentoPenalForm, self).__init__(*args, **kwargs)


class ProcessoForm(BootstrapForm):
    class Meta:
        model = Processo
        fields = ['id', 'numero', 'chave', 'area']
        widgets = {
            'numero': forms.TextInput(attrs={'placeholder': 'Número'}),
            'chave': forms.TextInput(attrs={'placeholder': 'Chave'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProcessoForm, self).__init__(*args, **kwargs)


class ProcessoParteForm(BootstrapForm):
    class Meta:
        model = Parte
        fields = ['id', 'parte', 'defensor_cadastro', 'defensoria_cadastro', 'defensor', 'defensoria']
        widgets = {
            'defensor_cadastro': forms.Select(attrs={'class': 'span12', 'data-form': 'select2'}),
            'defensoria_cadastro': forms.Select(attrs={'class': 'span12', 'data-form': 'select2'}),
            'defensor': forms.Select(attrs={'class': 'span12', 'data-form': 'select2'}),
            'defensoria': forms.Select(attrs={'class': 'span12', 'data-form': 'select2'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProcessoParteForm, self).__init__(*args, **kwargs)
        self.fields['defensor_cadastro'].queryset = Defensor.objects.filter(eh_defensor=True, ativo=True)
        self.fields['defensor'].queryset = Defensor.objects.filter(eh_defensor=True, ativo=True)


class BuscarAtendimentoForm(forms.Form):

    data_ini = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'ng-model': 'filtro.data_ini',
                'ng-change': 'validar()',
                'autocomplete': 'off',
                'class': 'span1 datepicker',
                'placeholder': 'Data Inicial',
                'data-date-format': 'dd/mm/yy'}))

    data_fim = forms.DateField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'ng-model': 'filtro.data_fim',
                'ng-change': 'validar()',
                'autocomplete': 'off',
                'class': 'span1 datepicker',
                'placeholder': 'Data Final',
                'data-date-format': 'dd/mm/yy'}))

    filtro = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'ng-model': 'filtro.filtro',
                'ng-change': 'validar()',
                'class': 'span3',
                'placeholder': 'Nº do atendimento, nome ou cpf do assistido...'}))

    comarca = forms.ChoiceField(
        required=False,
        widget=forms.Select(
            attrs={
                'ng-model': 'filtro.comarca',
                'ng-change': 'validar()',
                'class': 'span2'}))

    defensoria = forms.ChoiceField(
        required=False,
        widget=forms.Select(
            attrs={
                'ng-model': 'filtro.defensoria',
                'ng-change': 'validar()',
                'class': 'span2'}))

    defensor = forms.ChoiceField(
        required=False,
        widget=forms.Select(
            attrs={
                'ng-model': 'filtro.defensor',
                'ng-change': 'validar()',
                'class': 'span2'}))

    def __init__(self, *args, **kwargs):
        super(BuscarAtendimentoForm, self).__init__(*args, **kwargs)

        self.fields['comarca'].choices = Comarca.objects.filter(ativo=True).order_by('nome').values_list('id', 'nome')
        self.fields['defensoria'].choices = Defensoria.objects.filter(ativo=True, nucleo=None).order_by('comarca__nome', 'numero').values_list('id', 'nome')  # noqa
        # Não colocar filtro 'eh_defensor' aqui, pois é possível buscar a partir das lotações dos servidores
        self.fields['defensor'].choices = Defensor.objects.filter(ativo=True).order_by('servidor__nome').values_list('id', 'servidor__nome')  # noqa

    def is_valid(self):

        if super(BuscarAtendimentoForm, self).is_valid():

            if (self.cleaned_data['data_ini']
                or self.cleaned_data['data_fim']
                or self.cleaned_data['comarca']
                or self.cleaned_data['defensoria']
                or self.cleaned_data['defensor']
                or self.cleaned_data['filtro']
                ):  # noqa
                return True

        return False


class CadastrarTransferenciaForm(forms.ModelForm):

    defensoria = forms.ModelChoiceField(
        queryset=Defensoria.objects.ativos(),
        required=True,
        widget=forms.Select()
    )

    defensor = forms.ModelChoiceField(
        queryset=Defensor.objects.filter(ativo=True, eh_defensor=True),
        required=True,
        widget=forms.Select()
    )

    class Meta:
        model = Aprisionamento
        fields = ['prisao', 'estabelecimento_penal', 'data_inicial', 'data_final', 'historico']

    def is_valid(self):
        if super(CadastrarTransferenciaForm, self).is_valid():
            prisoes = Aprisionamento.objects.filter(
                prisao__pessoa=self.cleaned_data['prisao'].pessoa,
                data_inicial__gte=self.cleaned_data['data_inicial'],
                ativo=True
            ).exclude(
                id=self.instance.id
            ).order_by('-data_inicial')[:1]

            if prisoes:
                self._errors['data_inicial'] = ErrorList([
                    'deve ser maior que %s' % prisoes[0].data_inicial.strftime('%d/%m/%Y')
                ])
            else:
                return True

        return False


class CadastrarDetracaoForm(forms.ModelForm):
    class Meta:
        model = Aprisionamento
        fields = ['prisao', 'estabelecimento_penal', 'data_inicial', 'data_final', 'historico']

    def is_valid(self):
        if super(CadastrarDetracaoForm, self).is_valid():

            q = Q(prisao__pessoa=self.cleaned_data['prisao'].pessoa)

            if self.cleaned_data['data_final']:
                q &= Q(data_inicial__lte=self.cleaned_data['data_final'])

            q &= (
                    Q(data_final__gte=self.cleaned_data['data_inicial']) |
                    Q(data_final=None)
                )

            q &= Q(ativo=True)

            prisoes = Aprisionamento.objects.filter(
                q
            ).exclude(
                id=self.instance.id
            ).order_by('-data_inicial').count()

            if prisoes:
                self._errors['data_inicial'] = ErrorList([
                    'Já existe um registro cadastro neste período'
                ])
            else:
                return True

        return False


class CadastrarFaltaForm(forms.ModelForm):
    class Meta:
        model = Falta
        fields = ['pessoa', 'estabelecimento_penal', 'data_fato', 'observacao', 'numero_pad', 'resultado']


class CadastrarRemissaoForm(forms.ModelForm):
    class Meta:
        model = Remissao
        fields = ['pessoa', 'data_inicial', 'data_final', 'tipo', 'para_progressao', 'dias_registro', 'dias_remissao']


class CadastrarInterrupcaoForm(forms.ModelForm):
    class Meta:
        model = Interrupcao
        fields = ['pessoa', 'data_inicial', 'data_final', 'observacao']

    def is_valid(self):

        if super(CadastrarInterrupcaoForm, self).is_valid():

            interrupcoes = Interrupcao.objects.filter(pessoa=self.cleaned_data['pessoa'], ativo=True)

            if self.instance:
                interrupcoes = interrupcoes.exclude(id=self.instance.id)

            data_inicial = self.cleaned_data['data_inicial']
            data_final = self.cleaned_data['data_final']

            if data_inicial > date.today():
                self._errors['data_inicial'] = ErrorList(['A data inicial não pode ser superior a hoje.'])

            if interrupcoes.filter((Q(data_inicial__lte=data_inicial) & Q(data_final__gte=data_inicial)) | Q(data_final=None)):  # noqa
                self._errors['data_inicial'] = ErrorList(['Já existem interrupções cadastradas neste período.'])

            if data_final:

                if data_final > date.today():
                    self._errors['data_final'] = ErrorList(['A data final não pode ser superior a hoje.'])

                if data_final < data_inicial:
                    self._errors['data_final'] = ErrorList(['A data final não pode ser inferior à data inicial.'])

                if interrupcoes.filter((Q(data_inicial__lte=data_final) & Q(data_final__gte=data_final)) | Q(data_final=None)):  # noqa
                    self._errors['data_final'] = ErrorList(['Já existem interrupções cadastradas neste período.'])

        return super(CadastrarInterrupcaoForm, self).is_valid()


class CadastrarMudancaRegimeForm(forms.ModelForm):
    class Meta:
        model = MudancaRegime
        fields = ['prisao', 'data_registro', 'data_base', 'tipo', 'regime', 'estabelecimento_penal', 'historico']

    def is_valid(self):
        if super(CadastrarMudancaRegimeForm, self).is_valid():

            prisao = self.cleaned_data['prisao']

            regime = MudancaRegime.objects.filter(
                prisao=prisao,
                ativo=True
            ).aggregate(
                Max('data_registro'),
                Max('data_base')
            )

            if regime['data_registro__max'] and regime['data_registro__max'] >= self.cleaned_data['data_registro']:
                self._errors['data_registro'] = ErrorList([
                    'deve ser maior que {0}'.format(regime['data_registro__max'].strftime('%d/%m/%Y'))
                ])

            if regime['data_base__max'] and regime['data_base__max'] >= self.cleaned_data['data_base']:
                self._errors['data_base'] = ErrorList([
                    'deve ser maior que {0}'.format(regime['data_base__max'].strftime('%d/%m/%Y'))
                ])

            if not prisao.regime_atual is None:

                if prisao.regime_atual >= self.cleaned_data['regime'] and self.cleaned_data['tipo'] == MudancaRegime.TIPO_PROGRESSAO:  # noqa
                    self._errors['regime'] = ErrorList([
                        'deve ser diferente que "{0}"'.format(Prisao.LISTA_REGIME[self.cleaned_data['regime']][1])
                    ])

                if prisao.regime_atual < self.cleaned_data['regime'] and self.cleaned_data['tipo'] == MudancaRegime.TIPO_REGRESSAO:  # noqa
                    self._errors['regime'] = ErrorList([
                        'deve ser diferente que "{0}"'.format(Prisao.LISTA_REGIME[self.cleaned_data['regime']][1])
                    ])

            if not self._errors:
                return True

        return False


class LiquidarPenaForm(forms.ModelForm):
    class Meta:
        model = Prisao
        fields = ['data_liquidacao', ]


class BaixarPrisaoForm(forms.ModelForm):
    class Meta:
        model = Prisao
        fields = ['data_baixa', 'motivo_baixa', ]
        # ajustes css
        widgets = {
            'data_baixa': forms.TextInput(attrs={
                'class': 'datepicker',
                'data-date-format': 'dd/mm/yyyy',
                'data-mask': '99/99/9999',
            }),
            'motivo_baixa': forms.Select(attrs={
                'class': 'span12'
            }),
        }

    def __init__(self, *args, **kwargs):

        super(BaixarPrisaoForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].required = True
            self.fields[field].widget.attrs['required'] = True
