# Importações necessárias
from core.exceptions import CoreBaseException

# Classe base para todas as exceções personalizadas neste código, que herda de CoreBaseException.


class ExceptionBase(CoreBaseException):
    ERROS_DE_CONEXAO = [
        'ConnectionError',
        'HTTPError',
        'RemoteDisconnected'
    ]

# Exceção personalizada para quando o prazo já está fechado no PJe


class PJEAvisoJaFechadoException(ExceptionBase):
    message = 'PJEAvisoJaFechadoException, O prazo já está fechado no PJe.'

    def __str__(self):
        if self.args:
            return 'PJEAvisoJaFechadoException, {0} prazo já fechado no PJe '.format(self.args[0])
        else:
            return self.message

# Exceção personalizada para quando não é possível fazer a consulta de teor de comunicação no PROCAPI


class PROCAPIConsultaTeorComunicacaoError(ExceptionBase):
    message = 'ConsultaTeorComunicacaoError, não foi possível fazer consulta teor comunicação no PROCAPI'

    def __str__(self):
        if self.args:
            return 'ConsultaTeorComunicacaoError, {0} '.format(self.args[0])
        else:
            return self.message

# Exceção personalizada para quando o serviço de enviar manifestação está indisponível


class ManifestacaoServiceUnavailable(ExceptionBase):
    message = 'O serviço de enviar manifestação está fora do Ar.'

# Exceção personalizada para quando os documentos enviados na manifestação não correspondem ao total enviado pelo Solar


class ManifestacaoTotalDocumentosInvalid(ExceptionBase):
    message = 'Os documentos enviados na manifestação não correspondem ao total enviado pelo Solar.'

# Exceção personalizada para falhas na consulta ao serviço de enviar manifestação


class ManifestacaoRequestFailed(ExceptionBase):
    message = 'Falha na consulta ao serviço de enviar manifestação.'
