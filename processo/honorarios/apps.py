from django.apps import AppConfig


class ProcessoHonorariosAppConfig(AppConfig):
    name = 'processo.honorarios'
    verbose_name = "Honorarios"

    def ready(self):
        from . import signals  # noqa
