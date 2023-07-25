from core.exceptions import CoreBaseException


class DocumentOriginNotFound(CoreBaseException):
    message = 'Não foi possível determinar a origem do documento enviado'
