# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import datetime
from fractions import Fraction

# Bibliotecas de terceiros
import reversion
from django.db import models

# Solar
from assistido.models import PessoaAssistida
from atendimento.atendimento.models import Defensor as AtendimentoDefensor
from contrib.models import Endereco, Telefone, Util
from core.models import AuditoriaAbstractMixin

# Modulos locais
from . import managers


class Aprisionamento(models.Model):
    # modelo que representa um aprisionamento no sistema
    SITUACAO_PRESO = 0
    SITUACAO_SOLTO = 1
    SITUACAO_TRANSFERIDO = 2
    # opções para a situação do aprisionamento
    LISTA_SITUACAO = (
        (SITUACAO_PRESO, 'Preso'),
        (SITUACAO_SOLTO, 'Solto'),
        (SITUACAO_TRANSFERIDO, 'Transferido'),
    )
    # constantes para as opções de origem do registro
    ORIGEM_REGISTRO = 0
    ORIGEM_PRISAO = 1
    ORIGEM_VISITA = 2
    ORIGEM_MUDANCA_REGIME = 3
    # opções para a origem do registro
    LISTA_ORIGEM = (
        (ORIGEM_REGISTRO, 'Registro'),
        (ORIGEM_PRISAO, 'Prisão'),
        (ORIGEM_VISITA, 'Visita'),
        (ORIGEM_MUDANCA_REGIME, 'Mudança de Regime'),
    )
    # campos do modelo Aprisionamento
    prisao = models.ForeignKey('Prisao', related_name='aprisionamentos', on_delete=models.DO_NOTHING)
    estabelecimento_penal = models.ForeignKey('EstabelecimentoPenal', verbose_name='Estabelecimento Penal', on_delete=models.DO_NOTHING)
    data_inicial = models.DateTimeField('Data da Início')
    data_final = models.DateTimeField('Data de Término', null=True, blank=True)
    situacao = models.SmallIntegerField('Situação', choices=LISTA_SITUACAO, null=False, blank=False, default=SITUACAO_PRESO)  # noqa
    historico = models.TextField(blank=True, null=True, default=None)
    detracao = models.BooleanField('Detração', default=False)

    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    origem_cadastro = models.SmallIntegerField('Origem', choices=LISTA_ORIGEM, null=False, blank=False, default=ORIGEM_REGISTRO)  # noqa
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    data_exclusao = models.DateTimeField(u'Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, editable=False, on_delete=models.DO_NOTHING)  # noqa
    ativo = models.BooleanField(default=True)

    eventos = models.ManyToManyField('Historico', related_name='aprisionamentos', editable=False)

    objects = managers.AprisionamentoManager()

    @reversion.create_revision(atomic=False)
    def excluir(self, excluido_por):  # método para exclusão do aprisionamento
        # marca o aprisionamento como excluído, registra a data de exclusão e o usuário responsável
        self.excluido_por = excluido_por.servidor
        self.data_exclusao = datetime.datetime.now()
        self.ativo = False
        self.save()

        reversion.set_user(excluido_por)
        reversion.set_comment(Util.get_comment_delete(excluido_por, self))

        return True

    @property
    def dias_preso(self):  # Propriedade que calcula a quantidade de dias que o indivíduo ficou preso
        if self.data_final:
            return (self.data_final.date() - self.data_inicial.date()).days
        else:
            return (datetime.date.today() - self.data_inicial.date()).days

    def __str__(self):
        return self.prisao.pessoa.nome


class Soltura(models.Model):  # modelo que representa uma soltura no sistema
    # armazena informações sobre o tipo de soltura, histórico e mais informações relacionadas
    TIPO_DEC_JUIZ_ATO_CONVERSAO = 1
    TIPO_HABEAS_CORPUS = 2
    TIPO_LIBERDADE_PROVISORIA = 3
    TIPO_PAGAMENTO_FIANCA = 4
    TIPO_REVOGACAO_PREVENTIVA = 5
    TIPO_SENTENCA_ABSOLUTORIA = 6
    TIPO_RELAXAMENTO_PRISAO = 7

    LISTA_TIPO = (
        (TIPO_DEC_JUIZ_ATO_CONVERSAO, u'Dec. Juíz do Ato Conversão em Flagrante'),
        (TIPO_HABEAS_CORPUS, u'Habeas Corpus'),
        (TIPO_LIBERDADE_PROVISORIA, u'Liberdade Provisória'),
        (TIPO_PAGAMENTO_FIANCA, u'Pagamento de Fiança'),
        (TIPO_REVOGACAO_PREVENTIVA, u'Revogação de Prisão Preventiva'),
        (TIPO_SENTENCA_ABSOLUTORIA, u'Sentença Absolutória'),
        (TIPO_RELAXAMENTO_PRISAO, u'Relaxamento de Prisão'),
    )

    aprisionamento = models.OneToOneField('Aprisionamento', on_delete=models.DO_NOTHING)
    processo = models.ForeignKey('processo.Processo', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    tipo = models.SmallIntegerField('Tipo', choices=LISTA_TIPO, null=False, blank=False)
    historico = models.TextField(blank=True, null=True, default=None)

    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    data_exclusao = models.DateTimeField(u'Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, editable=False, on_delete=models.DO_NOTHING)  # noqa
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.aprisionamento.prisao.pessoa.nome


class Prisao(models.Model):  # modelo que representa uma prisão no sistema
    # armazena informações sobre o tipo de prisão, a pessoa associada, duração da pena, entre outros
    TIPO_PROVISORIO = 0
    TIPO_CONDENADO = 1

    LISTA_TIPO = (
        (TIPO_PROVISORIO, 'Provisório'),
        (TIPO_CONDENADO, 'Condenado'),
    )

    TIPO_CRIME_TENTANDO = 10
    TIPO_CRIME_CONSUMADO = 20

    LISTA_TIPO_CRIME = (
        (TIPO_CRIME_TENTANDO, 'Tentado'),
        (TIPO_CRIME_CONSUMADO, 'Consumado'),
    )

    SITUACAO_PRESO = 0
    SITUACAO_SOLTO = 1

    LISTA_SITUACAO = (
        (SITUACAO_PRESO, 'Preso'),
        (SITUACAO_SOLTO, 'Solto'),
    )

    REGIME_FECHADO = 0
    REGIME_SEMIABERTO = 1
    REGIME_ABERTO = 2
    REGIME_LIVRAMENTO = 3
    REGIME_MEDIDA_SEGURANCA = 4

    LISTA_REGIME = (
        (REGIME_FECHADO, 'Fechado'),
        (REGIME_SEMIABERTO, 'Semiaberto'),
        (REGIME_ABERTO, 'Aberto'),
        (REGIME_LIVRAMENTO, 'Livramento'),
        (REGIME_MEDIDA_SEGURANCA, 'Medida de Segurança'),
    )

    PRONUNCIA_IMPRONUNCIADO = 0
    PRONUNCIA_CONDENADO = 1
    PRONUNCIA_DESCLASSIFICADO = 2

    LISTA_PRONUNCIA = (
        (PRONUNCIA_IMPRONUNCIADO, 'Impronunciado'),
        (PRONUNCIA_CONDENADO, 'Pronunciado'),
        (PRONUNCIA_DESCLASSIFICADO, 'Desclassificado'),
    )

    SENTENCA_ABSOLVIDO = 0
    SENTENCA_CONDENADO = 1
    SENTENCA_DESCLASSIFICADO = 2
    SENTENCA_ABS_IMP_INTERNACAO = 101
    SENTENCA_ABS_IMP_TRATAMENTO = 102

    LISTA_SENTENCA = (
        (SENTENCA_ABSOLVIDO, 'Absolvido'),
        (SENTENCA_CONDENADO, 'Condenado'),
        (SENTENCA_DESCLASSIFICADO, 'Desclassificado'),
        (SENTENCA_ABS_IMP_INTERNACAO, 'Absolvição Imprópria - Internação'),
        (SENTENCA_ABS_IMP_TRATAMENTO, 'Absolvição Imprópria - Tratamento Ambulatorial'),
    )

    PR_COMUM = Fraction(1, 6)
    PR_HEDIONDO = Fraction(2, 5)
    PR_HEDIONDO_REICIDENTE = Fraction(3, 5)

    LISTA_PR = (
        (PR_COMUM, '1/6 - Comum'),
        (PR_HEDIONDO, '2/5 - Hediondo Primário'),
        (PR_HEDIONDO_REICIDENTE, '3/5 - Hediondo Reicidente'),
    )

    TIPO_LISTA_PR = (
        (16, '1/6 - Comum'),
        (25, '2/5 - Hediondo Primário'),
        (35, '3/5 - Hediondo Reicidente'),
    )

    LC_COMUM = Fraction(1, 3)
    LC_COMUM_REICIDENTE = Fraction(1, 2)
    LC_HEDIONDO = Fraction(2, 3)
    LC_HEDIONDO_REICIDENTE = Fraction(1, 1)

    LISTA_LC = (
        (LC_COMUM, '1/3 - Comum Primário'),
        (LC_COMUM_REICIDENTE, '1/2 - Comum Reicidente'),
        (LC_HEDIONDO, '2/3 - Hediondo'),
        (LC_HEDIONDO_REICIDENTE, '1/1 - Hediondo Reicidente'),
    )

    TIPO_LISTA_LC = (
        (13, '1/3 - Comum Primário'),
        (12, '1/2 - Comum Reicidente'),
        (23, '2/3 - Hediondo'),
        (11, '1/1 - Hediondo Reicidente'),
    )

    PENA_PRIVATIVA = 0
    PENA_RESTRITIVA = 1

    LISTA_PENA = (
        (PENA_PRIVATIVA, 'Privativa'),
        (PENA_RESTRITIVA, 'Restritiva'),
    )

    pena = models.SmallIntegerField('Pena', choices=LISTA_PENA, null=False, blank=False, default=PENA_PRIVATIVA)
    tipo = models.SmallIntegerField('Tipo', choices=LISTA_TIPO, null=False, blank=False, default=TIPO_PROVISORIO)
    pessoa = models.ForeignKey('assistido.PessoaAssistida', on_delete=models.DO_NOTHING)
    processo = models.ForeignKey('processo.Processo', null=True, blank=True, related_name='prisoes', on_delete=models.DO_NOTHING)
    parte = models.ForeignKey('processo.Parte', null=True, blank=True, related_name='prisoes', on_delete=models.DO_NOTHING)
    origem = models.OneToOneField('Prisao', null=True, blank=True, related_name='originada', on_delete=models.DO_NOTHING)

    data_fato = models.DateField('Data do Fato', null=True, blank=True)
    data_prisao = models.DateField('Data da Prisão', null=True, blank=True)
    data_termino = models.DateField('Término da Pena', null=True, blank=True)
    local_prisao = models.ForeignKey('contrib.Municipio', verbose_name='Município do Local da Prisão', null=True,
                                     blank=False, on_delete=models.DO_NOTHING)
    estabelecimento_penal = models.ForeignKey('EstabelecimentoPenal', verbose_name='Estabelecimento Penal', null=True,
                                              blank=False, on_delete=models.DO_NOTHING)
    tipificacao = models.ForeignKey('Tipificacao', verbose_name='Tipificação', null=True, blank=False, on_delete=models.DO_NOTHING)
    tentado_consumado = models.SmallIntegerField(
        'Tentado/Consumado',
        choices=LISTA_TIPO_CRIME,
        null=True,
        blank=True,
        default=None)

    situacao = models.SmallIntegerField('Situação', choices=LISTA_SITUACAO, null=True, blank=True)
    regime_inicial = models.SmallIntegerField('Regime Inicial', choices=LISTA_REGIME, null=True, blank=True)
    regime_atual = models.SmallIntegerField('Regime Atual', choices=LISTA_REGIME, null=True, blank=True)

    duracao_pena_anos = models.SmallIntegerField('Duração da Pena (Anos)', null=False, blank=True, default=0)
    duracao_pena_meses = models.SmallIntegerField('Duração da Pena (Meses)', null=False, blank=True, default=0)
    duracao_pena_dias = models.SmallIntegerField('Duração da Pena (Dias)', null=False, blank=True, default=0)

    duracao_pena_horas = models.DurationField('Duração da Pena (Horas)', null=True, blank=True, help_text='Formato DD HH:mm:ss ou HHH:mm:ss')  # noqa

    prestacao_pecuniaria = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=None)

    multa = models.CharField('Dias Multa', max_length=512, null=True, blank=True)

    fracao_pr = models.SmallIntegerField('Fração PR', choices=TIPO_LISTA_PR, null=True, blank=True)
    fracao_lc = models.SmallIntegerField('Fração LC', choices=TIPO_LISTA_LC, null=True, blank=True)

    data_recebimento_denuncia = models.DateField('Data de Recebimento da Denúncia', null=True, blank=True)
    data_pronuncia = models.DateField('Data da Pronúncia', null=True, blank=True)
    resultado_pronuncia = models.SmallIntegerField('Resultado da Pronúncia', choices=LISTA_PRONUNCIA, null=True, blank=True)  # noqa
    historico_pronuncia = models.TextField('Histórico da Pronúncia', blank=True, null=True, default=None)
    resultado_sentenca = models.SmallIntegerField('Resultado da Sentença', choices=LISTA_SENTENCA, null=True, blank=True)  # noqa

    data_sentenca_condenatoria = models.DateField('Data da Setença Condenatória', null=True, blank=True)
    data_transito_defensor = models.DateField('Trânsito em Julgado da Sentença para o Defensor', null=True, blank=True)
    data_transito_acusacao = models.DateField('Trânsito em Julgado da Sentença para a Acusação', null=True, blank=True)
    data_transito_apenado = models.DateField('Trânsito em Julgado da Sentença para o(a) Apenado(a)', null=True, blank=True)  # noqa

    data_liquidacao = models.DateField('Data da Liquidação da Pena', null=True, blank=True)
    data_base = models.DateField('Data-Base', null=True, blank=True)
    reicidente = models.BooleanField(default=False)

    data_baixa = models.DateField('Data da Baixa', null=True, blank=True)
    motivo_baixa = models.ForeignKey('MotivoBaixaPrisao', verbose_name='Motivo da Baixa', null=True, blank=True, on_delete=models.DO_NOTHING)  # noqa
    baixado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, editable=False, on_delete=models.DO_NOTHING)  # noqa

    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, editable=False, on_delete=models.DO_NOTHING)  # noqa

    data_exclusao = models.DateTimeField(u'Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, editable=False, on_delete=models.DO_NOTHING)  # noqa
    ativo = models.BooleanField(default=True)

    eventos = models.ManyToManyField('Historico', related_name='prisoes', editable=False)

    def atendimentos(self):
        # retorna os atendimentos relacionados a essa prisão que sejam do tipo Inicial ou Retorno
        return Atendimento.objects.filter(
            prisao=self,
            tipo__in=[Atendimento.TIPO_INICIAL, Atendimento.TIPO_RETORNO],
            ativo=True).order_by('data_atendimento')

    def visitas(self):
        # retorna os atendimentos relacionados a essa prisão que sejam do tipo Visita
        return Atendimento.objects.filter(prisao=self,
                                          tipo=Atendimento.TIPO_VISITA,
                                          ativo=True).order_by('data_atendimento')

    @property
    def duracao_pena(self):  # retorna a duração da pena em anos, meses, dias e horas
        horas = 0
        if self.duracao_pena_horas:
            horas = self.duracao_pena_horas.days * 24 + self.duracao_pena_horas.seconds / 3600

        return {
            'anos': self.duracao_pena_anos,
            'meses': self.duracao_pena_meses,
            'dias': self.duracao_pena_dias,
            'horas': horas
        }

    @property
    def dias_preso(self):  # retorna o número de dias que a prisão está ativa (da data de prisão até hoje)
        if self.data_prisao:
            return (datetime.date.today() - self.data_prisao).days
        else:
            return 0

    @property
    def dias_liberdade(self):  # retorna o número de dias desde que o preso foi solto (da data de saída até hoje)
        dias_liberdade = datetime.date.today() - self.data_saida
        return dias_liberdade.days

    @property
    def defensor(self):
        # retorna o defensor associado à prisão (primeiro atendimento relacionado à prisão)
        atendimento = Atendimento.objects.filter(prisao=self)[:1]

        if atendimento:
            return atendimento[0].defensor
        else:
            return None

    @property
    def get_fracao_pr(self):  # retorna a fração da pena remanescente, caso haja
        if self.fracao_pr:
            num, den = divmod(self.fracao_pr, 10)
            return Fraction(num, den)

    @property
    def get_fracao_lc(self):  # retorna a fração da liquidação de condenação remanescente, caso haja
        if self.fracao_lc:
            num, den = divmod(self.fracao_lc, 10)
            return Fraction(num, den)

    def get_tipo(self): 
        # retorna o tipo da prisão (provisório ou condenado), verificando o processo associado, se houver
        if self.processo and self.processo.acao_id:
            if self.processo.acao.execucao_penal:
                return self.TIPO_CONDENADO
            else:
                return self.TIPO_PROVISORIO
        return self.tipo

    @property
    def esta_em_regime_aberto(self):  # retorna True se a prisão estiver em regime aberto, False caso contrário
        return self.regime_atual == self.REGIME_ABERTO

    @reversion.create_revision(atomic=False)
    def excluir(self, excluido_por):
        # exclui a prisão, desativando-a e registrando o usuário que fez a exclusão
        self.excluido_por = excluido_por.servidor
        self.data_exclusao = datetime.datetime.now()
        self.ativo = False
        self.save()

        reversion.set_user(excluido_por)
        reversion.set_comment(Util.get_comment_delete(excluido_por, self))

        return True

    def __str__(self):
        return self.pessoa.nome

    class Meta:
        app_label = 'nadep'
        verbose_name = u'Prisão'
        verbose_name_plural = u'Prisões'


class PenaRestritiva(models.Model):
    # modelo para representar uma pena restritiva associada a uma prisão
    RESTRICAO_PRESTACAO_PECUNIARIA = 1
    RESTRICAO_PERDA_BENS_VALORES = 2
    RESTRICAO_PRESTACAO_SERVICO = 4
    RESTRICAO_INTERDICAO_DIREITOS = 5
    RESTRICAO_LIMITACAO_FIM_DE_SEMANA = 6

    LISTA_RESTRICAO = (
        (RESTRICAO_PRESTACAO_PECUNIARIA, 'Prestação Pecuniária (CP Art. 43, I)'),
        (RESTRICAO_PERDA_BENS_VALORES, 'Perda de Bens e Valores (CP Art. 43, II)'),
        (RESTRICAO_PRESTACAO_SERVICO, 'Prestação de Serviço (CP Art. 43, IV)'),
        (RESTRICAO_INTERDICAO_DIREITOS, 'Interdição Temporária de Direitos (CP Art. 43, V)'),
        (RESTRICAO_LIMITACAO_FIM_DE_SEMANA, 'Limitação de Fim de Semana (CP Art. 43, VI)'),
    )
    # campo de chave estrangeira para a prisão associada à pena restritiva
    prisao = models.ForeignKey('Prisao', on_delete=models.DO_NOTHING)
    restricao = models.SmallIntegerField('Tipo', choices=LISTA_RESTRICAO, null=False, blank=False)
    ativo = models.BooleanField(default=True)
    # campos para registrar informações de data de cadastro, cadastro por quem, data de exclusão e exclusão por quem
    data_cadastro = models.DateTimeField(u'Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    data_exclusao = models.DateTimeField(u'Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                     editable=False, on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'nadep'
        verbose_name = u'Pena Restritiva'
        verbose_name_plural = u'Penas Restritivas'
        unique_together = ('prisao', 'restricao')


class RestricaoPrestacaoServico(models.Model):
    # modelo para representar uma restrição de prestação de serviço associada a uma prisão
    prisao = models.ForeignKey('Prisao', on_delete=models.DO_NOTHING)
    data_referencia = models.DateField('Data de Referência', null=False, blank=False)
    horas_trabalhadas = models.DurationField('Horas Trabalhadas', null=False, blank=False, help_text='Formato DD HH:mm:ss ou HHH:mm:ss')  # noqa
    ativo = models.BooleanField(default=True)
    # campos para registrar informações de data de cadastro, cadastro por quem, data de exclusão e exclusão por quem
    data_cadastro = models.DateTimeField(u'Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    data_exclusao = models.DateTimeField(u'Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                     editable=False, on_delete=models.DO_NOTHING)

    class Meta:
        app_label = 'nadep'
        verbose_name = u'Restrição - Prestação de Serviço'
        verbose_name_plural = u'Restrição - Prestação de Serviço'
        unique_together = ('prisao', 'data_referencia')
        ordering = ('-ativo', 'prisao__pessoa__nome', 'data_referencia')

    def horas_to_string(self):  # converte a duração das horas trabalhadas para uma string no formato HH:mm
        if self.horas_trabalhadas:
            horas, minutos = divmod((self.horas_trabalhadas.seconds / 60),  60)
            horas += self.horas_trabalhadas.days * 24
            return '{0:d}:{1:02d}'.format(int(horas), int(minutos))
        else:
            return '0:00'


class EstabelecimentoPenal(models.Model):  # modelo para representar um estabelecimento penal
    # opções para o campo destinado_ao_sexo, que indica para qual sexo o estabelecimento é destinado
    SEXO_MASCULINO = 0
    SEXO_FEMININO = 1
    SEXO_AMBOS = 2

    LISTA_SEXO = (
        (SEXO_MASCULINO, 'Masculino'),
        (SEXO_FEMININO, 'Feminino'),
        (SEXO_AMBOS, 'Ambos')
    )

    data_cadastro = models.DateTimeField('Data de cadastro', blank=True, null=True, auto_now_add=True, editable=False)
    nome = models.CharField(max_length=200)
    endereco = models.ForeignKey(Endereco, null=True, blank=True, default=None, on_delete=models.DO_NOTHING)
    telefone = models.ForeignKey(Telefone, null=True, blank=True, default=None, on_delete=models.DO_NOTHING)
    email = models.EmailField(max_length=128, null=True, blank=True, default=None)
    tipo = models.ForeignKey('TipoEstabelecimentoPenal', on_delete=models.DO_NOTHING)
    destinado_ao_sexo = models.SmallIntegerField('Destinado ao sexo', choices=LISTA_SEXO, default=SEXO_MASCULINO)
    inspecionado_pela_dpe = models.BooleanField('Inspecionado pela DPE?', default=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    class Meta:
        app_label = 'nadep'
        verbose_name = u'Estabelecimento Penal'
        verbose_name_plural = u'Estabelecimentos Penais'


class Atendimento(AtendimentoDefensor):  # modelo para representar um atendimento relacionado a uma prisão
    # opções para o campo parentesco_preso, que indica o grau de parentesco com o preso
    LISTA_GRAU_PARENTESCO = (
        (1, 'Pai/Mãe'),
        (2, 'Filho/Filha'),
        (3, 'Irmão/Irmã'),
        (4, 'Esposo/Esposta'),
        (0, 'Outro'),
    )

    prisao = models.ForeignKey('Prisao', null=True, blank=True, on_delete=models.DO_NOTHING)
    assunto = models.CharField(max_length=255, null=True, blank=True)
    estabelecimento_penal = models.ForeignKey(EstabelecimentoPenal, null=True, blank=True, on_delete=models.DO_NOTHING)
    interessado = models.ForeignKey(PessoaAssistida, null=True, blank=True, on_delete=models.DO_NOTHING)
    parentesco_preso = models.SmallIntegerField(choices=LISTA_GRAU_PARENTESCO, null=True, blank=True)

    eventos = models.ManyToManyField('Historico', related_name='atendimentos', editable=False)

    class Meta:
        app_label = 'nadep'


class Tipificacao(AuditoriaAbstractMixin):  # modelo para representar uma tipificação de crime
    # opções para o campo tipo, que indica o tipo de crime (comum ou hediondo)
    CRIME_COMUM = 0
    CRIME_HEDIONDO = 1

    LISTA_CRIME = (
        (CRIME_COMUM, 'Comum'),
        (CRIME_HEDIONDO, 'Hediondo'),
    )

    tipo = models.SmallIntegerField(choices=LISTA_CRIME, null=True, blank=True)
    nome = models.TextField()

    numero_lei = models.CharField("Número da Lei", max_length=25, null=True, blank=True)
    artigo_lei = models.CharField("Artigo da Lei", max_length=25, null=True, blank=True)
    paragrafo_lei = models.CharField("Parágrafo da Lei", max_length=25, null=True, blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        app_label = 'nadep'
        ordering = ['-desativado_em', 'nome']
        verbose_name = u'Tipificação'
        verbose_name_plural = u'Tipificações'


class TipoEstabelecimentoPenal(AuditoriaAbstractMixin):  # modelo para representar um tipo de estabelecimento penal
    nome = models.CharField(max_length=256)

    class Meta:
        verbose_name = u'Tipo de Estabelecimento Penal'
        verbose_name_plural = u'Tipos de Estabelecimento Penal'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Falta(models.Model):  # modelo para representar uma falta relacionada a uma pessoa assistida
    # opções para o campo resultado, que indica o resultado da falta (aguardando julgamento, procedente ou improcedente)
    RESULTADO_AGUARDANDO = 0
    RESULTADO_PROCEDENTE = 1
    RESULTADO_IMPROCEDENTE = 2

    LISTA_RESULTADO = (
        (RESULTADO_AGUARDANDO, u'Aguardando Julgamento'),
        (RESULTADO_PROCEDENTE, u'Procedente'),
        (RESULTADO_IMPROCEDENTE, u'Improcedente'),
    )

    pessoa = models.ForeignKey('assistido.PessoaAssistida', on_delete=models.DO_NOTHING)
    estabelecimento_penal = models.ForeignKey(EstabelecimentoPenal, null=True, blank=True, on_delete=models.DO_NOTHING)
    processo = models.OneToOneField('processo.Processo', null=True, blank=True, on_delete=models.DO_NOTHING)
    data_fato = models.DateTimeField(u'Data do Fato', null=True, blank=True)
    numero_pad = models.CharField(u'Número PAD', max_length=255)
    observacao = models.TextField(u'Observação', blank=True, null=True, default=None)
    resultado = models.SmallIntegerField(u'Tipo', choices=LISTA_RESULTADO, null=False, blank=False,
                                         default=RESULTADO_AGUARDANDO)
    data_cadastro = models.DateTimeField(u'Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    data_exclusao = models.DateTimeField(u'Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                     editable=False, on_delete=models.DO_NOTHING)
    evento = models.ForeignKey('Historico', related_name='falta', null=True, blank=True, editable=False, on_delete=models.DO_NOTHING)
    ativo = models.BooleanField(default=True)

    @reversion.create_revision(atomic=False)
    def excluir(self, excluido_por):  # método para realizar a exclusão da falta

        self.excluido_por = excluido_por.servidor
        self.data_exclusao = datetime.datetime.now()
        self.ativo = False
        self.save()

        reversion.set_user(excluido_por)
        reversion.set_comment(Util.get_comment_delete(excluido_por, self))

        return True

    def __str__(self):
        return self.observacao

    class Meta:
        app_label = 'nadep'
        verbose_name = u'Falta'
        verbose_name_plural = u'Faltas'


class Remissao(models.Model):  # modelo para representar a remissão de pena
    # opções para o campo "tipo"
    TIPO_OUTRO = 0
    TIPO_TRABALHO = 1

    LISTA_TIPO = (
        (TIPO_OUTRO, u'Outros (1/1)'),
        (TIPO_TRABALHO, u'Trabalho (1/3)'),
    )

    pessoa = models.ForeignKey('assistido.PessoaAssistida', on_delete=models.DO_NOTHING)
    data_inicial = models.DateField(u'Data Inicial')
    data_final = models.DateField(u'Data Final')
    dias_registro = models.SmallIntegerField(u'Dias Registro', null=False, blank=False)
    dias_remissao = models.DecimalField(u'Dias Remição', null=False, blank=False, max_digits=16, decimal_places=2)
    tipo = models.SmallIntegerField(u'Tipo', choices=LISTA_TIPO, null=False, blank=False, default=TIPO_OUTRO)

    data_cadastro = models.DateTimeField(u'Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    data_exclusao = models.DateTimeField(u'Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                     editable=False, on_delete=models.DO_NOTHING)

    falta = models.ForeignKey('Falta', related_name='remissoes', null=True, blank=True, editable=False, on_delete=models.DO_NOTHING)
    para_progressao = models.BooleanField(u'Para Progressão?', default=True)
    ativo = models.BooleanField(default=True)

    @reversion.create_revision(atomic=False)
    def excluir(self, excluido_por):  # método para excluir a remissão
        # define o servidor que está excluindo a remissão
        self.excluido_por = excluido_por.servidor
        self.data_exclusao = datetime.datetime.now()
        self.ativo = False
        self.save()

        reversion.set_user(excluido_por)
        reversion.set_comment(Util.get_comment_delete(excluido_por, self))

        return True

    class Meta:
        app_label = 'nadep'
        verbose_name = u'Remição'
        verbose_name_plural = u'Remições'


class Interrupcao(models.Model):  # modelo para representar a interrupção de pena

    pessoa = models.ForeignKey('assistido.PessoaAssistida', on_delete=models.DO_NOTHING)
    data_inicial = models.DateField(u'Data Inicial')
    data_final = models.DateField(u'Data Final', blank=True, null=True, default=None)
    observacao = models.TextField(u'Observação', blank=True, null=True, default=None)

    data_cadastro = models.DateTimeField(u'Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    data_exclusao = models.DateTimeField(u'Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None,
                                     editable=False, on_delete=models.DO_NOTHING)
    ativo = models.BooleanField(default=True)  # indica se a interrupção está ativa ou não

    @reversion.create_revision(atomic=False)
    def excluir(self, excluido_por):  # método para excluir a interrupção
        # define o servidor que está excluindo a interrupção
        self.excluido_por = excluido_por.servidor
        self.data_exclusao = datetime.datetime.now()
        self.ativo = False
        self.save()

        reversion.set_user(excluido_por)
        reversion.set_comment(Util.get_comment_delete(excluido_por, self))

        return True

    @property
    def dias(self):  # propriedade que calcula e retorna a quantidade de dias da interrupção
        if self.data_inicial and self.data_final:
            return (self.data_final - self.data_inicial).days
        else:
            return 0

    class Meta:
        app_label = 'nadep'
        verbose_name = u'Interrupção'
        verbose_name_plural = u'Interrupções'


class MudancaRegime(models.Model):
    # modelo para representar a mudança de regime de pena
    TIPO_PROGRESSAO = 0  # opções para o campo "tipo"
    TIPO_REGRESSAO = 1

    LISTA_TIPO = (
        (TIPO_PROGRESSAO, 'Progressão'),
        (TIPO_REGRESSAO, 'Regressão'),
    )
    # prisão associada à mudança de regime (chave estrangeira para o modelo Prisao)
    prisao = models.ForeignKey('Prisao', on_delete=models.DO_NOTHING)
    tipo = models.SmallIntegerField('Tipo', choices=LISTA_TIPO)
    regime = models.SmallIntegerField('Regime', choices=Prisao.LISTA_REGIME)
    estabelecimento_penal = models.ForeignKey('EstabelecimentoPenal', verbose_name='Estabelecimento Penal', null=True, blank=True, on_delete=models.DO_NOTHING)  # noqa
    data_registro = models.DateTimeField('Data Registro')
    data_base = models.DateTimeField('Data Base')
    historico = models.TextField(blank=True, null=True, default=None)

    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    data_exclusao = models.DateTimeField(u'Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, editable=False, on_delete=models.DO_NOTHING)  # noqa

    evento = models.ForeignKey('Historico', related_name='mudanca_regime', null=True, blank=True, editable=False, on_delete=models.DO_NOTHING)
    ativo = models.BooleanField(default=True)

    @reversion.create_revision(atomic=False)
    def excluir(self, excluido_por):  # método para excluir a mudança de regime

        self.excluido_por = excluido_por.servidor  # define o servidor que está excluindo a mudança de regime
        self.data_exclusao = datetime.datetime.now()
        self.ativo = False
        self.save()

        reversion.set_user(excluido_por)
        reversion.set_comment(Util.get_comment_delete(excluido_por, self))

        return True

    class Meta:
        app_label = 'nadep'
        verbose_name = u'Mudança de Regime'
        verbose_name_plural = u'Mudanças de Regime'
        ordering = ['prisao__pessoa__nome', 'data_registro']


class Historico(models.Model):  # modelo para representar o histórico de eventos
    # opções para o campo "evento"
    EVENTO_PRISAO = 1
    EVENTO_SOLTURA = 2
    EVENTO_ATENDIMENTO = 3
    EVENTO_VISITA = 4
    EVENTO_CONDENACAO = 5
    EVENTO_FALTA = 6
    EVENTO_REGRESSAO = 7
    EVENTO_PROGRESSAO = 8
    EVENTO_MUDANCA_REGIME = 9
    EVENTO_TRANSFERENCIA = 10
    EVENTO_CONVERSAO = 11
    EVENTO_LIQUIDACAO = 12
    EVENTO_BAIXA = 13

    LISTA_EVENTO = (
        (EVENTO_PRISAO, 'Prisão'),
        (EVENTO_SOLTURA, 'Soltura'),
        (EVENTO_ATENDIMENTO, 'Atendimento'),
        (EVENTO_VISITA, 'Visita'),
        (EVENTO_CONDENACAO, 'Condenação'),
        (EVENTO_FALTA, 'Falta'),
        (EVENTO_REGRESSAO, 'Regressão'),
        (EVENTO_PROGRESSAO, 'Progressão'),
        (EVENTO_MUDANCA_REGIME, 'Mudança de Regime'),
        (EVENTO_TRANSFERENCIA, 'Transferência'),
        (EVENTO_CONVERSAO, 'Conversao de Pena'),
        (EVENTO_LIQUIDACAO, 'Liquidação de Pena'),
        (EVENTO_BAIXA, 'Baixa de Pena'),
    )

    pessoa = models.ForeignKey('assistido.PessoaAssistida', on_delete=models.DO_NOTHING)
    data_registro = models.DateField('Data Registro')
    evento = models.SmallIntegerField('Evento', choices=LISTA_EVENTO)
    historico = models.TextField(blank=True, null=True, default=None)

    data_cadastro = models.DateTimeField('Data de Cadastro', null=True, blank=False, auto_now_add=True, editable=False)
    cadastrado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, on_delete=models.DO_NOTHING)
    data_exclusao = models.DateTimeField(u'Data de Exclusão', null=True, blank=False, editable=False)
    excluido_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=True, null=True, default=None, editable=False, on_delete=models.DO_NOTHING)  # noqa
    ativo = models.BooleanField(default=True)

    class Meta:
        app_label = 'nadep'
        verbose_name = u'Histórico'
        verbose_name_plural = u'Históricos'
        ordering = ['pessoa__nome', 'data_registro']


class CalculoExecucaoPenal(models.Model):  # modelo para representar o cálculo de execução penal
    # pessoa assistida associada ao cálculo (chave estrangeira para o modelo PessoaAssistida)
    pessoa = models.OneToOneField('assistido.PessoaAssistida', on_delete=models.DO_NOTHING)
    pessoa_nome = models.CharField(max_length=256)
    # processo associado ao cálculo (chave estrangeira para o modelo Processo)
    execucao = models.ForeignKey('processo.Processo', related_name='calculos', on_delete=models.DO_NOTHING)
    execucao_numero = models.CharField('Número', max_length=50)
    # estabelecimento penal associado ao cálculo (chave estrangeira para o modelo EstabelecimentoPenal)
    estabelecimento_penal = models.ForeignKey('EstabelecimentoPenal', verbose_name='Estabelecimento Penal', on_delete=models.DO_NOTHING)
    estabelecimento_penal_nome = models.CharField(max_length=200)

    regime_atual = models.SmallIntegerField('Regime Atual', choices=Prisao.LISTA_REGIME)

    data_base = models.DateField('Data-Base')
    data_progressao = models.DateField('Data p/ Progressão de Regime')
    data_livramento = models.DateField('Data p/ Livramento Condicional')
    data_termino = models.DateField('Data do Término da Pena')

    total_pena = models.CharField('Pena Total', max_length=10)
    total_detracoes = models.CharField('Pena Total', max_length=10)
    total_interrupcoes = models.CharField('Pena Total', max_length=10)
    total_remissoes = models.CharField('Pena Total', max_length=10)

    pena_cumprida_data_base = models.CharField('Pena Cumprida - Data Base', max_length=10)
    pena_cumprida_data_registro = models.CharField('Pena Cumprida - Data Registro', max_length=10)

    pena_restante_data_base = models.CharField('Pena Restante - Data Base', max_length=10)
    pena_restante_data_registro = models.CharField('Pena Restante - Data Registro', max_length=10)

    data_atualizacao = models.DateField('Data-Base', null=False, blank=False)
    atualizado_por = models.ForeignKey('contrib.Servidor', related_name='+', blank=False, null=False, on_delete=models.DO_NOTHING)
    atualizado_por_nome = models.CharField(max_length=256)

    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.pessoa_nome

    class Meta:
        app_label = 'nadep'
        verbose_name = u'Cálculo de Execução Penal'
        verbose_name_plural = u'Cálculos de Execução Penal'
        ordering = ['pessoa_nome', 'data_progressao']


class MotivoBaixaPrisao(AuditoriaAbstractMixin):  # modelo para representar o motivo para baixa de prisão
    # nome do motivo para baixa de prisão
    nome = models.CharField(max_length=512)

    class Meta:
        app_label = 'nadep'
        verbose_name = u'Motivo para Baixa de Prisão'
        verbose_name_plural = u'Motivos para Baixa de Prisão'
        ordering = ['nome']

    def __str__(self):
        return self.nome


# registro dos modelos no sistema de versionamento
reversion.register(Aprisionamento)
reversion.register(Prisao, follow=['processo'])
reversion.register(EstabelecimentoPenal, follow=['endereco', 'telefone'])
reversion.register(Atendimento)
reversion.register(Tipificacao)
reversion.register(Falta)
reversion.register(Remissao)
reversion.register(Interrupcao)
reversion.register(MudancaRegime)
reversion.register(Historico)
