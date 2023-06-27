from django.apps import AppConfig


class IndeferimentoAppConfig(AppConfig):
    name = 'indeferimento'
    verbose_name = "Indeferimento"

    def ready(self):
        from . import signals  # noqa
