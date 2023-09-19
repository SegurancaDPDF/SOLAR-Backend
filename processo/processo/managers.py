# -*- coding: utf-8 -*-

# Bibliotecas de terceiros
from django.db.models import Manager

from core.managers import AuditoriaBaseQuerySet

from . import models


class ManifestacaoQuerySet(AuditoriaBaseQuerySet):
    def situacao_analise(self):
        return self.filter(situacao=models.Manifestacao.SITUACAO_ANALISE)

    def situacao_nafila(self):
        return self.filter(situacao=models.Manifestacao.SITUACAO_NAFILA)

    def situacao_protocolado(self):
        return self.filter(situacao=models.Manifestacao.SITUACAO_PROTOCOLADO)

    def situacao_erro(self):
        return self.filter(situacao=models.Manifestacao.SITUACAO_ERRO)


class ManifestacaoManager(Manager.from_queryset(ManifestacaoQuerySet)):
    pass


class ManifestacaoDocumentoQuerySet(AuditoriaBaseQuerySet):
    pass


class ManifestacaoDocumentoManager(Manager.from_queryset(ManifestacaoDocumentoQuerySet)):
    def documento_vinculado_manifestacao_ativa(self, documento_online_id):
        """Verifica se o documento_online_id é usado em alguma ManifestacaoDocumento ativa"""

        manifestacao_id = None

        # busca o DocumentoAtendimento pelo documento_online_id
        from atendimento.atendimento.models import \
            Documento as DocumentoAtendimento
        documento_atendimento = DocumentoAtendimento.objects.filter(documento_online_id=documento_online_id).values('id').first()

        # se encontrou o DocumentoAtendimento
        if documento_atendimento:
            # busca a ManifestacaoDocumento em Manifestacoes ativas
            manifestacao_documento = self.filter(
                origem_id=documento_atendimento['id'],
                origem=models.ManifestacaoDocumento.ORIGEM_ATENDIMENTO,
                manifestacao__desativado_em=None
            ).ativos().values('manifestacao_id').first()

            if manifestacao_documento:
                # retorna o manifestacao_id
                manifestacao_id = manifestacao_documento['manifestacao_id']

        return manifestacao_id
