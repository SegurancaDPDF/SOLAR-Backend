# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import calendar
import json as simplejson
import logging
import time as time_sleep
from datetime import date, datetime, time, timedelta
# Bibliotecas de terceiros
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Sum, Case, When, Value, IntegerField, F, Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, View
from constance import config
# Solar
from assistido.models import PessoaAssistida
from atendimento.atendimento.forms import BuscarAtendimentoConflitoForm
from atendimento.atendimento.models import (
    Acesso,
    Atendimento,
    FormaAtendimento,
    Defensor as AtendimentoDefensor,
    GrupoDeDefensoriasParaAgendamento,
    Pessoa as AtendimentoPessoa,
    Procedimento,
    Qualificacao
)
from atendimento.atendimento.services import AtendimentoService
from contrib.models import Comarca, Defensoria, Util
from contrib.services import envia_sms
from contrib.services import envia_email
from defensor.models import Atuacao
from evento.models import Agenda, Evento
from indeferimento.models import Indeferimento
from luna_chatbot_client.tasks import chatbot_notificar_requerente_agendamento
from relatorios.models import Local, Relatorio

logger = logging.getLogger(__name__)


class AgendarView(View):
    """Estrutura comum todos os tipos de agendamento"""

    atuacao_id = None
    categoria_de_agenda = None
    prazo = False
    prioridade = AtendimentoDefensor.PRIORIDADE_0
    anotacao = None
    justificativa = None
    data_agendamento = None
    forma_atendimento = None
    ligacao = None
    atendimento = None

    oficio = False
    detalhes = ''

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        # Obtém dados inseridos na url
        self.atendimento_numero = self.kwargs.get('atendimento_numero')

        # Se atuação de plantão, obtém dados da sessão
        if request.session.get('atuacao_de_plantao_id'):
            self.atuacao_id = request.session.pop('atuacao_de_plantao_id')
            self.categoria_de_agenda = 1
            self.data_agendamento = datetime.combine(date.today(), time.min)
        # Senão, obtém dados da requisição
        else:

            data = request.POST

            self.atuacao_id = data.get('atuacao')
            self.categoria_de_agenda = data.get('categoria_de_agenda', 1)
            self.prazo = (data.get('prazo') in ['1', 'on', 'true'])
            self.prioridade = data.get('prioridade', AtendimentoDefensor.PRIORIDADE_0)
            self.anotacao = data.get('anotacoes', '')
            self.justificativa = request.session.get('justificativa')

            if data.get('horario'):
                self.data_agendamento = datetime.strptime(data.get('horario'), '%Y-%m-%dT%H:%M:%S')

            # Se forma de atendimento foi informada, recupera informações
            if data.get('forma_atendimento'):
                forma_atendimento = data.get('forma_atendimento')
                # Obtém lista de formas de atendimento disponíveis para a recepção
                formas_atendimento = FormaAtendimento.objects.vigentes().filter(aparece_recepcao=True)
                # Se é dígito, procura pelo id
                if forma_atendimento.isnumeric():
                    self.forma_atendimento = formas_atendimento.filter(id=forma_atendimento).first()
                # Se texto, procura pelo tipo (presencial ou não)
                elif forma_atendimento == 'P':
                    self.forma_atendimento = formas_atendimento.filter(presencial=True).first()
                elif forma_atendimento == 'R':
                    self.forma_atendimento = formas_atendimento.filter(presencial=False).first()

            self.oficio = (data.get('oficio') in ['1', 'on', 'true'])
            self.detalhes = data.get('detalhes', '')

        # Verifica se horário escolhido ainda está disponível
        disponivel = self.verificar_disponibilidade_horario()

        # Se horário não está mais disponível, guarda dados na sessão e retorna para página anterior
        if not disponivel:

            request.session['agendamento_atuacao'] = self.atuacao_id
            request.session['agendamento_categoria_de_agenda'] = int(self.categoria_de_agenda)
            request.session['agendamento_prazo'] = self.prazo
            request.session['agendamento_prioridade'] = self.prioridade
            request.session['agendamento_anotacao'] = self.anotacao
            request.session['agendamento_data'] = self.data_agendamento

            messages.error(request, u'O horário escolhido não está mais disponível, por favor, tente novamente!')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # Se tem ligação na sessão, carrega dados
        if request.session.get('ligacao_id'):
            self.ligacao = Atendimento.objects.get(id=request.session.get('ligacao_id'))

        # Se número do atendimento foi informado, carrega dados
        if self.atendimento_numero:
            self.atendimento = AtendimentoDefensor.objects.get(numero=self.atendimento_numero)

        # Retorna resultado do método agendar, implementado na view para cada tipo de agendamento
        return self.agendar(request)

    def agendar(self, request):
        pass

    def verificar_disponibilidade_horario(self):
        '''
        Verifica se horário escolhido ainda está disponível
        '''

        # Verificar quantos agendamentos foram feitos no mesmo horário
        # Comparar total com limite de atendimentos simultâneos
        # Se já atingiu limite, horário não está mais disponível

        # TODO: Verificar se agenda permite agendamento extra-pauta
        # TODO: Verificar se há algum evento de bloqueio para o dia antes de liberar o agendamento
        # TODO: Verificar se há algum evento de desbloqueio para liberar o agendamento retroativo

        disponivel = False

        # Se não é uma data/hora válida, horário indisponível
        if not isinstance(self.data_agendamento, datetime):

            disponivel = False

        # Se agendamento é na extra-pauta, horário disponível
        elif self.data_agendamento.hour == 0 and self.data_agendamento.minute == 0:

            disponivel = True

        # Senão, verifica se horário da pauta ainda está disponível
        else:

            # Carrega dados da atuação
            atuacao = Atuacao.objects.get(id=self.atuacao_id)
            defensor = atuacao.titular if atuacao.tipo == Atuacao.TIPO_SUBSTITUICAO else atuacao.defensor

            # Carrega dados da agenda mais recente vigente no dia do agendamento
            agenda = Agenda.objects.filter(
                atuacao=self.atuacao_id,
                ativo=True,
                data_ini__lte=self.data_agendamento.date(),
                data_fim__gte=self.data_agendamento.date()
            ).order_by('-data_cadastro').first()

            if agenda:

                # Verifica quantos agendamentos existem para o mesmo(a) defensor/defensoria/agenda/horário
                agendamentos = AtendimentoDefensor.objects.filter(
                    Q(defensor=defensor) &
                    Q(defensoria=atuacao.defensoria) &
                    Q(agenda=self.categoria_de_agenda) &
                    Q(data_agendamento=self.data_agendamento) &
                    Q(remarcado=None) &
                    Q(ativo=True) &
                    (
                        Q(data_atendimento__isnull=True) |
                        Q(data_atendimento__date=self.data_agendamento.date())

                    )
                ).count()

                # Se total de agendamentos não atingiu o limite de agendamentos simultâneos para o mesmo horário, libera
                if agendamentos < agenda.simultaneos:
                    disponivel = True

        return disponivel

    def criar_procedimento_129(self, novo_agendamento, tipo, atendente):
        procedimento, msg = Procedimento.objects.get_or_create(
            ligacao=self.ligacao,
            agendamento=novo_agendamento,
            tipo=tipo,
            atendente=atendente,
            attprocedimento=novo_agendamento)

        procedimento.save()

        messages.success(self.request, u'Procedimento cadastrado: {}'.format(procedimento.get_tipo_display()))


class AgendarInicialView(AgendarView):
    """Utilizado para marcar um agendamento Inicial"""
    def agendar(self, request):

        pessoa = None
        qualificacao = None

        # Se tem ligação, obtém pessoa vinculada
        if self.ligacao:
            if self.ligacao.requerente:
                request.session['pessoa_id'] = self.ligacao.requerente.pessoa_id
            else:
                return redirect('precadastro_index')
        elif not request.session.get('pessoa_id'):
            # Senão, redireciona para página inicial
            return redirect('index')

        if not request.session.get('qualificacao_id'):
            messages.error(request, u'Erro: Agendamento não possui uma qualificação.')
            return redirect('qualificacao_index')

        # Carrega dados que estão armazenados na sessão
        pessoa = PessoaAssistida.objects.get(id=request.session.get('pessoa_id'))
        qualificacao = Qualificacao.objects.get(id=request.session.pop('qualificacao_id'))

        # Cria um novo atendimento
        atendimento = AtendimentoDefensor.objects.create(
            tipo=Atendimento.TIPO_INICIAL,
            origem=self.ligacao,
            qualificacao=qualificacao,
            prazo=self.prazo,
            prioridade=self.prioridade,
            agenda_id=self.categoria_de_agenda,
            historico_recepcao=self.anotacao,
            cadastrado_por=request.user.servidor
        )

        # Deixa atendimento público por padrão
        Acesso.conceder_publico(atendimento, None)

        # Se agendamento feito a partir de um processo, transfere relacionamentos do processo para o atendimento
        if request.session.get('atendimento_processo_numero'):

            atendimento_processo = AtendimentoDefensor.objects.get(
                numero=request.session.pop('atendimento_processo_numero')
            )

            service = AtendimentoService(atendimento_processo)
            service.transferir_relacionamentos(
                atendimento_destino=atendimento,
                transferir_filhos=False,
                transferir_documentos=False
            )

            # Vincula processo ao atendimento inicial
            atendimento_processo.inicial = atendimento
            atendimento_processo.save()

        else:

            # Define a pessoal como requerente principal do atendimento inicial
            atendimento.set_requerente(pessoa.id)

            if self.ligacao and self.ligacao.at_defensor:

                # Se possui outros requerentes, também adiciona ao atendimento inicial
                for requerente in self.ligacao.at_defensor.requerentes_secundarios:
                    atendimento.add_requerente(requerente.pessoa_id)

                # transfere relacionamentos da ligação para o atendimento
                service = AtendimentoService(self.ligacao.at_defensor)
                service.transferir_relacionamentos(
                    atendimento_destino=atendimento,
                    transferir_pessoas=False,
                    transferir_filhos=False,
                    transferir_documentos=False
                )

        # Atualiza atendimento, preenchendo dados do agendamento
        atendimento.marcar(
            atuacao_id=self.atuacao_id,
            data_agendamento=self.data_agendamento,
            agendado_por=request.user.servidor,
            categoria_de_agenda=self.categoria_de_agenda,
            forma_atendimento=self.forma_atendimento,
            justificativa=self.justificativa,
            anotacao=self.anotacao,
            # DPE-AM
            oficio=self.oficio,
            detalhes=self.detalhes
        )

        # Se processo informado, vincula ao atendimento
        if request.session.get('processo_id'):
            from processo.processo.models import Processo, Parte as ProcessoParte
            processo = Processo.objects.get(id=request.session.pop('processo_id'))
            ProcessoParte.objects.create(
                processo=processo,
                atendimento=atendimento,
                defensor_cadastro=atendimento.substituto if atendimento.substituto else atendimento.defensor,
                defensoria_cadastro=atendimento.defensoria,
                defensoria=atendimento.defensoria,
                # TODO: Identificar parte (polo) corretamente
                parte=ProcessoParte.TIPO_REU
            )

        # Notifica assistido via chatbot Luna
        chatbot_notificar_requerente_agendamento.apply_async(
            kwargs={'numero': atendimento.numero, 'remarcado': False},
            queue='sobdemanda'
        )

        # Notifica assistido via SMS
        if (config.USAR_SMS and config.SERVICO_SMS_DISPONIVEL):
            envia_sms_agendamento(request, atendimento, self.data_agendamento, config.MENSAGEM_SMS_AGENDAMENTO_INICIAL)

        # Notifica assistido via E-mail SMTP
        if (config.USAR_EMAIL):
            envia_email_agendar(request, atendimento, self.data_agendamento, config.MENSAGEM_EMAIL_AGENDAMENTO_INICIAL)

        # Se agendado pelo 129, registra procedimento e redireciona página do 129
        if self.ligacao:
            atendente = atendimento.cadastrado_por.usuario
            self.criar_procedimento_129(atendimento, Procedimento.TIPO_AGENDAMENTO_INICIAL, atendente)

            # TODO: Verificar melhor maneira de identificar que é originário do Painel CRC
            if hasattr(self.ligacao, 'defensor'):
                request.session['pessoa_id'] = None
                request.session['ligacao_id'] = None
                return redirect('recepcao_atendimento', atendimento.numero)
            else:
                return redirect('precadastro_continuar', self.ligacao.numero)

        # Se agendamento de plantão, redireciona para Ficha do Atendimento
        if atendimento.defensoria.nucleo and atendimento.defensoria.nucleo.plantao:
            return redirect('atendimento_atender', atendimento.numero)
        # Senão, se foi passada uma url, redireciona
        elif request.POST.get('next'):
            return redirect(request.POST.get('next'))
        # Senão, redireciona para Detalhes do Atendimento
        else:
            return redirect('recepcao_atendimento', atendimento.numero)


class AgendarRetornoView(AgendarView):
    """Utilizado para marcar um agendamento de retorno"""
    def agendar(self, request):
        inicial = self.atendimento.at_inicial
        atuacao = Atuacao.objects.get(id=self.atuacao_id)

        # Se a defensoria escolhida é diferente da do atendimento originial, então é um encaminhamento
        if atuacao.defensoria != self.atendimento.defensoria:
            tipo = Atendimento.TIPO_ENCAMINHAMENTO
        else:
            tipo = Atendimento.TIPO_RETORNO

        if config.CONVERTER_PRIMEIRO_ENCAMINHAMENTO_EM_INICIAL and tipo == Atendimento.TIPO_ENCAMINHAMENTO:
            if not atuacao.defensoria.nucleo or not atuacao.defensoria.nucleo.multidisciplinar:
                possui_atendimento_inicial = AtendimentoDefensor.objects.filter(
                    Q(tipo=Atendimento.TIPO_INICIAL) &
                    Q(remarcado=None) &
                    Q(ativo=True) &
                    (
                        Q(id=self.atendimento.at_inicial.id) |
                        Q(inicial_id=self.atendimento.at_inicial.id)
                    ) &
                    ~Q(defensoria__nucleo__multidisciplinar=True)
                )

                if not possui_atendimento_inicial:
                    tipo = Atendimento.TIPO_INICIAL

        # Cria um agendamento de retorno a partir do atendimento inicial
        retorno = inicial.marcar_retorno(
            origem=self.ligacao,
            atuacao_id=self.atuacao_id,
            data_agendamento=self.data_agendamento,
            agendado_por=request.user.servidor,
            categoria_de_agenda=self.categoria_de_agenda,
            forma_atendimento=self.forma_atendimento,
            prazo=self.prazo,
            prioridade=self.prioridade,
            anotacao=self.anotacao,
            tipo=tipo
        )

        # Notifica assistido via chatbot Luna
        chatbot_notificar_requerente_agendamento.apply_async(
            kwargs={'numero': retorno.numero, 'remarcado': False},
            queue='sobdemanda'
        )

        # Notifica assistido via SMS
        if (config.USAR_SMS and config.SERVICO_SMS_DISPONIVEL):
            envia_sms_agendamento(request, retorno, self.data_agendamento, config.MENSAGEM_SMS_AGENDAMENTO_RETORNO)

        # Notifica assistido via E-mail SMTP
        if (config.USAR_EMAIL):
            envia_email_agendar(request, retorno, self.data_agendamento, config.MENSAGEM_EMAIL_AGENDAMENTO_RETORNO)

        # Se agendado pelo 129, registra procedimento e redireciona página do 129
        if self.ligacao:
            atendente = retorno.cadastrado_por.usuario
            self.criar_procedimento_129(retorno, Procedimento.TIPO_AGENDAMENTO_RETORNO, atendente)

            # TODO: Verificar melhor maneira de identificar que é originário do Painel CRC
            if hasattr(self.ligacao, 'defensor'):
                request.session['pessoa_id'] = None
                request.session['ligacao_id'] = None
                return redirect('recepcao_atendimento', retorno.numero)
            else:
                return redirect('precadastro_continuar', self.ligacao.numero)

        messages.success(request, u'Retorno marcado com sucesso!')

        if request.POST.get('indeferimento_uuid') and request.POST.get('indeferimento_nucleo_id'):

            if tipo == Atendimento.TIPO_ENCAMINHAMENTO:
                tipo_baixa_indeferimento = Indeferimento.BAIXA_ENCAMINHADO
            else:
                tipo_baixa_indeferimento = Indeferimento.BAIXA_REMARCADO

            return redirect(
                'indeferimento:baixar_solicitacao',
                nucleo_id=request.POST.get('indeferimento_nucleo_id'),
                processo_uuid=request.POST.get('indeferimento_uuid'),
                tipo=tipo_baixa_indeferimento)

        elif retorno.defensoria.nucleo and retorno.defensoria.nucleo.acordo:
            return redirect('agendamento_nucleo_confirmar', retorno.numero)
        elif retorno.defensoria.nucleo and retorno.defensoria.nucleo.plantao:
            return redirect('atendimento_atender', retorno.numero)
        elif request.POST.get('next'):
            return redirect(request.POST.get('next'))
        else:
            return redirect('recepcao_atendimento', retorno.numero)


class AgendarRemarcarView(AgendarView):
    """Utilizado para remarcar o agendamento"""
    def agendar(self, request):

        # Se agendamento que será remarcado é um apoio, usa a mesma origem para o novo agendamento
        if self.atendimento.tipo == AtendimentoDefensor.TIPO_NUCLEO:
            origem = self.atendimento.origem
        else:
            origem = self.ligacao

        # Remarcar agendamento, criando um novo agendamento a partir dele
        destino = self.atendimento.remarcar(
            origem=origem,
            atuacao_id=self.atuacao_id,
            data_agendamento=self.data_agendamento,
            agendado_por=request.user.servidor,
            justificativa=self.justificativa,
            categoria_de_agenda=self.categoria_de_agenda,
            forma_atendimento=self.forma_atendimento,
            prazo=self.prazo,
            prioridade=self.prioridade,
            anotacao=self.anotacao,
            # DPE-AM
            oficio=self.oficio,
            detalhes=self.detalhes
        )

        # Notifica assistido via chatbot Luna
        chatbot_notificar_requerente_agendamento.apply_async(
            kwargs={'numero': destino.numero, 'remarcado': True},
            queue='sobdemanda'
        )

        # Notifica assistido via SMS
        if (config.USAR_SMS and config.SERVICO_SMS_DISPONIVEL):
            envia_sms_agendamento(request, destino, self.data_agendamento, config.MENSAGEM_SMS_AGENDAMENTO_REMARCACAO)

        # Notifica assistido via E-mail SMTP
        if (config.USAR_EMAIL):
            envia_email_agendar(request, destino, self.data_agendamento, config.MENSAGEM_EMAIL_AGENDAMENTO_REMARCACAO)

        # Se agendado pelo 129, registra procedimento e redireciona página do 129
        if self.ligacao:
            atendente = destino.cadastrado_por.usuario
            self.criar_procedimento_129(destino, Procedimento.TIPO_REAGENDAMENTO, atendente)

            # TODO: Verificar melhor maneira de identificar que é originário do Painel CRC
            if hasattr(self.ligacao, 'defensor'):
                request.session['pessoa_id'] = None
                request.session['ligacao_id'] = None
                return redirect('recepcao_atendimento', destino.numero)
            else:
                return redirect('precadastro_continuar', self.ligacao.numero)

        # Se defensoria de plantão, redireciona para Ficha de Atendimento
        if destino.defensoria.nucleo and destino.defensoria.nucleo.plantao:
            return redirect('atendimento_atender', destino.numero)
        # Senão, redireciona para Detalhes do Atendimento
        else:
            return redirect('recepcao_atendimento', destino.numero)


class AgendarNucleoView(AgendarView):
    """Utilizado para agendar em núcleo especializado"""
    def agendar(self, request):

        self.atendimento.marcar_nucleo(
            self.data_agendamento,
            self.request.user.servidor,
            self.categoria_de_agenda,
            self.anotacao,
            oficio=self.oficio,
            detalhes=self.detalhes
        )
        return redirect('agendamento_nucleo_confirmar', self.atendimento.numero)


@login_required
def agendar_plantao(request, atendimento_numero=None, remarcar=False):

    nucleo = request.session['nucleo']
    defensor = request.user.servidor.defensor

    atuacao = Atuacao.objects.parcialmente_vigentes().filter(
        defensor=defensor,
        defensoria__nucleo=nucleo
    ).first()

    if atuacao and not defensor.eh_defensor:
        atuacao = Atuacao.objects.parcialmente_vigentes().filter(
            defensoria=atuacao.defensoria,
            tipo__in=[Atuacao.TIPO_TITULARIDADE, Atuacao.TIPO_ACUMULACAO],
            ativo=True,
        ).first()

    if atuacao:
        request.session['atuacao_de_plantao_id'] = atuacao.id
    else:
        messages.error(request, u'Erro: Não existe nenhum defensor atuando para realizar um agendamento.')
        return redirect('nucleo_index', nucleo.id)

    if atendimento_numero:
        if remarcar:
            return redirect('agendamento_agendar_remarcar', atendimento_numero=atendimento_numero)
        else:
            return redirect('agendamento_agendar_retorno', atendimento_numero=atendimento_numero)
    else:
        return redirect('agendamento_agendar')


@login_required
def conflitos(request, defensor_id=None):
    if request.POST:
        form = BuscarAtendimentoConflitoForm(request.POST)
    else:
        form = BuscarAtendimentoConflitoForm(request.GET)

    if defensor_id:
        conflitos = conflitos_buscar(request, defensor_id)
    else:
        conflitos = conflitos_buscar(request)

    angular = 'BuscarCtrl'

    return render(request=request, template_name="atendimento/agendamento/conflitos.html", context=locals())


@login_required
def conflitos_buscar(request, defensor=None, ano=None, mes=None):
    data_ini = date.today()
    data_fim = None
    categoria_de_agenda = request.GET.get('categoria_de_agenda')

    # Se ano e mes passados por parametro, gera data inicial e final automaticamente
    if defensor and ano and mes:

        data_ini = date(ano, mes, 1)

        if data_ini < date.today():
            data_ini = date.today()

        data_fim = datetime.combine(
            date(data_ini.year, data_ini.month, calendar.monthrange(data_ini.year, data_ini.month)[1]), time.max)

    # Caso contrario, recupera datas a partir de parametros GET ou POST
    else:
        if request.POST:
            form = BuscarAtendimentoConflitoForm(request.POST)
        else:
            form = BuscarAtendimentoConflitoForm(request.GET)

        if form.is_valid():

            if form.cleaned_data['data_ini'] and form.cleaned_data['data_ini'] >= date.today():
                data_ini = form.cleaned_data['data_ini']
            else:
                data_ini = date.today()

            if form.cleaned_data['data_fim'] and form.cleaned_data['data_fim'] >= date.today():
                data_fim = datetime.combine(form.cleaned_data['data_fim'], time.max)
            else:
                data_fim = None

            if form.cleaned_data['defensor']:
                defensor = form.cleaned_data['defensor']

    agendas = Agenda.objects.filter(
        (Q(atuacao__defensor=defensor) | Q(atuacao__titular=defensor)) &
        Q(data_fim__gte=data_ini) &
        Q(ativo=True)).order_by('-data_cadastro')

    eventos = Evento.objects.filter(
        Q(data_fim__gte=data_ini) &
        Q(tipo=Evento.TIPO_BLOQUEIO) &
        (Q(defensor=None) | Q(defensor__in=agendas.values('atuacao__defensor'))) &
        Q(ativo=True)).order_by('-data_cadastro')

    conflitos = []

    for agenda in agendas:
        agenda.conciliacao = simplejson.loads(agenda.conciliacao)

    atendimentos = AtendimentoDefensor.objects.select_related(
        'qualificacao__area',
        'defensoria',
        'defensor__servidor__usuario',
        'substituto__servidor__usuario',
    ).filter(
        Q(tipo__in=[Atendimento.TIPO_INICIAL, Atendimento.TIPO_RETORNO, Atendimento.TIPO_ENCAMINHAMENTO]),
        Q(data_agendamento__gte=data_ini) &
        Q(data_atendimento=None) &
        (Q(defensor=defensor) | Q(substituto=defensor)) &
        Q(remarcado=None) &
        Q(ativo=True)
    ).order_by('data_agendamento')

    if data_fim:
        atendimentos = atendimentos.filter(data_agendamento__lte=data_fim)

    if categoria_de_agenda:
        eventos = eventos.filter(categoria_de_agenda=categoria_de_agenda)
        atendimentos = atendimentos.filter(agenda=categoria_de_agenda)

    for atendimento in atendimentos:

        conflito = True
        evento_conflito = None
        agenda_conflito = None

        # Passa em todas agendas disponíveis
        for agenda in agendas:

            # Verifica se agenda é da mesma defensoria do atendimento
            if agenda.atuacao.defensoria == atendimento.defensoria:

                # Verifica se agenda é valida para o dia do atendimento
                if agenda.data_ini <= atendimento.data_agendamento.date() <= agenda.data_fim:

                    # Valida se agenda é do titular ou substituto
                    if (atendimento.substituto and atendimento.substituto == agenda.atuacao.defensor) or \
                            (not atendimento.substituto and atendimento.defensor == agenda.atuacao.defensor):

                        # Verifica se agenda possui a categoria do atendimento
                        if str(atendimento.agenda_id) in agenda.conciliacao:
                            # Recupera horários de agendamento para o dia da semana do agendamento

                            week_day = atendimento.data_agendamento.weekday()
                            horarios = agenda.conciliacao[str(atendimento.agenda_id)][week_day]

                            if horarios:
                                # Se agendamento na extra-pauta, não gera conflito
                                if atendimento.data_agendamento.strftime('%H:%M') == "00:00":
                                    conflito = False
                                    break

                                # Passa por todos horarios disponiveis do dia da semana
                                for horario in horarios:  # noqa: E501
                                    # Caso encontre mesmo horario do atendimento, não gera conflito
                                    if atendimento.data_agendamento.strftime('%H:%M') == horario:
                                        conflito = False
                                        break

                        agenda_conflito = agenda
                        break

        for evento in eventos:

            if (evento.comarca is None or evento.comarca == atendimento.defensoria.comarca) and \
                    (evento.data_ini <= atendimento.data_agendamento.date() <= evento.data_fim):

                if (evento.defensor is None
                    or (evento.defensor == atendimento.defensor and atendimento.substituto is None) or (
                        evento.defensor == atendimento.substituto and atendimento.substituto is not None)):

                    if (evento.categoria_de_agenda is None or evento.categoria_de_agenda == atendimento.agenda):
                        evento_conflito = evento
                        conflito = True
                        break

        if conflito:
            conflitos.append([atendimento, evento_conflito, agenda_conflito])

    return conflitos


@login_required
def conflitos_mensal(request, defensor_id, ano, mes):
    return JsonResponse({'qtd': len(conflitos_buscar(request, defensor_id, int(ano), int(mes)))})


@login_required
def conflitos_total(request, defensor_id):
    return JsonResponse({'qtd': len(conflitos_buscar(request, defensor_id))})


@login_required
def conflitos_corrigir(request):
    if request.GET.get('defensor'):

        defensor = request.GET.get('defensor')

        for atendimento, _, agenda in conflitos_buscar(request):

            if agenda:

                remarcado = False
                data_ini = atendimento.data_agendamento.date()
                data_fim = datetime.combine(data_ini, time.max)

                agendamentos = AtendimentoDefensor.objects.filter(
                    Q(data_agendamento__gte=data_ini) &
                    Q(data_agendamento__lte=data_fim) &
                    Q(defensoria=atendimento.defensoria) &
                    (Q(defensor=defensor) | Q(substituto=defensor)) &
                    Q(agenda=atendimento.agenda_id) &
                    Q(remarcado=None) &
                    Q(nucleo=None) &
                    Q(ativo=True)
                ).order_by('agenda', 'data_agendamento')

                for horario in agenda.conciliacao[str(atendimento.agenda_id)][atendimento.data_agendamento.weekday()]:
                    disponivel = True
                    for agendamento in agendamentos:
                        if agendamento.data_agendamento.strftime('%H:%M') == horario:
                            disponivel = False
                            break
                    if disponivel:
                        atendimento.remarcar(
                            origem=None,
                            atuacao_id=atendimento.get_atuacao().id,
                            data_agendamento=datetime.combine(
                                atendimento.data_agendamento.date(),
                                time(*[int(h) for h in horario.split(':')])
                            ),
                            agendado_por=request.user.servidor,
                            categoria_de_agenda=atendimento.agenda_id,
                            automatico=True,
                            # DPE-AM
                            oficio=atendimento.oficio,
                            detalhes=atendimento.detalhes
                        )
                        remarcado = True
                        break

                if not remarcado and atendimento.data_agendamento.time() != time.min:
                    atendimento.remarcar(
                        origem=None,
                        atuacao_id=atendimento.get_atuacao().id,
                        data_agendamento=datetime.combine(atendimento.data_agendamento.date(), time(0, 0)),
                        agendado_por=request.user.servidor,
                        categoria_de_agenda=atendimento.agenda_id,
                        automatico=True,
                        # DPE-AM
                        oficio=atendimento.oficio,
                        detalhes=atendimento.detalhes
                    )

    return conflitos(request)


@login_required
def conflitos_corrigidos(request):

    defensor = None
    data_ini = date.today()
    data_fim = None

    if request.POST:
        form = BuscarAtendimentoConflitoForm(request.POST)
    else:
        form = BuscarAtendimentoConflitoForm(request.GET)

    if form.is_valid():

        if form.cleaned_data['data_ini'] and form.cleaned_data['data_ini'] > date.today():
            data_ini = form.cleaned_data['data_ini']

        if form.cleaned_data['data_fim'] and form.cleaned_data['data_fim'] > date.today():
            data_fim = datetime.combine(form.cleaned_data['data_fim'], time.max)

        if form.cleaned_data['defensor']:
            defensor = form.cleaned_data['defensor']

    atendimentos = AtendimentoDefensor.objects.filter(
        Q(data_agendamento__gte=data_ini) &
        Q(data_atendimento=None) &
        (Q(defensor=defensor) | Q(substituto=defensor)) &
        Q(remarcado_auto=True) &
        Q(remarcado__remarcado=None) &
        Q(ativo=True)
    ).order_by('data_agendamento')

    if data_fim:
        atendimentos = atendimentos.filter(data_agendamento__lte=data_fim)

    relatorios = Relatorio.objects.filter(
        papeis=request.user.servidor.papel,
        locais__pagina=Local.PAG_ATENDIMENTO_CONFLITOS_CORRIGIDOS
    ).ativos()

    angular = 'BuscarCtrl'

    return render(request=request, template_name="atendimento/agendamento/conflitos_corrigidos.html", context=locals())


@login_required
def horarios(request, atendimento_numero=None):
    """Busca horários de agendamento, defensor, defensoria e categorias"""

    from nucleo.itinerante.models import Evento as Itinerante
    # Recupera dados json
    dados = simplejson.loads(request.body)
    encaminhamento = dados.get('encaminhar', False)
    distribuir = dados.get('distribuir', False)

    servidor = request.user.servidor

    if dados.get('itinerante'):

        itinerante = Itinerante.objects.filter(
            data_final__gte=date.today(),
            participantes=servidor,
            ativo=True
        ).order_by(
            'data_inicial'
        ).first()

    else:

        itinerante = None

    if itinerante:
        dados['comarca'] = itinerante.defensoria.comarca.id

    # Dados default
    comarca_id = request.session.get('comarca', servidor.comarca.id)
    atuacao_id = None

    pessoa = None
    assistido = None
    qualificacao = None
    processo = None
    categoria_de_agenda = 1

    data_ini = date(dados['ano'], dados['mes'], 1)

    data_fim = datetime.combine(
        date(data_ini.year, data_ini.month, calendar.monthrange(data_ini.year, data_ini.month)[1]), time.max)

    # Recupera informacoes do atendimento
    if atendimento_numero:

        atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero)
        atendimento = atendimento.at_final

        # pré-seleciona categoria de agenda do atendimetno
        categoria_de_agenda = atendimento.agenda_id

        if atendimento.requerente:
            assistido = atendimento.requerente.pessoa

        # se atendimento originário do itinerante, remove flag para poder encaminhar para defensoria comum
        if encaminhamento and atendimento.defensoria.nucleo and atendimento.defensoria.nucleo.itinerante:
            itinerante = False

        qualificacao = atendimento.qualificacao

    else:

        # Recupera qualificacao
        if request.session.get('qualificacao_id'):
            qualificacao = Qualificacao.objects.get(id=request.session.get('qualificacao_id'))

        # Recupera assistido
        if request.session.get('pessoa_id'):
            assistido = PessoaAssistida.objects.get(id=request.session.get('pessoa_id'))

        # Recupera ligacao
        if request.session.get('ligacao_id'):
            atendimento = Atendimento.objects.get(id=request.session.get('ligacao_id'))
        else:
            atendimento = None

        # Recupera atendimento para processo
        if request.session.get('atendimento_processo_numero'):
            atendimento_processo = AtendimentoDefensor.objects.get(
                numero=request.session.get('atendimento_processo_numero'))
        else:
            atendimento_processo = None

        if atendimento_processo:

            comarca_id = atendimento_processo.defensoria.comarca.id

            for atuacao in Atuacao.objects.filter(
                Q(defensor=atendimento_processo.defensor) &
                Q(defensoria=atendimento_processo.defensoria) &
                Q(ativo=True) & (
                    Q(defensoria__nucleo=None) |
                    (
                        Q(defensoria__nucleo__agendamento=True) &
                        Q(defensoria__nucleo__ativo=True)
                    ))):
                atuacao_id = atuacao.id

        # Recupera processo
        if not dados.get('atuacao') and request.session.get('processo_id'):
            from processo.processo.models import Processo
            processo = Processo.objects.get(id=request.session.get('processo_id'))

        # Se processo e assistido informados, identifica defensoria pela distribuição processual
        if processo and assistido and config.ATIVAR_PROCAPI:
            from procapi_client.services import APIProcesso
            from processo.processo.services import AvisoService

            api_processo = APIProcesso(numero=processo.numero_procapi)

            # Faz até 3 tentativas de consulta se processo está atualizando
            tentativas = 3
            while tentativas > 0:

                sucesso, resposta = api_processo.consultar()

                # Se processo está atualizando, faz nova tentativa daqui 2 segundos
                if sucesso and resposta['atualizando']:
                    tentativas -= 1
                    time_sleep.sleep(2)
                else:
                    tentativas = 0

            if sucesso and resposta['data_ultimo_movimento']:
                # Gera aviso fictício para utilizar o recurso de distribuição processual
                aviso = {
                    'sistema_webservice': resposta['sistema_webservice'],
                    'tipo_documento': None,
                    'processo': {
                        'numero': resposta['numero'],
                        'competencia': resposta['competencia']['codigo'],
                        'orgaoJulgador': {
                            'codigoOrgao': resposta['orgao_julgador']['codigo']
                        }
                    },
                    'destinatario': {
                        'pessoa': {
                            'nome': assistido.nome,
                            'numeroDocumentoPrincipal': assistido.cpf,
                            'data_nascimento': assistido.data_nascimento.strftime('%Y-%m-%dT%H:%M:%S') if assistido.data_nascimento else None,
                            'nome_genitor': assistido.pai.nome if assistido.pai else None,
                            'nome_genitora': assistido.mae.nome if assistido.mae else None,
                            'sexo': 'F' if assistido.sexo == PessoaAssistida.SEXO_FEMININO else 'M',
                        }
                    }
                }

                defensoria = AvisoService().identificar_defensoria(aviso)

                # Se defensoria foi idenficada, força uso da mesma comarca
                if defensoria:
                    dados['defensoria'] = defensoria.id
                    dados['comarca'] = defensoria.comarca_id

    # seleciona categoria informada na requisição, se não foi informada, assume valor padrão
    categoria_de_agenda = dados.get('categoria_de_agenda', categoria_de_agenda)

    # Recupera comarca passada na sessão
    if 'comarca' in dados:

        comarca_id = dados['comarca']

    else:

        if atendimento:

            if atendimento.requerente:
                pessoa = atendimento.requerente.pessoa

            if atendimento.at_defensor:
                comarca_id = atendimento.at_defensor.comarca_id

        elif request.session.get('pessoa_id'):

            pessoa = PessoaAssistida.objects.get(id=request.session.get('pessoa_id'))

            if pessoa.endereco and pessoa.endereco.municipio and pessoa.endereco.municipio.comarca:
                comarca_id = pessoa.endereco.municipio.comarca.id

    # self.request.session.get('comarca', self.request.user.servidor.comarca.id)

    # Recupera defensores que atuam na area/comarca informadas
    atuacoes = []
    eventos = []
    desbloqueios = []
    agendas = []
    agendamentos = {}
    indeferimentos = []
    extra = {}

    atuacao_defensor_id = None
    atuacao_defensoria_id = None

    atuacoes_lst = Atuacao.objects.select_related(
        'defensor',
        'defensoria__comarca',
        'defensoria__nucleo',
    ).prefetch_related(
        'defensoria__categorias_de_agendas'
    ).annotate(
        desbloqueios=Sum(
            Case(
                When(
                    Q(
                        Q(defensoria__agendas__ativo=True) &
                        Q(defensoria__agendas__tipo=Evento.TIPO_PERMISSAO) &
                        Q(defensoria__agendas__data_validade__gte=date.today()) &
                        Q(defensoria__agendas__data_ini__lte=F('data_final')) &
                        Q(defensoria__agendas__data_fim__gte=F('data_inicial')) &
                        ~Q(defensoria__agendas__data_autorizacao=None)
                    ),
                    then=Value(1)
                ),
                default=Value(0),
                output_field=IntegerField()
            )
        ),
    ).filter(
        Q(data_inicial__lte=data_fim) &
        (
            (
                Q(data_final__gte=data_ini) &
                Q(data_final__gt=F('data_inicial')) &
                (
                    Q(data_final__gte=date.today()) |
                    Q(desbloqueios__gt=0)
                )
            ) |
            Q(data_final=None)
        ) &
        Q(defensor__eh_defensor=True) &
        Q(defensoria__comarca_id=comarca_id) &
        Q(titular=None) &
        (
            Q(defensoria__nucleo=None) |
            (
                Q(defensoria__nucleo__agendamento=True) &
                Q(defensoria__nucleo__ativo=True)
            )
        ) &
        Q(ativo=True)
    )

    # só pode encaminhar p/ defensoria da mesma área ou usuário c/ permissão especial
    if qualificacao and encaminhamento and \
            not request.user.has_perm('atendimento.encaminhar_atendimento_para_qualquer_area'):
        atuacoes_lst = atuacoes_lst.filter(defensoria__areas=qualificacao.area)

    if atendimento and hasattr(atendimento, 'defensoria') and (
                                                                atendimento.tipo != Atendimento.TIPO_INICIAL or
                                                                atendimento.realizado):

        if encaminhamento:
            atuacoes_lst = atuacoes_lst.filter(
                ~Q(defensoria=atendimento.defensoria) &
                (
                    Q(defensoria__nucleo=None) |
                    Q(defensoria__nucleo__encaminhamento=True)
                ) &
                (
                    ~Q(defensoria__aceita_encaminhamento_pauta=Defensoria.AGENDAMENTO_NINGUEM) |
                    ~Q(defensoria__aceita_encaminhamento_extra=Defensoria.AGENDAMENTO_NINGUEM)
                )
            )
        elif distribuir:
            proxima_defensoria = distribuir_agendamento(atendimento)
            atuacoes_lst = atuacoes_lst.filter(defensoria_id=proxima_defensoria.id)

        else:
            atuacoes_lst = atuacoes_lst.filter(defensoria=atendimento.defensoria)

    if itinerante:
        atuacoes_lst = atuacoes_lst.filter(evento=itinerante)
    else:
        atuacoes_lst = atuacoes_lst.filter(
            defensoria__evento=None
        )

    if config.SOMENTE_DEFENSORIAS_MESMA_AREA:
        if qualificacao:
            atuacoes_lst = atuacoes_lst.filter(defensoria__areas=qualificacao.area)

    for atuacao in atuacoes_lst:

        if atuacao.defensoria.id == dados['defensoria']:
            atuacao_defensoria_id = atuacao.id
            if atuacao.defensor.id == dados['defensor']:
                atuacao_defensor_id = atuacao.id

        substituicoes = []
        for substituicao in atuacao.substituicao:
            substituicoes.append({
                'id': substituicao.id,
                'defensor': substituicao.defensor.nome,
                'data_ini': Util.date_to_json(substituicao.data_inicial),
                'data_fim': Util.date_to_json(substituicao.data_final),
            })

        nome_atuacao = config.MODO_EXIBICAO_ATUACAO_AO_AGENDAR.format(atuacao=atuacao)

        if config.EXIBIR_DATA_ATUACAO:
            if atuacao.data_inicial and atuacao.data_final:
                nome_atuacao = nome_atuacao + ' ({:%d/%m/%Y} a {:%d/%m/%Y})'.format(atuacao.data_inicial, atuacao.data_final)  # noqa: E501
            elif atuacao.data_inicial:
                nome_atuacao = nome_atuacao + ' (a partir de {:%d/%m/%Y})'.format(atuacao.data_inicial)
            elif atuacao.data_final:
                nome_atuacao = nome_atuacao + ' (até {:%d/%m/%Y})'.format(atuacao.data_final)

        # flag para alertar ao usuário que está encaminhando para área diferente da atuação da defensoria
        encaminando_area_diferente = False

        if qualificacao and encaminhamento and not atuacao.defensoria.areas.filter(id=qualificacao.area_id).exists():
            encaminando_area_diferente = True

        atuacoes.append({
            'id': atuacao.id,
            'nome': nome_atuacao,
            'defensor_id': atuacao.defensor.id,
            'defensor': atuacao.defensor.nome,
            'defensoria_id': atuacao.defensoria.id,
            'defensoria': atuacao.defensoria.nome,
            'comarca': atuacao.defensoria.comarca.id,
            'substituicoes': substituicoes,
            'nucleo': {'id': atuacao.defensoria.nucleo.id,
                       'nome': atuacao.defensoria.nucleo.nome} if atuacao.defensoria.nucleo else None,
            'categorias_de_agendas': list(atuacao.defensoria.categorias_de_agendas.all().values('id', 'nome')),
            'encaminando_area_diferente': encaminando_area_diferente,
        })

    dados['atuacao_defensor_id'] = atuacao_defensor_id
    dados['atuacao_defensoria_id'] = atuacao_defensoria_id

    if atuacao_defensor_id:
        dados['atuacao'] = atuacao_defensor_id
    elif atuacao_defensoria_id:
        dados['atuacao'] = atuacao_defensoria_id

    # Recupera atuacao do defensor
    if 'atuacao' in dados:
        atuacao_id = dados['atuacao']

    # Selecao automatica em caso de apenas uma atuação
    if atuacoes_lst.count() == 1:
        atuacao_id = atuacoes_lst.first().id

    atuacao = None
    if atuacao_id:

        defensores = []

        for atuacao in Atuacao.objects.filter(
                id=atuacao_id,
                defensoria__comarca=comarca_id,
                defensor__eh_defensor=True
                ):

            # Inclui titular na lista
            defensores.append(atuacao.defensor.id)

            # Inclui substitutos na lista
            for substituicao in atuacao.substituicao:
                defensores.append(substituicao.defensor.id)

            dia_semana, dias_mes = calendar.monthrange(data_ini.year, data_ini.month)

            # Se catagoria nao existe, assume primeira ou nenhuma se não tem categorias
            if not atuacao.defensoria.categorias_de_agendas.filter(id=categoria_de_agenda).exists():
                if atuacao.defensoria.categorias_de_agendas.exists():
                    categoria_de_agenda = atuacao.defensoria.categorias_de_agendas.first().id
                else:
                    categoria_de_agenda = None

            # carrega agendas do substituto
            for agenda in Agenda.objects.filter(
                    atuacao__id__in=atuacao.substituicao,
                    data_ini__lte=data_fim,
                    data_fim__gte=data_ini,
                    ativo=True).order_by('-data_cadastro'):

                agendas.append(Util.object_to_dict(agenda, {}))

                agendas[-1]['horarios'] = []
                agendas[-1]['forma_atendimento'] = []
                horarios_object = simplejson.loads(agendas[-1]['conciliacao'])

                if categoria_de_agenda:
                    try:
                        agendas[-1]['horarios'] = horarios_object[str(categoria_de_agenda)]
                        agendas[-1]['forma_atendimento'] = horarios_object['forma_atendimento'][str(categoria_de_agenda)]  # noqa: E501
                    except KeyError:
                        pass

            # carrega agendas do titular
            for agenda in Agenda.objects.filter(
                    atuacao__id=atuacao.id,
                    data_ini__lte=data_fim,
                    data_fim__gte=data_ini,
                    ativo=True).order_by('-data_cadastro'):

                # se agenda termina depois da atuação, mostra apenas até a data final da atuação
                if atuacao.data_final and agenda.data_fim > atuacao.data_final.date():
                    agenda.data_fim = atuacao.data_final

                # se agenda começa antes da atuação, mostra apenas após a data inicial da atuação
                if atuacao.data_inicial and agenda.data_ini < atuacao.data_inicial.date():
                    agenda.data_ini = atuacao.data_inicial

                # se não aceita agendamento futuro, mostra apenas agenda de hoje
                if not atuacao.defensoria.aceita_agendamento_futuro:
                    agenda.data_fim = datetime.combine(datetime.today(), time.max)

                agendas.append(Util.object_to_dict(agenda, {}))

                agendas[-1]['horarios'] = []
                agendas[-1]['forma_atendimento'] = []
                horarios_object = simplejson.loads(agendas[-1]['conciliacao'])

                try:
                    agendas[-1]['horarios'] = horarios_object[str(categoria_de_agenda)]
                    agendas[-1]['forma_atendimento'] = horarios_object['forma_atendimento'][str(categoria_de_agenda)]
                except KeyError:
                    pass

            if not itinerante:

                # Lista de eventos de bloqueio (feriados) no mês
                lista_eventos = Evento.objects.filter(
                    (
                        (
                            Q(defensor__in=defensores) |
                            Q(defensor=None)
                        ) &
                        (
                            Q(defensoria=atuacao.defensoria) |
                            Q(defensoria=None)
                        ) &
                        (
                            Q(comarca=atuacao.defensoria.comarca) |
                            Q(comarca=None)
                        ) &
                        (
                            Q(categoria_de_agenda=categoria_de_agenda) |
                            Q(categoria_de_agenda=None)
                        )
                    ) &
                    Q(data_ini__lte=data_fim) &
                    Q(data_fim__gte=data_ini) &
                    Q(tipo=Evento.TIPO_BLOQUEIO) &
                    Q(ativo=True)
                )

                for i, evento in enumerate(lista_eventos):
                    eventos.append(Util.object_to_dict(evento, {}))

            # Lista de eventos de desbloqueio no mês
            lista_eventos = Evento.objects.filter(
                Q(ativo=True) &
                Q(tipo=Evento.TIPO_PERMISSAO) &
                Q(data_validade__gte=date.today()) &
                Q(data_ini__lte=data_fim) &
                Q(data_fim__gte=data_ini) &
                ~Q(data_autorizacao=None) &
                (
                    Q(comarca=None) |
                    Q(defensoria=atuacao.defensoria) |
                    (
                        Q(comarca=atuacao.defensoria.comarca) &
                        Q(defensoria=None)
                    )
                )
            )

            for i, evento in enumerate(lista_eventos):
                desbloqueios.append(Util.object_to_dict(evento, {}))

            # Recupera horarios marcados no mes para o defensor
            atendimentos = AtendimentoDefensor.objects.filter(
                Q(defensoria=atuacao.defensoria) &
                Q(data_agendamento__year=data_ini.year) &
                Q(data_agendamento__month=data_ini.month) &
                (
                    (
                        Q(data_agendamento__range=[date.today(), date.today() + timedelta(days=1)]) &
                        Q(data_atendimento__range=[date.today(), date.today() + timedelta(days=1)])
                    ) |
                    Q(data_atendimento=None)
                ) &
                Q(remarcado=None) &
                Q(agenda=categoria_de_agenda) &
                Q(ativo=True)
            ).exclude(
                filhos__tipo=Atendimento.TIPO_NUCLEO
            ).order_by('data_agendamento')

            if not itinerante:
                atendimentos = atendimentos.filter(defensor=atuacao.defensor)

            atendimentos = atendimentos.extra(where=['extract(hour from atendimento_atendimento.data_agendamento) != 0 OR extract(minute from atendimento_atendimento.data_agendamento) != 0'])  # noqa: E501

            for atendimento in atendimentos:

                if atendimento.data_agendamento.day not in agendamentos:
                    agendamentos[atendimento.data_agendamento.day] = {'length': 0}

                agendamentos[atendimento.data_agendamento.day]['length'] += 1

                hora = Util.time_to_json(atendimento.data_agendamento)[:5]

                if hora in agendamentos[atendimento.data_agendamento.day]:
                    agendamentos[atendimento.data_agendamento.day][hora] += 1
                else:
                    agendamentos[atendimento.data_agendamento.day][hora] = 1

            atendimentos = AtendimentoDefensor.objects.filter(
                Q(defensoria=atuacao.defensoria) &
                Q(data_agendamento__year=data_ini.year) &
                Q(data_agendamento__month=data_ini.month) &
                (
                    (
                        Q(data_agendamento__range=[date.today(), date.today() + timedelta(days=1)]) &
                        Q(data_atendimento__range=[date.today(), date.today() + timedelta(days=1)])
                    ) |
                    Q(data_atendimento=None)
                ) &
                Q(remarcado=None) &
                Q(agenda=categoria_de_agenda) &
                Q(ativo=True)
            ).order_by('data_agendamento')

            if not itinerante:
                atendimentos = atendimentos.filter(defensor=atuacao.defensor)

            atendimentos = atendimentos.extra(where=['extract(hour from data_agendamento) = 0 AND extract(minute from data_agendamento) = 0'])  # noqa: E501

            for atendimento in atendimentos:

                if atendimento.data_agendamento.day not in extra:
                    extra[atendimento.data_agendamento.day] = 0

                extra[atendimento.data_agendamento.day] += 1

        atuacao = Atuacao.objects.get(id=atuacao_id)

        # procura atendimentos onde assistido atual é um dos requeridos
        if assistido:
            atendimentos_lst = AtendimentoDefensor.objects.filter(
                Q(partes__pessoa=assistido) &
                Q(partes__tipo=AtendimentoPessoa.TIPO_REQUERIDO) &
                (
                    Q(defensoria=atuacao.defensoria) |
                    (
                        Q(defensor=atuacao.defensor) | Q(defensor=atuacao.titular)
                    )
                ) &
                Q(ativo=True))

            for atendimento in atendimentos_lst:
                indeferimentos.append({
                    'nivel': 2,
                    'numero': atendimento.numero,
                    'area': atendimento.qualificacao.area.nome if atendimento.qualificacao else None,
                    'pedido': atendimento.qualificacao.titulo if atendimento.qualificacao else None,
                    'requerente': atendimento.requerente.pessoa.nome if atendimento.requerente else None,
                    'requerido': atendimento.requerido.pessoa.nome if atendimento.requerido else None,
                    'defensor': atendimento.defensor.nome,
                    'defensoria': atendimento.defensoria.nome,
                    'data_atendimento': Util.date_to_json(atendimento.data_atendimento),
                })

            processos_indeferimento = Indeferimento.objects.filter(
                defensor=atuacao.defensor,
                pessoa=assistido
            ).only(
                'defensor__servidor__nome',
                'pessoa__nome',
                'justificativa',
                'processo__cadastrado_em'
            )

            for indeferimento in processos_indeferimento:
                indeferimentos.append({
                    'nivel': 1,
                    'defensor': indeferimento.defensor.nome,
                    'assistido': indeferimento.pessoa.nome,
                    'justificativa': indeferimento.justificativa,
                    'data_cadastro': Util.date_to_json(indeferimento.processo.cadastrado_em),
                })

    lista_grupos_agendamento = None
    aceitar_agend_pauta = False
    aceitar_agend_extrapauta = False
    servidor_pertence_ao_disk = request.user.has_perm(perm='atendimento.view_129')

    if atuacao:

        if config.BLOQUEAR_AGENDAMENTO_ENTRE_DEFENSORIAS:

            # verifica se o servidor está na unidade selecionada
            if servidor.defensor.defensorias.filter(id=atuacao.defensoria_id).exists():
                aceitar_agend_pauta = True
                aceitar_agend_extrapauta = True
            else:
                # ids grupos defensoria selecionada
                ids_grupos_defensoria_selecionada = set(
                    atuacao.defensoria.grupos_de_agendamento.values_list('id', flat=True))

                # ids grupos defensorias servidor
                ids_grupos_defensorias_do_servidor = set(
                    servidor.defensor.defensorias.values_list("grupos_de_agendamento__id", flat=True))

                if (ids_grupos_defensoria_selecionada and
                        ids_grupos_defensorias_do_servidor and
                        ids_grupos_defensorias_do_servidor != {None}):
                    pertencem_ao_mesmo_grupo = ids_grupos_defensoria_selecionada & ids_grupos_defensorias_do_servidor
                    if pertencem_ao_mesmo_grupo:
                        lista_grupos_agendamento = GrupoDeDefensoriasParaAgendamento.objects.filter(
                            id__in=list(pertencem_ao_mesmo_grupo),
                            ativo=True
                        )
                # disk 129 tentando agendar e a defensoria pertence a um grupo
                elif servidor_pertence_ao_disk and ids_grupos_defensoria_selecionada:
                    lista_grupos_agendamento = GrupoDeDefensoriasParaAgendamento.objects.filter(
                        id__in=list(ids_grupos_defensoria_selecionada),
                        ativo=True
                    )
                elif servidor_pertence_ao_disk:
                    aceitar_agend_pauta = True
                    aceitar_agend_extrapauta = True

            if lista_grupos_agendamento:
                for grupo_agendamento in lista_grupos_agendamento:
                    if grupo_agendamento.aceitar_agend_pauta:
                        aceitar_agend_pauta = True
                    if grupo_agendamento.aceitar_agend_extrapauta:
                        aceitar_agend_extrapauta = True

        if encaminhamento:
            # pode encaminar para a pauta se a defensoria de destino aceitar
            pode_agendar_pauta = Defensoria.verifica_permissao_agendamento(
                atuacao.defensoria.aceita_encaminhamento_pauta, request.user)
            # pode encaminhar para a extra-pauta se a defensoria de destino aceitar
            pode_agendar_extra = Defensoria.verifica_permissao_agendamento(
                atuacao.defensoria.aceita_encaminhamento_extra, request.user)
        else:
            # pode agendar na pauta se usuário tem permissão e defensoria aceita agendamento na pauta
            pode_agendar_pauta = Defensoria.verifica_permissao_agendamento(
                atuacao.defensoria.aceita_agendamento_pauta, request.user)
            # pode agendar na extra-pauta se usuário tem permissão e defensoria aceita agendamento na extra-pauta
            pode_agendar_extra = Defensoria.verifica_permissao_agendamento(
                atuacao.defensoria.aceita_agendamento_extra, request.user)

    else:

        # Verifica se usuário tem permissão para realizar agendamentos
        pode_agendar_pauta = pode_agendar_extra = (
            servidor_pertence_ao_disk or
            request.user.has_perm(perm='atendimento.view_recepcao')
        )

    grupo_agendamento = {
        'BLOQUEAR_AGENDAMENTO_ENTRE_DEFENSORIAS': config.BLOQUEAR_AGENDAMENTO_ENTRE_DEFENSORIAS,
        'aceitar_agend_pauta': aceitar_agend_pauta,
        'aceitar_agend_extrapauta': aceitar_agend_extrapauta,
    }

    return {
        'grupo_agendamento': grupo_agendamento,
        'pode_agendar_pauta': pode_agendar_pauta,
        'pode_agendar_extra': pode_agendar_extra,
        'pode_agendar_com_bloqueio': request.user.has_perm('atendimento.agendar_com_bloqueio'),
        'itinerante': True if itinerante else False,
        'consulta': (qualificacao is None),
        'comarca': int(comarca_id) if comarca_id else None,
        'comarcas': list(Comarca.objects.ativos().values('id', 'nome')),
        'atuacao': int(atuacao_id) if atuacao_id else None,
        'atuacoes': atuacoes,
        'agendas': agendas,
        'eventos': eventos,
        'desbloqueios': desbloqueios,
        'agendamentos': agendamentos,
        'indeferimentos': indeferimentos,
        'extra': extra,
        'categoria_de_agenda': categoria_de_agenda,
        'hoje': Util.date_to_json(date.today())}


class AgendamentoView(TemplateView):
    template_name = 'atendimento/agendamento/agendar.html'
    ligacao = None
    atendimento = None
    processo = None
    pessoa = None
    remarcando = False
    retorno = False

    def post(self, request, *args, **kwargs):
        return JsonResponse(horarios(request, self.kwargs.get('atendimento_numero')), safe=False)

    def get(self, request, *args, **kwargs):

        # Se núcleo plantão, redireciona para agendamento de plantão
        if self.request.session.get('nucleo') and self.request.session['nucleo'].plantao:
            return agendar_plantao(request, self.kwargs.get('atendimento_numero'), self.remarcando)

        # Se tem pessoa, carrega informações
        if self.request.session.get('pessoa_id'):
            self.pessoa = PessoaAssistida.objects.get(id=self.request.session.get('pessoa_id'))

        # Se tem ligação, carrega informações
        if self.request.session.get('ligacao_id'):
            self.ligacao = Atendimento.objects.get(id=self.request.session.get('ligacao_id'))
            if not request.session.get('agendamento_anotacao') and self.ligacao.historico_recepcao:
                request.session['agendamento_anotacao'] = self.ligacao.historico_recepcao
            # Se ligação não tem pessoa, redireciona p/ página de ligação
            if self.ligacao.requerente:
                self.pessoa = self.ligacao.requerente.pessoa
            else:
                return redirect('{}?next={}'.format(reverse('precadastro_index'), self.request.META.get('HTTP_REFERER')))  # noqa: E501

        # Se número de atendimento foi informado, carrega informações
        if self.kwargs.get('atendimento_numero'):

            self.atendimento = AtendimentoDefensor.objects.get(numero=self.kwargs.get('atendimento_numero'))

            # Se tem ligação em andamento e a pessoa não é a mesma do atendimento, redireciona p/ página de ligação
            if (self.ligacao and self.ligacao.requerente and self.atendimento.requerente
                    and self.ligacao.requerente.pessoa != self.atendimento.requerente.pessoa):
                return redirect('{}?next={}'.format(reverse('precadastro_index'), self.request.META.get('HTTP_REFERER')))  # noqa: E501

            # TODO: Verificar porque alguns atendimentos não possuem requerente vinculado
            if self.atendimento.requerente:
                self.pessoa = self.atendimento.requerente.pessoa

            # Se agendamento de retorno e existe retornos pendentes, retorna para página anterior
            if self.retorno:
                if self.atendimento.retornos_pendentes:
                    messages.error(request, u'Erro: Já existe um retorno marcado para este atendimento!')
                    return redirect(request.META.get('HTTP_REFERER', '/'))
                else:
                    # Define último atendimento da árvore como referência para agendamento de retorno
                    self.atendimento = self.atendimento.at_final

        # Se tem processo vinculado, carrega informações
        if self.request.session.get('processo_id'):
            from processo.processo.models import Processo
            self.processo = Processo.objects.get(id=self.request.session.get('processo_id'))

        # Se pessoa foi identificada, exibe horários disponíveis, senão, retorna para página inicial
        if self.pessoa:
            return super(AgendamentoView, self).get(request, *args, **kwargs)
        else:
            return redirect('index')

    def get_context_data(self, **kwargs):

        self.request.session['justificativa'] = None

        context = super(AgendamentoView, self).get_context_data(**kwargs)

        # Se houver ligacao em andamento, atualiza cronometro
        if self.ligacao:
            cronometro = self.ligacao.cronometro
            cronometro.atualizar()

        hoje = date.today()
        dia_um = datetime(hoje.year, hoje.month, 1)

        # Dados iniciais para exibição
        dados_iniciais = {
            'ano': hoje.year,
            'mes': hoje.month,
            'comarca': None,
            'anotacoes': self.request.session.pop('agendamento_anotacao', '')
        }

        # Se tem atendimento, inclui informações para exibição
        if self.atendimento:
            dados_iniciais.update({
                'defensor': self.atendimento.defensor_id,
                'categoria_de_agenda': self.atendimento.agenda_id,
            })
            # TODO: Verificar porque alguns atendimentos não possuem defensor/defensoria
            if self.atendimento.defensoria:
                dados_iniciais.update({
                    'comarca': self.atendimento.defensoria.comarca_id,
                    'defensoria': self.atendimento.defensoria_id,
                })

        # Se tem dados na sessão, atualiza informações para exibição
        if self.request.session.get('agendamento_atuacao'):
            atuacao = Atuacao.objects.get(id=self.request.session.pop('agendamento_atuacao'))
            data = self.request.session.pop('agendamento_data')
            dados_iniciais.update({
                'ano': data.year,
                'mes': data.month,
                'comarca': atuacao.defensoria.comarca_id,
                'defensoria': atuacao.defensoria_id,
                'defensor': atuacao.defensor_id,
                'categoria_de_agenda': self.request.session.pop('agendamento_categoria_de_agenda', 1),
                'prazo': self.request.session.pop('agendamento_prazo', False),
                'prioridade': self.request.session.pop('agendamento_prioridade', self.pessoa.prioridade() if self.pessoa else AtendimentoDefensor.PRIORIDADE_0),  # noqa: E501
            })

        context['hoje'] = hoje
        context['dia_um'] = dia_um
        context['retorno'] = self.retorno
        context['remarcando'] = self.remarcando
        context['atendimento'] = self.atendimento
        context['processo'] = self.processo
        context['pessoa'] = self.pessoa
        context['dados_iniciais'] = dados_iniciais
        context['angular'] = 'AgendamentoCtrl'
        context['conteudo_sms_angular'] = prepara_conteudo_sms_angular(
            self.get_conteudo_sms_angular(),
            self.atendimento)

        return context

    def get_conteudo_sms_angular(self):
        return ''


class InicialView(AgendamentoView):

    def get_conteudo_sms_angular(self):
        return config.MENSAGEM_SMS_AGENDAMENTO_INICIAL


class RemarcarView(AgendamentoView):
    remarcando = True

    def get_conteudo_sms_angular(self):
        return config.MENSAGEM_SMS_AGENDAMENTO_REMARCACAO


class RetornoView(AgendamentoView):
    retorno = True

    def get_conteudo_sms_angular(self):
        return config.MENSAGEM_SMS_AGENDAMENTO_RETORNO


class CalendarioView(TemplateView):
    template_name = 'atendimento/agendamento/agendar.html'

    def post(self, request, *args, **kwargs):
        return JsonResponse(horarios(request), safe=False)

    def get_context_data(self, **kwargs):

        context = super(CalendarioView, self).get_context_data(**kwargs)

        hoje = date.today()
        dia_um = datetime(hoje.year, hoje.month, 1)

        context['hoje'] = hoje
        context['dia_um'] = dia_um
        context['consulta'] = True
        context['angular'] = 'AgendamentoCtrl'

        return context


@login_required
def nucleo(request, atendimento_numero):
    if request.method == 'POST':
        return JsonResponse(horarios(request, atendimento_numero))

    request.session['justificativa'] = None

    atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero)
    pessoa = atendimento.requerente

    angular = 'AgendamentoCtrl'

    return render(request=request, template_name="atendimento/agendamento/agendar.html", context=locals())


@login_required
def nucleo_confirmar(request, atendimento_numero):
    atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero)

    if request.method == 'POST':
        messages.success(request, u'Pedido de apoio confirmado para o núcleo!')
        return redirect('atendimento_atender', atendimento.origem.numero)

    relatorios = Relatorio.objects.filter(
        papeis=request.user.servidor.papel,
        locais__pagina=Local.PAGINA_AGENDAMENTO_CONFIRMAR
    ).ativos()

    angular = 'ImprimirCtrl'

    return render(request=request, template_name="atendimento/agendamento/confirmar.html", context=locals())


@login_required
def justificar(request):
    if request.method == 'POST':
        # Recupera dados json
        dados = simplejson.loads(request.body)
        request.session['justificativa'] = dados.get('justificativa')

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})


@login_required
def processo(request, atendimento_numero):

    atendimento = Atendimento.objects.get(numero=atendimento_numero)

    # armazena numero do atendimento para processo
    request.session['atendimento_processo_numero'] = atendimento_numero

    # armazena id da pessoa vinculada ao atendimento para processo
    if atendimento.requerente:
        request.session['pessoa_id'] = atendimento.requerente.pessoa_id

    redirect_to = None

    if atendimento.qualificacao_id:
        request.session['qualificacao_id'] = atendimento.qualificacao_id
        # redireciona para o agendamento
        redirect_to = reverse('agendamento_index')
    else:
        # redireciona para a qualificacao
        if request.session.get('ligacao_id'):
            redirect_to = reverse('qualificacao_index', args=[request.session.get('ligacao_id'), ])
        else:
            redirect_to = reverse('qualificacao_index')

    return redirect('{}?next={}'.format(redirect_to, request.GET.get('next', '')))


def envia_sms_agendamento(request, atendimento, data_agendamento, modelo_sms):

    """""Método que envia um SMS com os dados do atendimento"""

    logger.error("DPERR >> atendimento.defensor.nome: {}".format(atendimento.defensor.nome))
    logger.error("DPERR >> atendimento.numero: {}".format(atendimento.numero))

    texto_hora = data_agendamento.strftime("%H:%M")
    sms_artigo = 'as'
    # Se a configuração ATENDIMENTO_HORARIO_UNICO_POR_TURNO estiver ativada
    if (config.ATENDIMENTO_HORARIO_UNICO_POR_TURNO):
        # Mostra a hora fixa
        if (int(data_agendamento.strftime('%H')) < 13):
            texto_hora = config.HORARIO_FIXO_MANHA
        else:
            texto_hora = config.HORARIO_FIXO_TARDE

    #  Se a configuração ATENDIMENTO_EXTRA_PAUTA_HORARIO_UNICO estiver ativada
    if (config.ATENDIMENTO_EXTRA_PAUTA_HORARIO_UNICO and not config.ATENDIMENTO_HORARIO_UNICO_POR_TURNO):
        # verifica se é extra-pauta 00:00
        if (int(data_agendamento.strftime('%H')) == 0):
            texto_hora = config.HORARIO_FIXO_EXTRA_PAUTA
            sms_artigo = 'das'

    # Prepara a mensagem a ser enviada
    conteudo_sms = modelo_sms.replace(
        "SMS_DEF_SIGLA", settings.SIGLA_INSTITUICAO
    ).replace(
        "SMS_DIA", data_agendamento.strftime("%d/%m/%Y")
    ).replace(
        "SMS_HORA", texto_hora
    ).replace(
        "SMS_DEFENSOR", atendimento.defensor.nome
    ).replace(
        "SMS_NUMERO_ATENDIMENTO", str(atendimento.numero)
    ).replace(
        "SMS_ARTIGO", sms_artigo
    )

    # Se tem que remover os acentos, remove
    if (config.SMS_REMOVER_ACENTOS):
        conteudo_sms = Util.unaccent(conteudo_sms)

    # Envia o SMS para o assistido informando do agendamento
    telefone = atendimento.telefone_para_sms

    # Se o telefone não for encontrado, retorna mensagem de erro
    if (not telefone['telefone']):
        mensagem = "Nenhum SMS enviado!"
        if (telefone['no_valid_cell']):
            mensagem += " Nenhum telefone válido"
        messages.error(request, mensagem)
    else:
        # Formata o telefone e envia
        telefone_numero = '55{}{}'.format(telefone['telefone'].ddd, telefone['telefone'].numero)
        envio = envia_sms(conteudo_sms, telefone_numero)

        # se não foi possível enviar, adiciona mensagem de erro
        if not (envio.status_code >= 200 and envio.status_code < 300):
            mensagem = "Não foi possível enviar o SMS! Código do erro: {}".format(envio.status_code)
            messages.error(request, mensagem)
        else:
            # verifica se a flag envio pelo facilita sms se sim faz tratamento de erro para o retorno da FACILITA Movel
            if (config.FACILITA_SMS_AUTH):
                statusresposta = envio.content.decode('utf-8').split(';')
                if (statusresposta[0] != '6'):
                    logger.error("DPE >> Erro de Envio de SMS status facilita SMS: {}".format(statusresposta))
                    mensagem = "Não foi possível enviar o SMS! Código do erro: {}".format(statusresposta[0])
                    messages.error(request, mensagem)
                else:
                    mensagem = "SMS enviado com sucesso!"
                    messages.success(request, mensagem)
            else:
                mensagem = "SMS enviado com sucesso!"
                messages.success(request, mensagem)


def envia_email_agendar(request, atendimento, data_agendamento, modelo_sms):
    """""Método que envia um Email com os dados do atendimento"""

    logger.info("DPEAC >> atendimento.defensor.nome: {}".format(atendimento.defensor.nome))
    logger.info("DPEAC >> atendimento.numero: {}".format(atendimento.numero))

    texto_hora = data_agendamento.strftime("%H:%M")
    sms_artigo = 'as'
    # Se a configuração ATENDIMENTO_HORARIO_UNICO_POR_TURNO estiver ativada
    if (config.ATENDIMENTO_HORARIO_UNICO_POR_TURNO):
        # Mostra a hora fixa
        if (int(data_agendamento.strftime('%H')) < 13):
            texto_hora = config.HORARIO_FIXO_MANHA
        else:
            texto_hora = config.HORARIO_FIXO_TARDE

    #  Se a configuração ATENDIMENTO_EXTRA_PAUTA_HORARIO_UNICO estiver ativada
    if (config.ATENDIMENTO_EXTRA_PAUTA_HORARIO_UNICO and not config.ATENDIMENTO_HORARIO_UNICO_POR_TURNO):
        # verifica se é extra-pauta 00:00
        if (int(data_agendamento.strftime('%H')) == 0):
            texto_hora = config.HORARIO_FIXO_EXTRA_PAUTA
            sms_artigo = 'das'

    # Prepara a mensagem a ser enviada
    conteudo_sms = modelo_sms.replace(
        "SMS_DEF_SIGLA", settings.SIGLA_INSTITUICAO
    ).replace(
        "SMS_DIA", data_agendamento.strftime("%d/%m/%Y")
    ).replace(
        "SMS_HORA", texto_hora
    ).replace(
        "SMS_DEFENSOR", atendimento.defensor.nome
    ).replace(
        "SMS_NUMERO_ATENDIMENTO", str(atendimento.numero)
    ).replace(
        "SMS_ARTIGO", sms_artigo
    )

    # Envia o Email para o assistido informando do agendamento
    email = atendimento.requerente.pessoa.email
    logger.info("DPEAC >> atendimento.assistido email: {}".format(email))
    if (email):
        resposta = envia_email(conteudo_sms, email, config.ASSUNTO_EMAIL_NOTIFICACAO)
        if (resposta == 0):
            mensagem = "O email não foi enviado!"
            messages.error(request, mensagem)
        else:
            mensagem = "Email enviado com sucesso!"
            messages.success(request, mensagem)
    else:
        mensagem = "Assistido não tem e-mail cadastrado"
        messages.error(request, mensagem)


def prepara_conteudo_sms_angular(pre_conteudo, atendimento):

    """
    Substitui as palavras chaves de acordo com o atendimento.
    O atendimento nunca mostra o número na preview,
    pois não é possível ter certeza sobre o número que será gerado.
    A hora não é exibida na preview,
    a menos que o horário fixo seja definido nas configurações.
    """

    numero_atendimento = 'XXXXXXXXXXXX'
    texto_hora = "HH:MM"

    # Se a configuração ATENDIMENTO_HORARIO_UNICO_POR_TURNO estiver ativada
    if (config.ATENDIMENTO_HORARIO_UNICO_POR_TURNO):
        # Mostra a hora fixa
        texto_hora = "[[( (horario | date : 'H')*1 < 13) ? '{}' : '{}']]".format(
            config.HORARIO_FIXO_MANHA,
            config.HORARIO_FIXO_TARDE
        )

    return pre_conteudo.replace(
        "SMS_DEF_SIGLA",  settings.SIGLA_INSTITUICAO
    ).replace(
        "SMS_DIA",       "[[ dia.data | date:'dd/MM/yyyy' ]]"
    ).replace(
        "SMS_HORA",      texto_hora
    ).replace(
        "SMS_DEFENSOR",  "[[ atuacao.substituto | default: atuacao.defensor ]]"
    ).replace(
        "SMS_NUMERO_ATENDIMENTO",  numero_atendimento
    )


def distribuir_agendamento(atendimento_atual):

    """""Método que informa a próxima defensoria que receberá um atendimento em uma distribuição automática"""

    proxima_defensoria = None

    if atendimento_atual.encaminhado_para:
        proxima_defensoria = atendimento_atual.encaminhado_para
    else:
        # defensorias que atuam na mesma área do atendimento em curso
        defensorias = Defensoria.objects.filter(
            comarca=atendimento_atual.defensoria.comarca,
            areas=atendimento_atual.qualificacao.area,
            encaminhamento_distribuido=True,
            all_atuacoes__ativo=True,
            all_atuacoes__tipo__in=[Atuacao.TIPO_TITULARIDADE, Atuacao.TIPO_ACUMULACAO, Atuacao.TIPO_SUBSTITUICAO],
        ).order_by('numero').distinct()

        # busca último atendimento realizado na mesma comarca e área que o atendimento em curso
        ultimo_atendimento = AtendimentoDefensor.objects.filter(
            encaminhado_para__in=defensorias,
            ativo=True
        ).order_by('-data_encaminhado').first()

        if ultimo_atendimento:
            proxima_defensoria = defensorias.filter(numero__gt=ultimo_atendimento.encaminhado_para.numero).first()

        if not proxima_defensoria:
            proxima_defensoria = defensorias.first()

        atendimento_atual.encaminhado_para = proxima_defensoria
        atendimento_atual.data_encaminhado = datetime.now()
        atendimento_atual.save()

    return proxima_defensoria
