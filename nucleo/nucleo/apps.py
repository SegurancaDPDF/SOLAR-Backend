from django.apps import AppConfig


class NucleoNucleoAppConfig(AppConfig):
    name = 'nucleo.nucleo'
    verbose_name = "Nucleo"

    def ready(self):
        from . import signals  # noqa
