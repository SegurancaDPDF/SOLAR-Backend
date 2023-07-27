from django.apps import AppConfig


class NucleoNadepAppConfig(AppConfig):
    name = 'nucleo.nadep'
    verbose_name = "Nadep"

    def ready(self):
        from . import signals  # noqa
