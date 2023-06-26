from django.apps import AppConfig


class EventoAppConfig(AppConfig):
    name = 'evento'
    verbose_name = "Evento"

    def ready(self):
        from . import signals  # noqa
