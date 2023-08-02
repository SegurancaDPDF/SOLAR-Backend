from django.apps import AppConfig


class AssistidoAppConfig(AppConfig):
    name = 'assistido'
    verbose_name = "Assistido"

    def ready(self):
        from . import signals  # noqa