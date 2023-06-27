# third-party
from celery import shared_task

# application
from . import models


@shared_task(bind=True, retry_backoff=15, max_retries=3)
def indeferimento_gerar_numero_processo(self, id):
    '''
    Gera número do processo de indeferimento
    '''
    indeferimento = models.Indeferimento.objects.get(id=id)
    if not indeferimento.processo.numero:
        return indeferimento.gerar_numero_processo()
