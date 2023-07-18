# Bibliotecas de terceiros
from django.apps import AppConfig

# Classe responsável por configurar a aplicação "procapi_client"


class ProcAPIClientAppConfig(AppConfig):
    name = 'procapi_client'
    verbose_name = "ProcAPI Client"

    def ready(self):
        from . import signals  # noqa
