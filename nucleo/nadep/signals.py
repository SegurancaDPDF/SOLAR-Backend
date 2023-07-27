# -*- coding: utf-8 -*-

# Bibliotecas de terceiros
from django.db.models.signals import post_save, pre_save
from django.dispatch.dispatcher import receiver

# Modulos locais
from .models import Aprisionamento, Prisao, Historico, Atendimento, Soltura, MudancaRegime, Falta, PenaRestritiva, \
    CalculoExecucaoPenal


# funcão decorada para o Signal pre_save do modelo Prisao
@receiver(pre_save, sender=Prisao)
def pre_save_prisao(sender, instance, **kwargs):
    # define o tipo da prisão com base na função get_tipo() do modelo Prisao
    instance.tipo = instance.get_tipo()
    # define o regime atual como o regime inicial, caso o regime atual seja None
    if instance.regime_atual is None:
        instance.regime_atual = instance.regime_inicial


# funcão decorada para o Signal post_save do modelo Prisao
@receiver(post_save, sender=Prisao)
def post_save_prisao_ev_conversao(sender, instance, **kwargs):
    # verifica se a prisão possui origem diferente e penalidade diferente
    if instance.origem and instance.origem.pena != instance.pena:
        # busca o evento de conversão no histórico
        ev_prisao = instance.origem.eventos.filter(evento=Historico.EVENTO_CONVERSAO).first()
        # caso o evento de conversão não exista, cria um novo objeto Historico
        if not ev_prisao:
            ev_prisao = Historico(
                pessoa=instance.pessoa,
                evento=Historico.EVENTO_CONVERSAO,
                cadastrado_por=instance.cadastrado_por)
        # monta o histórico com informações relevantes da prisão original
        historico = u'Processo: <b>{}</b><br/>' \
                    u'Tipificação: <b>{}</b><br/>' \
                    u'Pena Privativa: <b>{}a{}m{}d ({} dias-multa)</b><br/>' \
                    u'Restrições:</b><br/><ul>'.format(
                        instance.processo.numero,
                        instance.tipificacao.nome,
                        instance.origem.duracao_pena_anos,
                        instance.origem.duracao_pena_meses,
                        instance.origem.duracao_pena_dias,
                        instance.origem.multa)
        # adiciona as restrições ao histórico
        for restricao in instance.penarestritiva_set.filter(ativo=True):
            historico += u'<li>{}</li>'.format(
                dict(PenaRestritiva.LISTA_RESTRICAO)[restricao.restricao]
            )

        historico += u'</ul>'
        # configura o evento de conversão
        ev_prisao.data_registro = instance.origem.data_sentenca_condenatoria
        ev_prisao.historico = historico
        ev_prisao.save()

        instance.origem.eventos.add(ev_prisao)


# funcão decorada para o Signal post_save do modelo Prisao
@receiver(post_save, sender=Prisao)
def post_save_prisao(sender, instance, **kwargs):
    # verifica o tipo de prisão e busca o aprisionamento correspondente
    if instance.tipo == Prisao.TIPO_PROVISORIO:
        aprisionamento = Aprisionamento.objects.filter(
            prisao=instance,
            ativo=True
        ).first()
    else:
        aprisionamento = Aprisionamento.objects.filter(
            prisao__tipo=Prisao.TIPO_CONDENADO,
            prisao__pessoa=instance.pessoa,
            ativo=True
        ).first()

    # caso não exista aprisionamento, cria um novo e salva os dados
    if not aprisionamento and instance.estabelecimento_penal:
        aprisionamento = Aprisionamento(
            prisao=instance,
            estabelecimento_penal=instance.estabelecimento_penal,
            data_inicial=instance.data_prisao,
            origem_cadastro=Aprisionamento.ORIGEM_PRISAO,
            ativo=True)

    # se o aprisionamento existe, atualiza a data final em caso de prisão provisória e salva os dados
    if aprisionamento:
        if instance.tipo == Prisao.TIPO_PROVISORIO and instance.resultado_sentenca:
            aprisionamento.data_final = instance.data_sentenca_condenatoria
        aprisionamento.save()


# funcão decorada para o Signal post_save do modelo Prisao
@receiver(post_save, sender=Prisao)
def post_save_prisao_ev_prisao(sender, instance, **kwargs):
    # verifica se a prisão possui data de prisão, processo e estabelecimento penal associado
    if instance.data_prisao and instance.processo and instance.estabelecimento_penal:

        ev_prisao = instance.eventos.filter(evento=Historico.EVENTO_PRISAO).first()

        if not ev_prisao:
            ev_prisao = Historico(
                pessoa=instance.pessoa,
                evento=Historico.EVENTO_PRISAO,
                cadastrado_por=instance.cadastrado_por)

        # monta o histórico com informações relevantes da prisão
        ev_prisao.data_registro = instance.data_prisao
        ev_prisao.historico = u'Preso em: <b>{}</b><br/>Processo: <b>{}</b><br/>Tipificação: <b>{}</b>'.format(
            instance.estabelecimento_penal.nome,
            instance.processo.numero,
            instance.tipificacao.nome)

        ev_prisao.save()
        instance.eventos.add(ev_prisao)


@receiver(post_save, sender=Prisao)
def post_save_prisao_ev_condenacao(sender, instance, **kwargs):

    if instance.processo \
            and instance.resultado_sentenca == Prisao.SENTENCA_CONDENADO \
            and instance.data_sentenca_condenatoria \
            and instance.pena == Prisao.PENA_PRIVATIVA:

        ev_condenacao = instance.eventos.filter(evento=Historico.EVENTO_CONDENACAO).first()

        if not ev_condenacao:
            ev_condenacao = Historico(
                pessoa=instance.pessoa,
                evento=Historico.EVENTO_CONDENACAO,
                cadastrado_por=instance.cadastrado_por)

        historico = u'Processo: <b>{}</b><br/>' \
                    u'Tipificação: <b>{}</b><br/>' \
                    u'Pena: <b>{}a{}m{}d ({} dias-multa)</b><br/>' \
                    u'Regime Inicial: <b>{}</b><br/>' \
                    u'Fração para Progressão de Regime: <b>{}</b><br/>' \
                    u'Fração para Livramento Condicional: <b>{}</b><br/>'.format(
                        instance.processo.numero,
                        instance.tipificacao.nome,
                        instance.duracao_pena_anos,
                        instance.duracao_pena_meses,
                        instance.duracao_pena_dias,
                        instance.multa,
                        Prisao.LISTA_REGIME[instance.regime_inicial][1] if instance.regime_inicial else None,
                        dict(Prisao.TIPO_LISTA_PR)[instance.fracao_pr] if instance.fracao_pr else None,
                        dict(Prisao.TIPO_LISTA_LC)[instance.fracao_lc] if instance.fracao_lc else None)

        ev_condenacao.data_registro = instance.data_sentenca_condenatoria
        ev_condenacao.historico = historico
        ev_condenacao.save()

        instance.eventos.add(ev_condenacao)


@receiver(pre_save, sender=Aprisionamento)
def pre_save_aprisionamento(sender, instance, **kwargs):

    if instance.prisao.tipo == Prisao.TIPO_PROVISORIO:
        instance.detracao = True


@receiver(post_save, sender=Aprisionamento)
def post_save_aprisionamento(sender, instance, **kwargs):

    if instance.prisao.tipo == Prisao.TIPO_PROVISORIO:
        aprisionamentos = Aprisionamento.objects.filter(
            prisao=instance.prisao,
        )
    else:
        aprisionamentos = Aprisionamento.objects.filter(
            prisao__tipo=Prisao.TIPO_CONDENADO,
            prisao__pessoa=instance.prisao.pessoa,
        )

    aprisionamentos = aprisionamentos.filter(
        data_inicial__lt=instance.data_inicial,
        data_final=None,
        ativo=True
    ).exclude(
        id=instance.id
    )

    for aprisionamento in aprisionamentos:

        aprisionamento.data_final = instance.data_inicial
        aprisionamento.situacao = Aprisionamento.SITUACAO_TRANSFERIDO
        aprisionamento.save()

        evento = instance.eventos.filter(evento=Historico.EVENTO_TRANSFERENCIA).first()

        if not evento:
            evento = Historico(
                pessoa=instance.prisao.pessoa,
                evento=Historico.EVENTO_TRANSFERENCIA,
                cadastrado_por=instance.cadastrado_por)

        historico = u'Processo: <b>{}</b><br/>' \
                    u'Origem: <b>{}</b><br/>' \
                    u'Destino: <b>{}</b><br/>' \
                    u'Observações: <b>{}</b><br/>'.format(
                        instance.prisao.processo,
                        aprisionamento.estabelecimento_penal,
                        instance.estabelecimento_penal,
                        instance.historico)

        evento.data_registro = aprisionamento.data_final
        evento.historico = historico
        evento.save()

        instance.eventos.add(evento)


@receiver(post_save, sender=Atendimento)
def post_save_atendimento_ev_visita(sender, instance, **kwargs):
    # funcão para registrar um evento de visita no histórico, caso o atendimento seja do tipo visita

    if instance.tipo == Atendimento.TIPO_VISITA:

        evento = instance.eventos.filter(evento=Historico.EVENTO_VISITA).first()

        if not evento:
            evento = Historico(
                pessoa=instance.prisao.pessoa,
                evento=Historico.EVENTO_VISITA,
                cadastrado_por=instance.cadastrado_por)

        historico = u'Local: <b>{}</b><br/>' \
                    u'Defensoria: <b>{}</b><br/>' \
                    u'Defensor: <b>{}</b><br/>' \
                    u'Área/Pedido: <b>{}/{}</b><br/>'.format(
                        instance.estabelecimento_penal,
                        instance.defensoria,
                        instance.defensor,
                        instance.qualificacao.area,
                        instance.qualificacao.titulo)

        evento.data_registro = instance.data_atendimento
        evento.historico = historico
        evento.save()

        instance.eventos.add(evento)


@receiver(post_save, sender=Atendimento)
def post_save_atendimento_ev_atendimento(sender, instance, **kwargs):
    # funcão para registrar um evento de atendimento no histórico, caso o atendimento não seja do tipo visita

    if instance.tipo != Atendimento.TIPO_VISITA and instance.data_atendimento:

        evento = instance.eventos.filter(evento=Historico.EVENTO_ATENDIMENTO).first()

        if not evento:
            evento = Historico(
                pessoa=instance.requerente.pessoa,
                evento=Historico.EVENTO_ATENDIMENTO,
                cadastrado_por=instance.atendido_por)

        qualificacao = 'Não informado'
        if instance.qualificacao:
            qualificacao = '{}/{}'.format(
                instance.qualificacao.area,
                instance.qualificacao.titulo
            )

        historico = u'Defensoria: <b>{}</b><br/>' \
                    u'Defensor: <b>{}</b><br/>' \
                    u'Área/Pedido: <b>{}</b><br/>' \
                    u'Interessado: <b>{}</b><br/>'.format(
                        instance.defensoria,
                        instance.defensor,
                        qualificacao,
                        instance.interessado)

        evento.data_registro = instance.data_atendimento
        evento.historico = historico
        evento.save()

        instance.eventos.add(evento)


@receiver(post_save, sender=Soltura)
def post_save_soltura_ev(sender, instance, **kwargs):
    # funcão para registrar um evento de soltura no histórico, quando uma soltura é realizada

    evento = instance.aprisionamento.eventos.filter(evento=Historico.EVENTO_SOLTURA).first()

    if not evento:
        evento = Historico(
            pessoa=instance.aprisionamento.prisao.pessoa,
            evento=Historico.EVENTO_SOLTURA,
            cadastrado_por=instance.cadastrado_por)

    historico = u'Processo: <b>{}</b><br/>' \
                u'Tipo: <b>{}</b><br/>' \
                u'Observações: <b>{}</b><br/>'.format(
                    instance.processo,
                    dict(Soltura.LISTA_TIPO)[int(instance.tipo)] if instance.tipo else None,
                    instance.historico)

    evento.data_registro = instance.aprisionamento.data_final
    evento.historico = historico
    evento.ativo = instance.ativo
    evento.save()

    instance.aprisionamento.eventos.add(evento)


@receiver(pre_save, sender=MudancaRegime)
def pre_save_mudanca_regime_ev(sender, instance, **kwargs):
    # funcão para registrar um evento de mudança de regime no histórico, antes de salvar a mudança de regime.

    if instance.tipo == MudancaRegime.TIPO_PROGRESSAO:
        tipo = Historico.EVENTO_PROGRESSAO
    else:
        tipo = Historico.EVENTO_REGRESSAO

    if instance.evento:
        evento = instance.evento
    else:
        evento = Historico(
            pessoa=instance.prisao.pessoa,
            cadastrado_por=instance.cadastrado_por)

    historico = u'Processo: <b>{}</b><br/>' \
                u'Nova Data Base: <b>{:%d/%m/%Y}</b><br/>' \
                u'Novo Regime: <b>{}</b><br/>' \
                u'Observações: <b>{}</b><br/>'.format(
                    instance.prisao.processo,
                    instance.data_base,
                    dict(Prisao.LISTA_REGIME)[int(instance.regime)],
                    instance.historico)

    evento.evento = tipo
    evento.data_registro = instance.data_registro
    evento.historico = historico
    evento.save()

    instance.evento = evento


@receiver(pre_save, sender=Falta)
def pre_save_falta_ev(sender, instance, **kwargs):
    # funcão para registrar um evento de falta no histórico, antes de salvar a falta

    if instance.evento:
        evento = instance.evento
    else:
        evento = Historico(
            pessoa=instance.pessoa,
            evento=Historico.EVENTO_FALTA,
            cadastrado_por=instance.cadastrado_por)

    historico = u'PAD: <b>{}</b><br/>' \
                u'Resultado: <b>{}</b><br/>' \
                u'Observações: <b>{}</b><br/>'.format(
                    instance.numero_pad,
                    dict(Falta.LISTA_RESULTADO)[int(instance.resultado)],
                    instance.observacao)

    evento.data_registro = instance.data_fato
    evento.historico = historico
    evento.save()

    instance.evento = evento


@receiver(pre_save, sender=CalculoExecucaoPenal)
def pre_save_calculo_execucao_penal(sender, instance, **kwargs):
    # funcão para atualizar informações em um cálculo de execução penal antes de salvá-lo

    instance.pessoa_nome = instance.pessoa.nome
    instance.execucao_numero = instance.execucao.numero
    instance.estabelecimento_penal_nome = instance.estabelecimento_penal.nome
    instance.atualizado_por_nome = instance.atualizado_por.nome
