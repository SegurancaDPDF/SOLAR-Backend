from django.apps import AppConfig


class PropacAppConfig(AppConfig):
    name = 'propac'
    verbose_name = "Propac"

    def ready(self):
        from . import signals  # noqa
