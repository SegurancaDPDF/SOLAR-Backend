# Bibliotecas de terceiros
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

# Modulos locais
from .models import Indeferimento
from .tasks import indeferimento_gerar_numero_processo


@receiver(post_save, sender=Indeferimento)
def post_save_indeferimento(sender, instance, **kwargs):
    indeferimento_gerar_numero_processo.apply_async(kwargs={
        'id': instance.id,
    }, queue='prioridade')
