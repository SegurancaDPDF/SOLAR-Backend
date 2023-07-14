from django.apps import AppConfig


class ContribAppConfig(AppConfig):
    name = 'contrib'
    verbose_name = "Contrib"

    def ready(self):
        from . import signals  # noqa
