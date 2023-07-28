from django.apps import AppConfig


class AtendimentoAtendimentoAppConfig(AppConfig):
    name = 'atendimento.atendimento'
    verbose_name = "Atendimento"

    def ready(self):
        from . import signals  # noqa
