# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import json
from datetime import datetime, time, timedelta

from constance import config
from django.conf import settings
from django.db.models import Case, When, Value, IntegerField
from django.db.models import Q

from defensor.models import Atuacao
from atendimento.atendimento.models import Defensor as AtendimentoDefensor
from evento.models import Agenda, Evento

TIPOS_ATENDIMENTO_VALIDOS_PARA_AGENDAMENTO_RETORNO = (
    AtendimentoDefensor.TIPO_INICIAL,
    AtendimentoDefensor.TIPO_RETORNO,
    AtendimentoDefensor.TIPO_ENCAMINHAMENTO
)


# TODO: Unificar com atendimento.agendamento.views.horarios
def proximos_horarios_disponiveis(defensoria, defensor=None, quantidade=1, dias_limite=90, dias_diferentes=False,
                                  categoria_agenda=None, forma_atendimento=None, tipos_atendimentos=TIPOS_ATENDIMENTO_VALIDOS_PARA_AGENDAMENTO_RETORNO):  # noqa: E501

    if settings.USAR_EDEFENSOR:
        categoria_agenda = settings.EDEFENSOR_CATEGORIA_AGENDA_ID

    # Se forma atendimento não informada, mas configuração está ativada, define remoto como padrão
    if forma_atendimento is None and config.EXIBIR_PRESENCIAL_REMOTO_AGENDAMENTO:
        forma_atendimento = 'remoto'

    data_base = datetime.now().date() + timedelta(days=1)  # amanhã
    data_limite = data_base + timedelta(days=dias_limite)
    hora_limite = datetime.combine(data_limite, time.max)
    extra_pauta = time(0, 0, 0)

    resposta = []

    # agendas do setor
    agendas = Agenda.objects.annotate(
        substituicao=Case(
            When(
                atuacao__tipo=Atuacao.TIPO_SUBSTITUICAO,
                then=Value(1)
            ),
            default=Value(0),
            output_field=IntegerField()),
    ).filter(
        Q(atuacao__defensoria=defensoria) &
        Q(ativo=True) &
        Q(data_ini__lte=data_limite) &
        (
            Q(data_fim__gte=data_base) |
            Q(data_fim=None)
        )
    ).order_by(
        '-substituicao', '-data_cadastro'
    ).values(
        'id',
        'data_ini',
        'data_fim',
        'conciliacao',
        'substituicao',
        'defensor_id',
        'atuacao_id',
        'atuacao__defensor_id',
        'defensor__servidor__nome',
    )

    # base atuações
    atuacoes = Atuacao.objects.vigentes(
        inicio=data_limite,
        termino=data_base
    ).filter(
        defensoria=defensoria
    ).order_by(
        'data_inicial',
        'data_final'
    ).values(
        'data_inicial',
        'data_final'
    )

    # base substituições
    substituicoes_index = 0
    substituicoes = atuacoes.substituicoes()

    # base bloqueios nas agendas
    bloqueios_index = 0

    q_evento = Q()
    q_evento &= Q(tipo=Evento.TIPO_BLOQUEIO)
    q_evento &= Q(ativo=True)
    q_evento &= Q(data_ini__lte=data_limite)
    q_evento &= Q(data_fim__gte=data_base)
    q_evento &= (
        Q(comarca=None) |
        Q(comarca=defensoria.comarca)
    )
    q_evento &= (
        Q(defensoria=None) |
        Q(defensoria=defensoria)
    )

    # Obtém bloqueios dos defensores que estiverem atuando na defensoria
    q_evento &= (
        Q(defensor=None) |
        Q(defensor__in=atuacoes.values('defensor_id'))
    )

    eventos_ = Evento.objects.filter(
        q_evento
    ).order_by(
        'data_ini',
        'data_fim',
    ).values(
        'data_ini',
        'data_fim'
    )

    bloqueios = tuple(eventos_)

    # obtem os horários dos agendamentos marcados para o período
    agendamentos_index = 0
    agendamentos = tuple(AtendimentoDefensor.objects.filter(
        data_agendamento__range=[data_base, hora_limite],
        defensoria=defensoria,
        remarcado=None,
        ativo=True
    ).order_by(
        'data_agendamento'
    ).values_list('data_agendamento', flat=True))

    procurando = True
    tentativas = 0

    # procura por horários disponíveis até a data limite
    while procurando and data_base < data_limite:

        existe_substituicao = False

        # compara substituicoes enquanto não atingir o limite e enquanto for menor que a data base
        while substituicoes_index < len(substituicoes) and substituicoes[substituicoes_index]['data_inicial'].date() <= data_base:  # noqa

            # se existe uma substituicao para o dia, marca existencia e encerra loop
            if data_base <= substituicoes[substituicoes_index]['data_final'].date():
                existe_substituicao = True
                break

            # guarda índice do próximo item a ser comparado
            substituicoes_index += 1

        existe_bloqueio = False

        # compara bloqueios enquanto não atingir o limite e enquanto for menor que a data base
        while bloqueios_index < len(bloqueios) and bloqueios[bloqueios_index]['data_ini'] <= data_base:

            # se existe um bloqueio para o dia, marca existencia e encerra loop
            if data_base <= bloqueios[bloqueios_index]['data_fim']:
                existe_bloqueio = True
                break

            # guarda índice do próximo item a ser comparado
            bloqueios_index += 1

        # se nao existe bloqueio procura por agenda válida para o dia
        if not existe_bloqueio:

            for agenda in agendas:

                if agenda['data_ini'] <= data_base <= agenda['data_fim']:

                    if not existe_substituicao or agenda['substituicao']:  # trata verificao de agenda em substituicao

                        horarios = json.loads(agenda['conciliacao'])  # converte string json em objeto

                        # Obtém configurações da forma de atendimento
                        formas_atendimento = horarios.pop('forma_atendimento', None)
                        if not config.EXIBIR_PRESENCIAL_REMOTO_AGENDAMENTO:
                            formas_atendimento = None

                        # Se a categoria não foi informada, usa a primeira como base
                        if categoria_agenda:
                            categoria_agenda_horario = categoria_agenda
                        else:
                            categoria_agenda_horario = int(next(iter(horarios)))

                        dias_da_semana = horarios.get(str(categoria_agenda_horario), [])

                        weekday_de_data_base = data_base.weekday()
                        # verifica se o dia da semana eh um indice valido para o valor
                        # atual de dias_da_semana
                        if weekday_de_data_base < len(dias_da_semana):

                            if formas_atendimento:
                                forma_atendimento_dia = formas_atendimento[str(categoria_agenda_horario)][weekday_de_data_base]  # noqa
                            else:
                                forma_atendimento_dia = None

                            # Se a forma de atendimento foi informada, verifica se é a mesma do dia
                            if forma_atendimento_dia and forma_atendimento and forma_atendimento_dia != forma_atendimento[0].upper():  # noqa
                                break

                            # obtém horários da agenda do dia
                            horas = dias_da_semana[weekday_de_data_base]

                            # obtém lista de agendamentos do dia
                            agendamentos_dia = []
                            for agendamento in agendamentos:
                                if agendamento.date() == data_base and agendamento.time() != time.min:
                                    agendamentos_dia.append(agendamento)

                            conflitos = False

                            # verificação de conflito: mais agendamentos que horários disponíveis
                            if len(agendamentos_dia) >= len(horas):
                                conflitos = True
                                break

                            # verificação de conflito: horário agendado não existe mais na agenda
                            for agendamento in agendamentos_dia:
                                if len([hora for hora in horas if datetime.strptime(hora, '%H:%M').time() == agendamento.time()]) == 0:  # noqa: E501
                                    conflitos = True
                                    break

                            if conflitos:
                                break

                            # passa por todos horarios possíveis para o dia da semana
                            for hora in horas:

                                hora_base = datetime.strptime(hora, '%H:%M').time()
                                horario = datetime.combine(data_base, hora_base)
                                tentativas += 1

                                existe_agendamento = False

                                # compara horários enquanto não atingir o limite e enquanto for menor que o atual
                                while agendamentos_index < len(agendamentos) and agendamentos[agendamentos_index] <= horario:  # noqa

                                    # se existe um agendamento para horário, marca existencia e encerra loop
                                    if agendamentos[agendamentos_index] == horario:
                                        existe_agendamento = True
                                        break

                                    # guarda índice do próximo item a ser comparado
                                    agendamentos_index += 1

                                # se não existe agendamento para o horário, adiciona à lista
                                if not existe_agendamento and hora_base != extra_pauta:

                                    # tratamento de dia com conflitos de horários (mudança na agenda)
                                    conflitos = False

                                    d = {
                                        'horario': horario,
                                        'categoria_agenda': categoria_agenda_horario,
                                        'forma_atendimento': forma_atendimento_dia,
                                        'agenda_id': agenda['id'],
                                        'defensor_id': agenda['defensor_id'],
                                        'atuacao_id': agenda['atuacao_id'],
                                        'atuacao__defensor_id': agenda['atuacao__defensor_id'],
                                        'defensor_nome': agenda['defensor__servidor__nome'],
                                    }
                                    resposta.append(d)

                                    if len(resposta) == quantidade:
                                        return resposta
                                    elif dias_diferentes:
                                        break

                    break  # só confere a primeira agenda válida para o dia pois ela sobrepõe as demais

        data_base = data_base + timedelta(days=1)

    return resposta


def formata_mensagem_whatsapp_agendamento_efetuado(agendamento, incluir_documentos):
    mensagem_whatsapp = "Detalhes do Atendimento\n\n"
    mensagem_whatsapp = '{}*Número:* {}\n'.format(mensagem_whatsapp, agendamento.numero)

    if config.EXIBIR_OFICIO_AGENDAMENTO:
        mensagem_whatsapp = '{}*Atendimento Necessita de Ofício:* {}\n'.format(mensagem_whatsapp, ("SIM" if agendamento.oficio == 'yes' else "NÃO"))  # noqa: E501

    if agendamento.extra:
        mensagem_whatsapp = '{}*Agendado para:* {:%d/%m/%Y}\n'.format(mensagem_whatsapp, agendamento.data_agendamento)  # noqa: E501
    else:
        mensagem_whatsapp = '{}*Agendado para:* {:%d/%m/%Y %H:%M}\n'.format(mensagem_whatsapp, agendamento.data_agendamento)  # noqa: E501

    if config.WHATSAPP_INCLUIR_NOME_DEFENSOR:
        mensagem_whatsapp = '{}*Defensor:* {} *Pauta*\n'.format(mensagem_whatsapp, agendamento.defensor)

    if agendamento.defensoria.nucleo:
        mensagem_whatsapp = '{}*Núcleo:* {}\n'.format(mensagem_whatsapp, agendamento.defensoria.nucleo)
    else:
        mensagem_whatsapp = '{}*Defensoria:* {}\n'.format(mensagem_whatsapp, agendamento.defensoria)

    mensagem_whatsapp = '{}*Telefone da Unidade:* {}\n'.format(mensagem_whatsapp, (agendamento.defensoria.telefone if agendamento.defensoria.telefone is not None else "Não informado"))  # noqa: E501

    if agendamento.defensoria.predio and agendamento.defensoria.predio.endereco:
        mensagem_whatsapp = '{}*Endereço:* {}\n'.format(mensagem_whatsapp, agendamento.defensoria.predio.endereco)
    else:
        mensagem_whatsapp = '{}*Endereço:* {}\n'.format(mensagem_whatsapp, 'Não informado')

    mensagem_whatsapp = '{}*Área/Pedido:* {}/{}\n'.format(mensagem_whatsapp, agendamento.qualificacao.area, agendamento.qualificacao)  # noqa: E501

    if incluir_documentos and agendamento.qualificacao.documentos:
        mensagem_whatsapp = '{}*Documentos:*\n{}\n'.format(mensagem_whatsapp, agendamento.qualificacao.documentos.replace('•', '\n\n•'))  # noqa: E501

    return mensagem_whatsapp.replace('\n', '%0a')


def formata_mensagem_whatsapp_procedimentos_efetuados(ligacao, incluir_documentos):
    mensagem_whatsapp = "Procedimentos efetuados\n\n"

    for procedimento in ligacao.get_procedimentos():
        if procedimento.tipo == procedimento.TIPO_ENCAMINHAMENTO:
            mensagem_whatsapp += '{}*: {}\n'.format(procedimento.get_tipo_display(), procedimento.encaminhamento)  # noqa: E501
        elif procedimento.tipo == procedimento.TIPO_INFORMACAO:
            mensagem_whatsapp += '{}*: {}\n'.format(procedimento.get_tipo_display(), procedimento.informacao)  # noqa: E501
        elif procedimento.tipo == procedimento.TIPO_INFORMACAO_ASSISTIDO:
            mensagem_whatsapp += '{}*\n'.format(procedimento.get_tipo_display())
        elif procedimento.tipo == procedimento.TIPO_RECLAMACAO:
            mensagem_whatsapp += '{}*: A Reclamação foi enviada para a corregedoria\n'.format(procedimento.get_tipo_display())  # noqa: E501
        else:
            mensagem_whatsapp += formata_mensagem_whatsapp_agendamento_efetuado(procedimento.agendamento, incluir_documentos)

    return mensagem_whatsapp.replace('\n', '%0a')
