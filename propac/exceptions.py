from core.exceptions import CoreBaseException


class TarefaNaoEncontradaException(CoreBaseException):
    message = "Tarefa não encontrada"


class TarefaErroException(CoreBaseException):
    message = "Ocorreu um erro ao processar a tarefa"
