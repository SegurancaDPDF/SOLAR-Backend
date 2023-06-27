import reversion
from django.db import models
from processo.processo.models import FaseTipo
from djdocuments.models import TipoDocumento
from evento.models import Categoria
from core.models import TipoEvento


# representa um modelo de dados que será usado para armazenar informacoes
class IndicadorMeritocracia(models.Model):
    nome = models.CharField(max_length=100, null=False, blank=False)

    tipos_agendas = models.ManyToManyField(Categoria, blank=True)

    tipos_fases_processuais = models.ManyToManyField(FaseTipo, blank=True)

    tipos_documentos = models.ManyToManyField(TipoDocumento, blank=True)

    tipos_atividades = models.ManyToManyField(TipoEvento, blank=True)

    audiencia_com_acordo = models.BooleanField(default=False)
    audiencia_sem_acordo = models.BooleanField(default=False)

    ativo = models.BooleanField(default=True)

    # retorna uma representação em string do objeto IndicadorMeritocracia
    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Indicador de Meritocracia'
        verbose_name_plural = 'Indicadores de Meritocracia'
        ordering = ['-ativo', 'nome']


reversion.register(IndicadorMeritocracia)
