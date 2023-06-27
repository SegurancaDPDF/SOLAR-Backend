# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from datetime import datetime

# Bibliotecas de terceiros
from django import forms
from django.db.models import Q, Max
from django_currentuser.middleware import get_current_user
from constance import config
from contrib.forms import RequiredFiedlsMixin
from contrib.models import Defensoria
from core.forms import NovoEventoForm, EditarEventoForm
from core.models import (
    Classe as CoreClasse,
    Documento as CoreDocumento,
    Evento as CoreEvento,
    TipoEvento as CoreTipoEvento
)
from assistido.models import PessoaAssistida
from atendimento.atendimento.forms import AgendarNucleoDiligenciaForm
from defensor.models import Atuacao, Defensor
from indeferimento.models import Indeferimento
from procapi_client.services import APIProcesso
from processo.processo.models import Processo as ProcessoJudicial


class BuscarIndeferimentoForm(forms.Form):
    filtro = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'span6',
                'placeholder': 'Buscar pelo nº do processo, nome ou CPF/CNPJ do assistido...'}))
    resultado = forms.ChoiceField(
        choices=((None, '<Todos resultados>'),) + Indeferimento.LISTA_RESULTADO,
        required=False,
        widget=forms.Select(
            attrs={'class': 'span2'}))
    tipo_baixa = forms.ChoiceField(
        choices=((None, '<Todos tipos de baixa>'),) + Indeferimento.LISTA_BAIXA,
        required=False,
        widget=forms.Select(
            attrs={'class': 'span2'}))


class NovaSolicitacaoForm(forms.Form):
    pessoa = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class': 'span12'}),
        queryset=PessoaAssistida.objects.none()
    )
    classe = forms.ModelChoiceField(
        label='Motivo',
        widget=forms.Select(attrs={'class': 'span12'}),
        queryset=CoreClasse.objects.ativos()
    )

    atuacao_cadastro = forms.ModelChoiceField(
        label='Defensor/Defensoria do Cadastro',
        widget=forms.Select(attrs={'class': 'span12'}),
        queryset=Atuacao.objects.vigentes().filter(defensor__eh_defensor=True),
        required=False
    )

    medida_pretendida = forms.CharField(
        widget=forms.HiddenInput,
        required=False,
    )
    justificativa = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'span12', 'cols': 10, 'rows': 4}),
    )
    setor_encaminhado = forms.ModelChoiceField(
        label='Encaminhar para',
        widget=forms.Select(attrs={'class': 'span12'}),
        queryset=Defensoria.objects.ativos()
    )

    atendimento = None

    def __init__(self, *args, **kwargs):

        invisivel = kwargs.pop('invisivel', False)
        self.atendimento = kwargs.pop('atendimento', None)

        super(NovaSolicitacaoForm, self).__init__(*args, **kwargs)

        # se o formulário for exibido, obriga informar a atuação
        self.fields['atuacao_cadastro'].required = not invisivel

        for key in self.fields:

            self.fields[key].widget.attrs['required'] = self.fields[key].required

            # deixar invisivel afeta os campos de multipla escolha
            # if invisivel:
            #     self.fields[key].widget = forms.HiddenInput()

        if self.atendimento:
            self.fields['pessoa'].queryset = PessoaAssistida.objects.filter(
                id__in=self.atendimento.requerentes.values('pessoa_id')
            )

        # Mostra apenas as defensorias onde a pessoa logada tem atuação
        user = get_current_user()

        user_atuacoes_vigentes = user.servidor.defensor.atuacoes_vigentes().values_list('defensoria_id', flat=True)

        if user_atuacoes_vigentes:
            query_atuacoes = Atuacao.objects.vigentes_por_defensoria(defensorias=user_atuacoes_vigentes)

        else:
            # TODO: tratar para não mostrar nenhuma atuação quando o usuário logado não tiver atuações
            query_atuacoes = Atuacao.objects.none()
            # self.fields['atuacao_cadastro'].widget.attrs['disable'] = 'True'
            # self.fields['atuacao_cadastro'].queryset = self.fields['atuacao_cadastro'].queryset.filter(query_atuacoes)

        self.fields['atuacao_cadastro'].queryset = query_atuacoes


class NovoImpedimentoForm(NovaSolicitacaoForm):

    def __init__(self, *args, **kwargs):

        super(NovoImpedimentoForm, self).__init__(*args, **kwargs)
        self.fields['classe'].queryset = self.fields['classe'].queryset.tipo_impedimento()
        self.fields['setor_encaminhado'].queryset = self.fields['setor_encaminhado'].queryset.filter(
            nucleo__indeferimento_pode_receber_impedimento=True
        )


class NovaSuspeicaoForm(NovaSolicitacaoForm):

    def __init__(self, *args, **kwargs):

        super(NovaSuspeicaoForm, self).__init__(*args, **kwargs)
        self.fields['classe'].queryset = self.fields['classe'].queryset.tipo_suspeicao()
        self.fields['setor_encaminhado'].queryset = self.fields['setor_encaminhado'].queryset.filter(
            nucleo__indeferimento_pode_receber_suspeicao=True
        )


class NovaNegacaoProcedimentoForm(NovaSolicitacaoForm):
    """Formulário para Denegação de Procedimento"""

    setores_notificados = forms.ModelMultipleChoiceField(
        label='Notificar',
        widget=forms.CheckboxSelectMultiple(),
        queryset=Defensoria.objects.ativos(),
        required=False
    )

    def __init__(self, *args, **kwargs):

        super(NovaNegacaoProcedimentoForm, self).__init__(*args, **kwargs)
        self.fields['classe'].queryset = self.fields['classe'].queryset.tipo_negacao_procedimento()
        self.fields['setor_encaminhado'].queryset = self.fields['setor_encaminhado'].queryset.filter(
            nucleo__indeferimento_pode_receber_negacao=True
        )
        self.fields['setores_notificados'].queryset = self.get_setores_notificaveis()

    def get_setores_notificaveis(self):
        '''
        Gera lista com setores que podem ser notificados para escolha no cadastro
        '''

        # recupera maior grau entre os processo vinculados
        maior_grau = self.atendimento.processo_partes.aggregate(maior=Max('processo__grau')).get('maior')

        # recupera processos de menor grau vinculados ao atendimento
        processos_1G = self.atendimento.processo_partes.filter(
            defensoria__ativo=True,
            defensoria__grau=Defensoria.GRAU_1,
            defensoria__pode_vincular_processo_judicial=True,
            processo__grau__lt=maior_grau,
            processo__tipo__in=[ProcessoJudicial.TIPO_FISICO, ProcessoJudicial.TIPO_EPROC]
        )

        # se existem processos de menor grau vinculados ao atendimento, retorna lista de defensorias vinculadas
        if processos_1G.exists():

            return Defensoria.objects.filter(
                id__in=processos_1G.values('defensoria'),
                pode_vincular_processo_judicial=True
            )

        elif config.ATIVAR_PROCAPI:  # senão, faz a verificação via PROCAPI (apenas 2º grau)

            for processo_2G in self.atendimento.processos.filter(grau=ProcessoJudicial.GRAU_2):

                # consulta processo de 2º grau no PROCAPI
                api = APIProcesso(numero=processo_2G.numero_procapi)
                sucesso, resposta = api.consultar()

                if sucesso:  # se consulta ao PROCAPI foi bem-sucedida

                    # consulta primeiro evento do processo de 2º Grau
                    sucesso, resposta_eventos = api.consultar_eventos()
                    data_base = resposta_eventos['results'][0]['data_protocolo']
                    data_base = datetime.strptime(data_base, '%Y-%m-%dT%H:%M:%S')

                    for vinculado in resposta['vinculados']:  # passa por todos processos vinculados

                        if vinculado['vinculo'] == 'DP':  # verifica se é o processo originário

                            api = APIProcesso(numero=vinculado['numero'])  # consulta processo originário no PROCAPI

                            pagina = 1
                            eventos = []

                            # consulta eventos do processo originário no PROCAPI
                            while pagina > 0:
                                sucesso, resposta = api.consultar_eventos(pagina=pagina)
                                eventos += resposta['results']
                                pagina = pagina + 1 if resposta['next'] else 0

                            # inverte ordem dos eventos (mais novos primeiro)
                            eventos.reverse()

                            # passa por todos os eventos do processo originário
                            for evento in eventos:

                                data_evento = datetime.strptime(evento['data_protocolo'], '%Y-%m-%dT%H:%M:%S')

                                # verifica se evento foi protocolado antes da petição inicial do processo de 2º grau
                                if data_evento.date() <= data_base.date():

                                    # Procura por defensor correspondente ao usuário que peticionou o processo
                                    defensor = Defensor.objects.filter(
                                        usuario_eproc__icontains=evento['usuario']
                                    ).first()

                                    # Se encontrar defensor, procura atuações no dia do peticionamento
                                    if defensor:

                                        atuacoes = Atuacao.objects.filter(
                                            Q(defensor=defensor) &
                                            Q(data_inicial__lte=evento['data_protocolo']) &
                                            (
                                                Q(data_final__gte=evento['data_protocolo']) |
                                                Q(data_final=None)
                                            )
                                        )

                                        # Retorna lista de defensorias vinculadas às atuações do defensor
                                        return Defensoria.objects.filter(
                                            id__in=atuacoes.values('defensoria'),
                                            pode_vincular_processo_judicial=True
                                        )

        # Por padrão, retorna lista de todas defensorias para escolha
        return Defensoria.objects.ativos().filter(
            pode_vincular_processo_judicial=True
        )


class NovaNegacaoForm(NovaSolicitacaoForm):

    def __init__(self, *args, **kwargs):

        super(NovaNegacaoForm, self).__init__(*args, **kwargs)

        self.fields['setor_encaminhado'].queryset = self.fields['setor_encaminhado'].queryset.filter(
            nucleo__indeferimento_pode_receber_negacao=True
        )

        q = Q()
        q |= Q(tipo__in=[CoreClasse.TIPO_NEGACAO, CoreClasse.TIPO_NEGACAO_HIPOSSUFICIENCIA])

        self.fields['classe'].queryset = self.fields['classe'].queryset.filter(
            q
        ).order_by('-tipo', 'nome')


class NovoRecursoForm(forms.ModelForm):

    setor_encaminhado = forms.ModelChoiceField(
        label='Encaminhar para',
        widget=forms.Select(attrs={
            'class': 'span12',
            'required': True
        }),
        required=True,
        queryset=Defensoria.objects.filter(
            nucleo__indeferimento_pode_receber_negacao=True,
            ativo=True
        ).only('id', 'nome')
    )

    class Meta:
        model = Indeferimento
        fields = ['medida_pretendida', 'justificativa', 'setor_encaminhado']

    def __init__(self, *args, **kwargs):
        super(NovoRecursoForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = True


class GenericEventoIndeferimentoMixin(object):

    def __init__(self, *args, **kwargs):

        super(GenericEventoIndeferimentoMixin, self).__init__(*args, **kwargs)

        # ajustes css
        self.fields['tipo'].widget.attrs['class'] = 'span12'
        self.fields['historico'].widget.attrs['class'] = 'span12'

        if 'setor_encaminhado' in self.fields:
            # ajustes css
            self.fields['setor_encaminhado'].widget.attrs['class'] = 'span12'
            # marca setor encaminhado como obrigatorio
            self.fields['setor_encaminhado'].required = True
            self.fields['setor_encaminhado'].widget.attrs['required'] = True
            # filtros
            self.fields['setor_encaminhado'].queryset = self.fields['setor_encaminhado'].queryset.filter(
                nucleo__indeferimento=True
            )
        # marca historico como obrigatorio
        self.fields['historico'].required = True
        self.fields['historico'].widget.attrs['required'] = True

        # # se existe processo mostra setor responsavel pela baixa e outros setores (ex: corregedoria)
        # if kwargs.get('instance') and hasattr(kwargs.get('instance'), 'processo'):

        #     processo = kwargs.get('instance').processo

        #     q = Q(nucleo__indeferimento_pode_registrar_baixa=False)

        #     if processo.indeferimento.defensoria:
        #         q |= Q(comarca=processo.indeferimento.defensoria.comarca.diretoria)
        #     else:
        #         q |= Q(comarca=processo.indeferimento.atendimento.defensoria.comarca.diretoria)

        #     self.fields['setor_encaminhado'].queryset = self.fields['setor_encaminhado'].queryset.filter(q)


class EditarEventoIndeferimentoForm(GenericEventoIndeferimentoMixin, EditarEventoForm):

    class Meta:
        model = CoreEvento
        fields = ['data_referencia', 'setor_criacao', 'historico', 'tipo', 'setor_encaminhado']
        widgets = EditarEventoForm._meta.widgets

    def __init__(self, *args, **kwargs):

        super(EditarEventoIndeferimentoForm, self).__init__(*args, **kwargs)

        # filtra tipos de eventos válidos
        tipos = [CoreTipoEvento.TIPO_ENCAMINHAMENTO, CoreTipoEvento.TIPO_ANOTACAO]

        if kwargs.get('instance'):
            # se evento decisao, mostra apenas setor responsavel pela baixa
            if kwargs.get('instance').tipo.tipo == CoreTipoEvento.TIPO_DECISAO:
                self.fields['setor_encaminhado'].required = False
                self.fields['setor_encaminhado'].widget.attrs['required'] = False
                self.fields['setor_encaminhado'].empty_label = '(Não encaminhar)'
                self.fields['setor_encaminhado'].queryset = self.fields['setor_encaminhado'].queryset.filter(
                    nucleo__indeferimento_pode_registrar_baixa=True
                )

            # mostra eventos do tipo decisão se setor criação estiver habilitado
            if kwargs.get('instance').setor_criacao.nucleo.indeferimento_pode_registrar_decisao:
                tipos.append(CoreTipoEvento.TIPO_DECISAO)

        self.fields['tipo'].queryset = self.fields['tipo'].queryset.ativos().filter(tipo__in=tipos)

        # campos somente leitura
        self.fields['data_referencia'].widget.attrs['readonly'] = True
        self.fields['setor_criacao'].widget.attrs['readonly'] = True


class NovoEventoIndeferimentoForm(GenericEventoIndeferimentoMixin, NovoEventoForm):
    def __init__(self, *args, **kwargs):

        tipo = kwargs.pop('tipo')
        super(NovoEventoIndeferimentoForm, self).__init__(*args, **kwargs)

        # filtra tipos de eventos
        self.fields['tipo'].queryset = self.fields['tipo'].queryset.ativos().filter(tipo=tipo)

        # se evento decisao, mostra apenas setor responsavel pela baixa
        if tipo == CoreTipoEvento.TIPO_DECISAO:

            # decisão precisa incluir documentos, pois na página de documentos possui as opções de decisão
            self.fields['incluir_documentos'].widget = forms.HiddenInput()

            self.fields['setor_encaminhado'].required = False
            self.fields['setor_encaminhado'].widget.attrs['required'] = False
            self.fields['setor_encaminhado'].empty_label = '(Não encaminhar)'
            self.fields['setor_encaminhado'].queryset = self.fields['setor_encaminhado'].queryset.filter(
                nucleo__indeferimento_pode_registrar_baixa=True
            )


class AgendarDiligenciaIndeferimentoForm(RequiredFiedlsMixin, AgendarNucleoDiligenciaForm):
    required_fields = ['defensoria', 'qualificacao', 'data_agendamento']

    documento = forms.ModelChoiceField(
        queryset=CoreDocumento.objects.ativos().tipo_ged_assinados(),
        required=True,
        widget=forms.Select(attrs={'class': 'span12'})
    )

    anexos = forms.ModelMultipleChoiceField(
        queryset=CoreDocumento.objects.ativos().anexos(),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )

    def __init__(self, *args, **kwargs):

        processo = kwargs.pop('processo', None)

        super(AgendarDiligenciaIndeferimentoForm, self).__init__(*args, **kwargs)

        # filtra tipos de eventos
        if processo:
            self.fields['documento'].queryset = self.fields['documento'].queryset.filter(processo=processo)
            self.fields['anexos'].queryset = self.fields['anexos'].queryset.filter(processo=processo)
