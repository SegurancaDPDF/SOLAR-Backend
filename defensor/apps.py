from django.apps import AppConfig


class DefensorAppConfig(AppConfig):
    name = 'defensor'
    verbose_name = "Defensor"

    def ready(self):
        from . import signals  # noqa
