from core.exceptions import CoreBaseException


class ThothsignerFailed(CoreBaseException):
    message = 'Falha ao assinar documento com assinador Thoth Signer.'


class ThothsignerUnavailable(CoreBaseException):
    message = 'O Assinador de documentos Thoth Signer está indisponível no momento.'
