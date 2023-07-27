# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
import reversion

# Solar
import calendar
from datetime import date, timedelta, datetime
from django.db.models import Q, Min, Sum, Max
from atendimento.atendimento.models import Pessoa as AtendimentoPessoa
from atendimento.atendimento.models import Atendimento
from contrib.models import Util
from nucleo.nadep.models import Prisao as DbPrisao, Aprisionamento, Remissao, Interrupcao, CalculoExecucaoPenal
from nucleo.nadep.models import EstabelecimentoPenal
from processo.processo.models import Parte


class AnoMesDia(object):
    # utilizada para realizar cálculos envolvendo intervalos de tempo
    MOD_ANO = 360
    MOD_MES = 30

    def __init__(self, ano=0, mes=0, dia=0, mod_ano=MOD_ANO, mod_mes=MOD_MES):
        # inicializa a classe AnoMesDia com valores de anos, meses e dias
        self.MOD_ANO = mod_ano
        self.MOD_MES = mod_mes

        ano = int(ano) if ano else 0
        mes = int(mes) if mes else 0
        dia = int(dia) if dia else 0

        self.mes, self.dia = divmod(dia, self.MOD_MES)
        self.ano, self.mes = divmod(self.mes + mes, 12)
        self.ano += ano

    def __add__(self, other):
        # sobrecarga do operador + para realizar a soma de dois objetos AnoMesDia
        total = self.dias() + other.dias()
        anos, total = divmod(total, self.MOD_ANO)
        meses, dias = divmod(total, self.MOD_MES)

        return AnoMesDia(anos, meses, dias)

    def __sub__(self, other):
        # sobrecarga do operador - para realizar a subtração de dois objetos AnoMesDia.
        total = self.dias() - other.dias()

        if total > 0:
            anos, total = divmod(total, self.MOD_ANO)
            meses, dias = divmod(total, self.MOD_MES)
        else:
            anos, meses, dias = 0, 0, 0

        return AnoMesDia(anos, meses, dias)

    def __str__(self):  # sobrecarga do método str para representar o objeto como uma string formatada
        return '{0}a{1}m{2}d'.format(self.ano, self.mes, self.dia)

    def dias(self):  # retorna a quantidade total de dias representada pelo objeto AnoMesDia
        return self.ano * self.MOD_ANO + self.mes * self.MOD_MES + self.dia

    def somarData(self, data_base):
        # soma o período de tempo representado pelo objeto AnoMesDia a uma data base
        meses, dias = divmod(data_base.day + self.dia, self.MOD_MES)
        anos, meses = divmod(data_base.month + self.mes + meses, 12)
        anos += data_base.year + self.ano

        if dias <= 0:
            dias = self.MOD_MES
            meses -= 1

        if meses <= 0:
            meses = 12
            anos -= 1

        dia_semana, dias_mes = calendar.monthrange(anos, meses)

        if dias > dias_mes:
            return date(anos, meses, dias_mes) + timedelta(days=(dias-dias_mes))
        else:
            return date(anos, meses, dias)

    def subtrairData(self, data_base):
        # subtrai o período de tempo representado pelo objeto AnoMesDia de uma data base
        dia = data_base.day - self.dia
        mes = data_base.month - self.mes
        ano = data_base.year - self.ano

        while dia <= 0:
            mes -= 1
            dia = self.MOD_MES + dia

        while mes <= 0:
            ano -= 1
            mes = 12 + mes

        dia_semana, dias_mes = calendar.monthrange(ano, mes)

        if dia > dias_mes:
            return date(ano, mes, dias_mes) - timedelta(days=(dia-dias_mes))
        else:
            return date(ano, mes, dia)

    def to_dict(self):  # retorna um dicionário contendo os valores de anos, meses e dias
        return {'anos': self.ano, 'meses': self.mes, 'dias': self.dia}

    @staticmethod
    def calcular_diff_data(ini, fim):
        # calcula a diferença de tempo entre duas datas, representando o resultado em AnoMesDia
        if ini is None or fim is None:
            return AnoMesDia()

        if fim < ini:
            return AnoMesDia()

        ano = fim.year - ini.year

        if fim.month == ini.month and fim.day < ini.day:
            ano -= 1

        if fim.month < ini.month:
            ano -= 1
            mes = fim.month + 12 - ini.month
        else:
            mes = fim.month - ini.month

        if fim.day < ini.day:
            mes -= 1
            dia = fim.day + 30 - ini.day
        else:
            dia = fim.day - ini.day

        return AnoMesDia(ano, mes, dia)


class Preso(object):
    def __init__(self, pessoa, data_base=date.today()):
        # classe que representa um prisioneiro e realiza cálculos relacionados a sua pena e aprisionamentos
        self.pessoa = pessoa
        self.data_base = data_base

        self.prisoes = DbPrisao.objects.filter(
            Q(pessoa=self.pessoa) &
            Q(ativo=True) &
            Q(data_baixa=None) &
            (
                (
                    Q(tipo=DbPrisao.TIPO_PROVISORIO) &
                    Q(resultado_sentenca=None)
                ) |
                (
                    Q(tipo=DbPrisao.TIPO_CONDENADO) &
                    Q(data_liquidacao=None) &
                    ~Q(originada__pena=DbPrisao.PENA_RESTRITIVA)
                )
            )
        ).order_by('-data_prisao')

    def data_prisao_definitiva(self):  # retorna a data da primeira prisão definitiva do prisioneiro
        return self.prisoes_condenado().aggregate(menor_data=Min('data_prisao'))['menor_data']

    def data_ultima_prisao(self):  # retorna a data da última prisão do prisioneiro
        return self.prisoes_condenado().aggregate(maior_data=Max('data_prisao'))['maior_data']

    def calcular_data_termino_pena(self):
        # calcula a data estimada do término da pena do prisioneiro
        data_prisao_definitiva = self.data_prisao_definitiva()

        if not data_prisao_definitiva:
            return None

        total_pena = self.calcular_duracao_total_pena()
        total_detracoes = self.calcular_total_detracoes()
        total_interrupcoes = self.calcular_total_interrupcoes()

        data_termino = total_pena.somarData(data_prisao_definitiva)
        data_termino = total_detracoes.subtrairData(data_termino)
        data_termino = total_interrupcoes.somarData(data_termino)
        data_termino -= timedelta(days=self.total_remissoes())
        data_termino -= timedelta(days=1)

        return data_termino

    def calcular_pena_restante(self, data_base=date.today()):
        # calcula o tempo de pena restante do prisioneiro a partir de uma data base
        data_termino = self.calcular_data_termino_pena()

        if data_base and data_termino:
            return AnoMesDia.calcular_diff_data(data_base, data_termino)
        else:
            return AnoMesDia()

    def pena_restante(self, data_base=date.today()):
        # retorna o tempo de pena restante do prisioneiro em anos, meses e dias
        return self.calcular_pena_restante(data_base).to_dict()

    def calcular_pena_cumprida(self, ini, fim):
        # calcula o tempo de pena cumprida do prisioneiro entre duas datas
        if ini and fim:
            total = AnoMesDia.calcular_diff_data(ini, fim - timedelta(days=1))
            total = total - self.calcular_total_interrupcoes()
            total = total + self.calcular_total_detracoes()
            total = total + AnoMesDia(0, 0, self.total_remissoes())
        else:
            total = AnoMesDia()

        return total

    def calcular_pena_cumprida_pr(self, ini=None, fim=None, detracoes=False):
        # calcula o tempo de pena cumprida do prisioneiro entre duas datas, incluindo detrações
        if not ini:
            ini = self.data_prisao_definitiva()

        if not fim:
            fim = self.data_base + timedelta(days=1)

        if ini and fim:

            total = AnoMesDia.calcular_diff_data(ini, fim - timedelta(days=1))
            total = total - self.calcular_total_interrupcoes()
            total = total + AnoMesDia(dia=self.total_remissoes_pr(False))

            if detracoes:
                total = total + self.calcular_total_detracoes()

        else:

            total = AnoMesDia()

        return total

    def pena_cumprida(self, data_base=date.today()):
        # retorna o tempo de pena cumprida do prisioneiro até a data base, juntamente com as datas de início e fim
        ini = self.data_prisao_definitiva()
        fim = data_base

        if ini and fim:
            total = self.calcular_pena_cumprida(ini, fim + timedelta(days=1))
        else:
            total = AnoMesDia()

        return {'anos': total.ano, 'meses': total.mes, 'dias': total.dia, 'data_ini': ini, 'data_fim': fim}

    def partes(self):  # retorna as partes relacionadas ao prisioneiro
        return Parte.objects.filter(
            (
                Q(atendimento__partes__pessoa=self.pessoa) |
                Q(atendimento__inicial__partes__pessoa=self.pessoa)
            ) &
            Q(ativo=True)
        ).distinct()

    @property
    def prisao_principal(self):
        # retorna a prisão principal do prisioneiro (primeira prisão condenada ou provisória)
        prisao_condenado = self.prisoes_condenado().order_by('data_prisao').first()

        if prisao_condenado:
            return prisao_condenado
        else:
            return self.prisoes_provisorio().order_by('data_prisao').first()

    def prisoes_inativas(self):  # retorna as prisões inativas do prisioneiro
        return DbPrisao.objects.filter(
            Q(pessoa=self.pessoa) &
            Q(ativo=True) &
            (
                ~Q(data_baixa=None) |
                (
                    Q(tipo=DbPrisao.TIPO_PROVISORIO) & ~Q(resultado_sentenca=None)
                ) |
                (
                    Q(tipo=DbPrisao.TIPO_CONDENADO) &
                    (
                        ~Q(data_liquidacao=None) |
                        Q(originada__pena=DbPrisao.PENA_RESTRITIVA)
                    )
                )
            )
        ).order_by('-data_prisao')

    def prisoes_condenado(self):  # retorna as prisões condenadas e ativas do prisioneiro
        return DbPrisao.objects.filter(
            Q(pessoa=self.pessoa) &
            Q(ativo=True) &
            Q(tipo=DbPrisao.TIPO_CONDENADO) &
            Q(data_baixa=None) &
            Q(data_liquidacao=None) &
            ~Q(originada__pena=DbPrisao.PENA_RESTRITIVA)
        ).order_by('data_prisao', 'data_fato')

    def prisoes_provisorio(self):  # retorna as prisões provisórias do prisioneiro
        return self.prisoes.filter(tipo=DbPrisao.TIPO_PROVISORIO)

    def calcular_duracao_total_pena(self):
        # calcula a duração total da pena do prisioneiro em anos, meses e dias
        duracao = self.prisoes_condenado().aggregate(anos=Sum('duracao_pena_anos'),
                                                     meses=Sum('duracao_pena_meses'),
                                                     dias=Sum('duracao_pena_dias'))

        if duracao['dias']:
            meses, dias = divmod(duracao['dias'], 30)
        else:
            meses, dias = 0, 0

        if duracao['meses']:
            anos, meses = divmod(duracao['meses'] + meses, 12)
        else:
            anos = 0

        if duracao['anos']:
            anos += duracao['anos']

        return AnoMesDia(anos, meses, dias)

    def duracao_total_pena(self):  # retorna a duração total da pena do prisioneiro em anos, meses e dias
        return self.calcular_duracao_total_pena().to_dict()

    def is_solto(self):  # verifica se o prisioneiro está solto, ou seja, não possui prisões ativas
        return not Aprisionamento.objects.filter(prisao__pessoa=self.pessoa, data_final=None, ativo=True).exists()

    def estabelecimento_penal_atual(self):
        # retorna o estabelecimento penal atual do prisioneiro
        prisoes = Aprisionamento.objects.filter(
            prisao__pessoa=self.pessoa, data_final=None, ativo=True
        ).order_by('-data_inicial')[:1]

        if prisoes:
            return prisoes[0].estabelecimento_penal
        elif self.prisoes:
            return self.prisoes[0].estabelecimento_penal
        else:
            return None

    def aprisionamentos(self):  # retorna os aprisionamentos do prisioneiro(aprisionamentos associados a prisões ativas)
        return Aprisionamento.objects.filter(
            prisao__pessoa=self.pessoa,
            ativo=True
        ).order_by('data_inicial')

    def total_aprisionamentos(self):  # retorna o tempo total de aprisionamentos do prisioneiro em anos, meses e dias
        return self.calcular_total_aprisionamentos().to_dict()

    def calcular_total_aprisionamentos(self):
        # calcula o tempo total de aprisionamentos do prisioneiro em anos, meses e dias
        total = AnoMesDia(0, 0, 0)

        for prisao in self.aprisionamentos():
            dt_final = (prisao.data_final if prisao.data_final else datetime.now()) + timedelta(days=1)
            valor = AnoMesDia.calcular_diff_data(prisao.data_inicial, dt_final)
            total += valor

        return total

    def detracoes(self):  # retorna as detrações associadas ao prisioneiro
        if self.data_prisao_definitiva():
            return Aprisionamento.objects.filter(
                prisao__pessoa=self.pessoa,
                data_final__lte=self.data_prisao_definitiva(),
                ativo=True)
        else:
            return Aprisionamento.objects.none()

    def total_detracoes(self):  # retorna o tempo total de detrações do prisioneiro em anos, meses e dias
        return self.calcular_total_detracoes().to_dict()

    def calcular_total_detracoes(self):
        # calcula o tempo total de detrações do prisioneiro em anos, meses e dias
        total = AnoMesDia(0, 0, 0)

        for detracao in self.detracoes():
            dt_final = detracao.data_final + timedelta(days=1)
            valor = AnoMesDia.calcular_diff_data(detracao.data_inicial, dt_final)
            total += valor

        return total

    def interrupcoes(self):  # retorna as interrupções associadas ao prisioneiro
        if self.data_prisao_definitiva():
            return Interrupcao.objects.filter(
                pessoa=self.pessoa,
                data_inicial__gte=self.data_prisao_definitiva(),
                ativo=True)
        else:
            return Interrupcao.objects.none()

    def total_interrupcoes(self):  # retorna o tempo total de interrupções do prisioneiro em anos, meses e dias
        return self.calcular_total_interrupcoes().to_dict()

    def calcular_total_interrupcoes(self):
        # calcula o tempo total de interrupções do prisioneiro em anos, meses e dias
        hoje = date.today()
        total = AnoMesDia(0, 0, 0)

        for interrupcao in self.interrupcoes():
            dt_final = hoje
            if interrupcao.data_final:
                dt_final = interrupcao.data_final
            valor = AnoMesDia.calcular_diff_data(interrupcao.data_inicial, dt_final)
            total += valor

        return total

    def total_remissoes(self):
        total = Remissao.objects.filter(pessoa=self.pessoa, ativo=True).aggregate(total=Sum('dias_remissao'))['total']
        return int(round(float(total))) if total else 0

    def total_remissoes_pr(self, para_progressao=True):
        total = Remissao.objects.filter(
            pessoa=self.pessoa,
            para_progressao=para_progressao,
            ativo=True
        ).aggregate(total=Sum('dias_remissao'))['total']
        return int(round(float(total))) if total else 0

    def calcular_fracoes_progressao_regime(self):

        # recupera lista de fracoes para PR
        fracoes = dict(DbPrisao.LISTA_PR)

        # gera objeto para calculos das fracoes
        for fracao in fracoes:
            fracoes[fracao] = Fracao(fracao)

        # adiciona cada prisao na respectiva fracao
        for prisao in self.prisoes_condenado().exclude(fracao_pr=None):
            fracoes[prisao.get_fracao_pr].prisoes.append(prisao)

        # desconta pena cumprida das fracoes - mais pesadas primeiro
        pena_cumprida = self.calcular_pena_cumprida_pr()
        interrupcoes = self.calcular_total_interrupcoes()
        data_base = self.data_base

        for fr in sorted(fracoes, key=lambda x: x, reverse=True):
            fracao = fracoes[fr]
            for prisao in fracao.prisoes:
                if prisao.data_prisao and prisao.data_prisao < data_base:
                    fracao.pena_cumprida += AnoMesDia.calcular_diff_data(prisao.data_prisao, data_base)
                    if interrupcoes.dias() > fracao.pena_cumprida.dias():
                        interrupcoes -= fracao.pena_cumprida
                        fracao.pena_cumprida = AnoMesDia()
                    else:
                        fracao.pena_cumprida -= interrupcoes
                        interrupcoes = AnoMesDia()
                    pena_cumprida -= fracao.pena_cumprida
                data_base = prisao.data_prisao

        # desconta remicoes das fracoes - mais leves primeiro
        total_remissoes = AnoMesDia(dia=self.total_remissoes_pr(False))

        for fr in sorted(fracoes, key=lambda x: x, reverse=False):
            fracao = fracoes[fr]
            dif_penas = fracao.dif_penas()
            if dif_penas.dias() < total_remissoes.dias():
                fracao.pena_cumprida += dif_penas
                total_remissoes -= dif_penas
            else:
                fracao.pena_cumprida += total_remissoes
                total_remissoes = AnoMesDia()

        return fracoes

    def calcular_soma_pena_cumprida_progressao_regime(self):

        fracoes = self.calcular_fracoes_progressao_regime()
        soma = AnoMesDia()

        for fracao in fracoes:
            soma += fracoes[fracao].pena_cumprida

        return soma

    def calcular_soma_fracoes_progressao_regime(self):

        fracoes = self.calcular_fracoes_progressao_regime()
        soma = AnoMesDia()

        for fracao in fracoes:
            soma += fracoes[fracao].calculo_pr()

        return soma

    # ordena mais pesados primeiro
    # ordena mais velhos primeiro
    # desconta tempo cumprido nos mais pesados (data_base - data_inicial)
    # o que sobrar vai descontando dos proximos pesos, se data_inicial_peso_atual < data_inicial_peso_anterior...
    def calcular_data_progressao_regime(self):

        if not self.data_prisao_definitiva():
            return None

        soma_fraces = self.calcular_soma_fracoes_progressao_regime()
        remissoes = self.total_remissoes_pr(True)
        detracoes = self.calcular_total_detracoes()

        data_progressao = soma_fraces.somarData(self.data_base)
        data_progressao = detracoes.subtrairData(data_progressao)
        data_progressao -= timedelta(days=remissoes)
        data_progressao -= timedelta(days=1)

        return data_progressao

    def calcular_fracoes_livramento_condicial(self):

        # recupera lista de fracoes para LC
        fracoes = dict(DbPrisao.LISTA_LC)

        # gera objeto para calculos das fracoes
        for fracao in fracoes:
            fracoes[fracao] = Fracao(fracao)

        # adiciona cada prisao na respectiva fracao
        for prisao in self.prisoes_condenado().exclude(fracao_lc=None):
            fracoes[prisao.get_fracao_lc].prisoes.append(prisao)

        for fr in sorted(fracoes, key=lambda x: x, reverse=True):
            fracao = fracoes[fr]

        return fracoes

    def calcular_soma_fracoes_livramento_condicional(self):

        data_base = self.data_prisao_definitiva()
        soma = AnoMesDia()

        if not data_base:
            return soma

        fracoes = self.calcular_fracoes_livramento_condicial()

        for fr in fracoes:
            fracao = fracoes[fr]
            for prisao in fracao.prisoes:
                pena_imposta = AnoMesDia(prisao.duracao_pena_anos, prisao.duracao_pena_meses, prisao.duracao_pena_dias)
                fracao_imposta = AnoMesDia() + AnoMesDia(0, 0, int(pena_imposta.dias() * float(fr)))
                pena_cumprida = AnoMesDia.calcular_diff_data(prisao.data_prisao, data_base)
                fracao_restante = fracao_imposta - pena_cumprida
                soma += fracao_restante

        return soma

    def calcular_data_livramento_condicial(self):

        data_base = self.data_prisao_definitiva()

        if not data_base:
            return None

        soma_fracoes = self.calcular_soma_fracoes_livramento_condicional()
        interrupcoes = self.calcular_total_interrupcoes()
        detracoes = self.calcular_total_detracoes()
        remissoes = self.total_remissoes()

        data_livramento = soma_fracoes.somarData(data_base)
        data_livramento = interrupcoes.somarData(data_livramento)
        data_livramento = detracoes.subtrairData(data_livramento)
        data_livramento -= timedelta(days=remissoes)
        data_livramento -= timedelta(days=1)

        return data_livramento

    @reversion.create_revision(atomic=False)
    def salvar_calculo(self, cadastrado_por):

        calculo = CalculoExecucaoPenal.objects.filter(pessoa=self.pessoa).first()
        guia = self.prisoes_condenado().first()

        if guia and guia.estabelecimento_penal:

            novo = calculo is None

            if not calculo and guia.processo:
                calculo = CalculoExecucaoPenal(pessoa=self.pessoa, execucao=guia.processo)

            if calculo:

                calculo.regime_atual = guia.regime_atual if guia.regime_atual else guia.regime_inicial
                calculo.estabelecimento_penal = guia.estabelecimento_penal

                calculo.data_base = self.data_base
                calculo.data_progressao = self.calcular_data_progressao_regime()
                calculo.data_livramento = self.calcular_data_livramento_condicial()
                calculo.data_termino = self.calcular_data_termino_pena()

                calculo.total_pena = self.calcular_duracao_total_pena()
                calculo.total_detracoes = self.calcular_total_detracoes()
                calculo.total_interrupcoes = self.calcular_total_interrupcoes()
                calculo.total_remissoes = self.total_remissoes()

                calculo.pena_cumprida_data_base = self.calcular_pena_cumprida(self.data_prisao_definitiva(), self.data_base + timedelta(days=1))  # noqa
                calculo.pena_cumprida_data_registro = self.calcular_pena_cumprida(self.data_prisao_definitiva(), date.today() + timedelta(days=1))  # noqa

                calculo.pena_restante_data_base = self.calcular_pena_restante(data_base=self.data_base)
                calculo.pena_restante_data_registro = self.calcular_pena_restante(data_base=date.today())

                calculo.atualizado_por = cadastrado_por
                calculo.data_atualizacao = datetime.now()

                calculo.save()

                reversion.set_user(cadastrado_por.usuario)
                reversion.set_comment(Util.get_comment_save(cadastrado_por.usuario, calculo, novo))

                return True

        return False


class Fracao(object):

    def __init__(self, fracao):
        self.fracao = fracao
        self.prisoes = []
        self.pena_cumprida = AnoMesDia()

    @property
    def pena_imposta(self):
        total = AnoMesDia()
        for prisao in self.prisoes:
            total += AnoMesDia(prisao.duracao_pena_anos, prisao.duracao_pena_meses, prisao.duracao_pena_dias)
        return total

    def dif_penas(self):
        return self.pena_imposta - self.pena_cumprida

    def calculo_pr(self):
        dias = int(self.dif_penas().dias() * float(self.fracao))
        return AnoMesDia() + AnoMesDia(0, 0, dias)

    def calculo_lc(self):
        dias = int(self.pena_imposta.dias() * float(self.fracao))
        return AnoMesDia() + AnoMesDia(0, 0, dias)


class PessoaAssistida(object):
    @staticmethod
    def list_prisoes(pessoa):
        return DbPrisao.objects.filter(pessoa=pessoa, ativo=True)

    @staticmethod
    def list_prisoes_condenado(pessoa):
        return DbPrisao.objects.filter(pessoa=pessoa, tipo=DbPrisao.TIPO_CONDENADO, ativo=True)

    @staticmethod
    def list_atendimentos(pessoa):
        # recupera atendimentos onde a pessoa que esta ligando eh requerido
        atendimentos = AtendimentoPessoa.objects.filter(pessoa=pessoa, tipo=AtendimentoPessoa.TIPO_REQUERENTE).values(
            'atendimento_id')
        # recupera atendimentos que estejam na lista de atendimentos da pessoa
        atendimentos = Atendimento.objects.filter(id__in=atendimentos, tipo=Atendimento.TIPO_INICIAL,
                                                  remarcado=None).exclude(data_agendamento=None).order_by(
            '-data_atendimento', 'data_agendamento')

        return atendimentos


class Prisao(object):
    @staticmethod
    def list_prisoes_cidade(cidade):
        return EstabelecimentoPenal.objects.filter(endereco__municipio=cidade)

    @staticmethod
    def list_progressao_defensor(defensor):

        defensorias = set(defensor.atuacoes(vigentes=True).values_list('defensoria_id', flat=True))

        return DbPrisao.objects.filter(
            tipo=DbPrisao.TIPO_CONDENADO,
            parte__defensoria__in=defensorias).order_by('data_prisao')
