from core.exceptions import CoreBaseException


class AtendimentoArquivadoException(CoreBaseException):
    message = "O Atendimento encontra-se arquivado."


class AtendimentoDesarquivadoException(CoreBaseException):
    message = "O Atendimento encontra-se desarquivado."


class AtendimentoPermissionError(CoreBaseException):
    message = "O usuário não tem permissão para realizar ações neste atendimento."


class AtendimentoNaoEncontradoException(CoreBaseException):
    message = "O Atendimento não foi encontrado."


class AtendimentoLotacaoError(CoreBaseException):
    message = "Você não está lotado na mesma defensoria ao qual este atendimento pertence."
