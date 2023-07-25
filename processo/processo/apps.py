from django.apps import AppConfig


class ProcessoProcessoAppConfig(AppConfig):
    name = 'processo.processo'
    verbose_name = "Processo"

    def ready(self):
        from . import signals  # noqa
