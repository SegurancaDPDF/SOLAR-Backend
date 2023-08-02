from core.exceptions import CoreBaseException


class DadosPessoaInsuficientesException(CoreBaseException):
    message = 'Os dados são insuficientes para criação da Pessoa Assistida!'
