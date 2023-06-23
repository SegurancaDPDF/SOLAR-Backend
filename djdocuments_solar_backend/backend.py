# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import logging

import requests
from constance import config
from django.contrib.auth.hashers import check_password as django_check_password
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sites.models import Site
from django.urls import reverse
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from urlobject import URLObject

from atendimento.atendimento.models import Atendimento
from contrib.models import Defensoria
from djdocuments.backends import DjDocumentsBaseBackend
from notificacoes import tasks
from processo.processo.models import Manifestacao, ManifestacaoDocumento

logger = logging.getLogger(__name__)


def _get_defensor_usuario(usuario):
    defensor = None

    if not isinstance(usuario, AnonymousUser):
        servidor = usuario.servidor if hasattr(usuario, 'servidor') else None

        if servidor:
            defensor = servidor.defensor if hasattr(servidor, 'defensor') else None

    return defensor


class SolarDefensoriaBackend(DjDocumentsBaseBackend):
    group_name_atrib = 'nome'
    group_label = 'Defensoria'
    nome_sistema = 'SOLAR'

    def notificar_documento_assinado_e_finalizado(self, document, usuario_atual):
        """Notifica quando documento for marcado como finalizado"""

        if config.NOTIFICAR_DOCUMENTO_FINALIZADO:

            # gera url callback com parametros get (query)
            url_callback = URLObject(
                reverse('ged:painel_geral_documentos_finalizados')
            ).with_query(
                '{}={}'.format('doc', document.pk_uuid)
            )

            # obtem endereço completo pelo site atual
            url_callback = '{}{}'.format(
                Site.objects.get_current().domain,
                url_callback
            )

            # cria a tarefa no celery para notificar usuarios sobre a finalização do documento
            tasks.notificar_documento_assinado_e_finalizado.apply_async(kwargs={
                'user_remetente_id': usuario_atual.id,
                'url_callback': url_callback,
                'documento_id': document.id,
            }, queue='sobdemanda')

    def notificar_documento_pronto_para_assinar(self, document, usuario_atual):
        """Notifica quando documento for marcado como pronto para assinar"""

        if config.NOTIFICAR_DOCUMENTO_PRONTO_PARA_ASSINAR:

            # gera url callback com parametros get (query)
            url_callback = URLObject(
                reverse('ged:painel_geral_assinaturas_pendentes')
            ).with_query(
                '{}={}'.format('doc', document.pk_uuid)
            )

            # obtem endereço completo pelo site atual
            url_callback = '{}{}'.format(
                Site.objects.get_current().domain,
                url_callback
            )

            # cria a tarefa no celery para notificar usuarios que o documento está pronto para assinar
            tasks.notificar_documento_pronto_para_assinar.apply_async(kwargs={
                'user_remetente_id': usuario_atual.id,
                'url_callback': url_callback,
                'documento_id': document.id,
            }, queue='sobdemanda')

    def notificar_pendencia_assinatura(self, assinatura, usuario_atual):
        """Notifica quando novo assinante for adicionado em documento pronto para assinar"""

        if config.NOTIFICAR_DOCUMENTO_ASSINATURA_PENDENTE:

            # gera url callback com parametros get (query)
            url_callback = URLObject(
                reverse('ged:painel_geral_assinaturas_pendentes')
            ).with_query(
                '{}={}'.format('doc', assinatura.documento.pk_uuid)
            )

            # obtem endereço completo pelo site atual
            url_callback = '{}{}'.format(
                Site.objects.get_current().domain,
                url_callback
            )

            # cria a tarefa no celery para notificar usuario sobre pendencia de assinatura
            tasks.notificar_pendencia_assinatura.apply_async(kwargs={
                'user_remetente_id': usuario_atual.id,
                'url_callback': url_callback,
                'assinatura_id': assinatura.id,
            }, queue='sobdemanda')

    def get_nome_instituicao(self):
        return config.NOME_INSTITUICAO

    def check_password(self, password_str, user_instance):
        if config.USAR_API_EGIDE_AUTH:
            # nao estou seguro se isso eh o suficiente para manter a seguranca
            # ao autenticar no egide
            headers = {
                'User-Agent': 'SOLAR',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest'
            }
            data = {
                'grant_type': 'password',
                'username': user_instance.username,
                'password': password_str,
                'client_id': settings.EGIDE_CLIENT_ID,
                'client_secret': settings.EGIDE_CLIENT_SECRET,
            }
            s = requests.Session()
            response = s.post(
                url=settings.EGIDE_TOKEN_URL,
                data=data,
                headers=headers
            )
            response_dict = response.json()

            if 'access_token' in response_dict and 'created_at' in response_dict:
                return True
            return False
        return django_check_password(password_str, user_instance.password)

    def get_grupos(self, excludes=None):
        return self.get_grupo_model().objects.filter(ativo=True)

    def grupo_ja_assinou(self, document, usuario, **kwargs):
        grupo_assinante = kwargs.get('grupo_assinante')
        if grupo_assinante:
            grupos = [grupo_assinante.pk]
        else:
            grupos = tuple(self.get_grupos_usuario(usuario).values_list('id', flat=True))

        possui_assinaturas_concluidas = document.assinaturas.filter(grupo_assinante__in=grupos,
                                                                    esta_assinado=True).exists()
        nao_possui_assinaturas_pendentes = not document.assinaturas.filter(grupo_assinante__in=grupos,
                                                                           esta_assinado=False).exists()

        ja_assinou = possui_assinaturas_concluidas and nao_possui_assinaturas_pendentes
        return ja_assinou

    def get_usuarios_grupo(self, grupo, **kwargs):
        agora = timezone.now()
        if not isinstance(grupo, self.get_grupo_model()):
            grupo = self.get_grupo_model().objects.get(pk=grupo)

        usuarios = User.objects.filter(
            Q(servidor__defensor__all_atuacoes__defensoria=grupo) &
            Q(servidor__defensor__all_atuacoes__ativo=True) &
            Q(servidor__defensor__all_atuacoes__data_inicial__lte=agora) &
            (
                Q(servidor__defensor__all_atuacoes__data_final__gte=agora) |
                Q(servidor__defensor__all_atuacoes__data_final=None)
            ) &
            Q(servidor__defensor__all_atuacoes__pode_assinar_ged=True)
        )

        return usuarios

    def pode_visualizar(self, document, usuario, **kwargs):
        agora = timezone.now()
        usuario_atual_pode_visualizar = document.assinaturas.filter(
            Q(grupo_assinante__all_atuacoes__ativo=True) &
            Q(grupo_assinante__all_atuacoes__data_inicial__lte=agora) &
            (
                Q(grupo_assinante__all_atuacoes__data_final__gte=agora) |
                Q(grupo_assinante__all_atuacoes__data_final=None)
            ) &
            Q(grupo_assinante__all_atuacoes__defensor__servidor__usuario=usuario)
        ).exists()

        return usuario_atual_pode_visualizar

    def pode_excluir_documento(self, document, usuario, **kwargs):
        SUPER_USER_CAN_EXCLUDE_DOCUMENT = False
        try:
            from constance import config
        except ImportError:
            pass
        else:
            if hasattr(config, 'SUPER_USER_CAN_EXCLUDE_DOCUMENT'):
                SUPER_USER_CAN_EXCLUDE_DOCUMENT = config.SUPER_USER_CAN_EXCLUDE_DOCUMENT

        pode_excluir = False
        msg = u'{username} não pode excluir este documento "{pk_uuid}'.format(
            username=usuario.username, pk_uuid=document.pk_uuid
        )

        from processo.processo.models import ManifestacaoDocumento

        if usuario.is_superuser and SUPER_USER_CAN_EXCLUDE_DOCUMENT:
            pode_excluir = True
            msg = u'{username} é um superusuário e pode excluir o documento pk_uuid {pk_uuid}: '.format(
                username=usuario.username, pk_uuid=document.pk_uuid)
        elif document.eh_modelo_padrao:
            # nao pode excluir usuario normal quando ele eh_modelo_padrao:
            # pode_excluir = False
            msg = u'Documento Modelo só pode ser excluído por administradores do Solar'
        elif document.esta_finalizado:
            # nao pode ser excluido quando:
            # document.esta_assinado == True e document.assinatura_hash not None (ja possui hash publico gerado)
            # pode_excluir = False
            msg = 'Documento finalizado não pode ser excluído'
        elif ManifestacaoDocumento.objects.documento_vinculado_manifestacao_ativa(document.id):
            # se houver vínculo com ManifestacaoDocumento ativo não pode excluir
            msg = 'Remova este documento do Peticionamento {} para poder excluir'.format(
                ManifestacaoDocumento.objects.documento_vinculado_manifestacao_ativa(document.id)
                )

        # pode excluir se:
        elif document.criado_por == usuario:
            # tiver passado nas etapas verificacao anteriores e
            # for o mesmo usuario que criou o documento
            pode_excluir = True
            msg = '{username} é o criador deste documento'.format(username=usuario.username)
        elif document.grupo_dono_id in self.get_grupos_usuario(usuario=usuario).values_list('pk', flat=True):
            # tiver passado nas etapas verificacao anteriores e
            # for o usuario faz parte da DEFENSORIA dona do documento
            pode_excluir = True
            msg = '{username} está no grupo_dono'.format(username=usuario.username)
        else:
            msg = '{username} não tem permissão para excluir este documento'.format(username=usuario.username)

        return pode_excluir, msg

    def excluir_documento(self, document, usuario, agora=timezone.now()):
        """
        Utilizado para excluir(desativar) o GED e Revogar suas Assinaturas.
        Só irá executar caso o Usuário tenha permissão no referido GED.
        :param document:
        :param usuario:
        :param agora:
        :return:
        """
        sucesso = False

        if self.pode_excluir_documento(document, usuario):
            sucesso = document.delete(current_user=usuario, agora=agora)

        return sucesso

    def pode_editar(self, document, usuario, **kwargs):
        SUPER_USER_CAN_EDIT_DOCUMENT = False
        try:
            from constance import config
        except ImportError:
            pass
        else:
            if hasattr(config, 'SUPER_USER_CAN_EDIT_DOCUMENT'):
                SUPER_USER_CAN_EDIT_DOCUMENT = config.SUPER_USER_CAN_EDIT_DOCUMENT

        if usuario.is_superuser and SUPER_USER_CAN_EDIT_DOCUMENT:
            msg = 'Usuario "{username}" é um superusuario e pode editar do documento pk_uuid "{pk_uuid}": '.format(
                username=usuario.username, pk_uuid=document.pk_uuid)
            return True, msg
        if document.eh_modelo_padrao:
            # nao pode editar usuario normal quando ele eh_modelo_padrao:
            return False, "Documento padrão só pode ser modificado por administradores do Solar"
        if document.esta_finalizado:
            # nao pode editar quando:
            # document.esta_assinado == True e document.assinatura_hash not None (ja possui hash publico gerado)
            return False, "Documento já foi finalizado"
        if document.assinaturas.filter(ativo=True, esta_assinado=True).exists():
            # nao pode editar quando:
            # alguem ja assinou o documento
            return False, "Este documento não pode ser editado porque ele já foi assinado por uma ou mais defensorias"
        # pode editar se:
        if document.criado_por == usuario:
            # tiver passado nas etapas verificacao anteriores e
            # for o mesmo usuario que criou o documento
            return True, 'Usuario "{username}" atual é o criador deste documento'.format(username=usuario.username)
        if document.grupo_dono_id in self.get_grupos_usuario(usuario=usuario).values_list('pk', flat=True):
            # tiver passado nas etapas verificacao anteriores e
            # for o usuario faz parte da DEFENSORIA dona do documento
            return True, 'Usuario "{username}" atual está no grupo_dono'.format(username=usuario.username)
        return False, "Nao pode editar"

    def pode_incluir_imagens_externas(self):
        GED_PODE_INCLUIR_IMAGENS_EXTERNAS = True
        if hasattr(config, 'GED_PODE_INCLUIR_IMAGENS_EXTERNAS'):
            GED_PODE_INCLUIR_IMAGENS_EXTERNAS = config.GED_PODE_INCLUIR_IMAGENS_EXTERNAS
        return GED_PODE_INCLUIR_IMAGENS_EXTERNAS

    def exibir_formulas_ged(self):
        GED_EXIBIR_FORMULAS_MODELO = False
        if hasattr(config, 'GED_EXIBIR_FORMULAS_MODELO'):
            GED_EXIBIR_FORMULAS_MODELO = config.GED_EXIBIR_FORMULAS_MODELO
        return GED_EXIBIR_FORMULAS_MODELO

    def pode_remover_assinatura(self, document, assinatura, usuario_atual, **kwargs):
        if not document == assinatura.documento:
            return False, "Assinatura {assinatura} não é referente ao documento {documento}".format(
                assinatura=assinatura.pk, documento=document.pk)
        if document.esta_finalizado:
            # nao pode remover assinatura quando:
            # document.esta_assinado == True e document.assinatura_hash not None (ja possui hash publico gerado)
            return False, "Documento já foi finalizado"
        if document.grupo_dono_id == assinatura.grupo_assinante_id:
            return False, 'Não é possivel remover assinatura pendente proprio dono "{grupo_dono}" do documento'.format(
                grupo_dono=self.get_grupo_name(document.grupo_dono))

        if document.grupo_dono_id in self.get_grupos_usuario(usuario=usuario_atual).values_list('pk', flat=True):
            return True, 'Usuario "{username}" atual está no grupo_dono'.format(username=usuario_atual.username)
        msg = 'Você não possui permissão para remover assinatura pendente de "{grupo_dono}"'.format(
            grupo_dono=self.get_grupo_name(document.grupo_dono))
        return False, msg

    def pode_revogar_assinatura(self, document, usuario: User):

        if not document.esta_assinado:
            return False, 'Documento não está assinado'

        if not (usuario.is_superuser or usuario == document.finalizado_por):
            return False, 'Usuário não tem permissão'

        if document.pdfs.exists():
            return False, 'Documento já baixado em PDF'

        if self.existe_em_indeferimento(document):
            return False, 'Documento está vinculado a um Indeferimento'

        if self.existe_em_pedido_de_apoio(document):
            return False, 'Documento está vinculado a um Pedido de Apoio'

        if self.existe_em_manifestacao(document):
            return False, 'Documento está vinculado a um Peticionamento'

        return True, ''

    def existe_em_manifestacao(self, document) -> bool:
        return ManifestacaoDocumento.objects.filter(
            origem=ManifestacaoDocumento.ORIGEM_ATENDIMENTO,
            origem_id__in=document.documento_set.all().values_list('id'),
            desativado_em=None,
            manifestacao__situacao__in=[Manifestacao.SITUACAO_NAFILA, Manifestacao.SITUACAO_PROTOCOLADO],
            manifestacao__desativado_em=None
        ).exists()

    def existe_em_pedido_de_apoio(self, document) -> bool:
        return document.documento_set.filter(
            atendimento__filhos__tipo=Atendimento.TIPO_NUCLEO
        ).exists()

    def existe_em_indeferimento(self, document) -> bool:
        return document.core_documentos.ativos().exists()

    def pode_criar_documento_para_grupo(self, usuario, grupo):
        agora = timezone.now()
        pode_criar = False
        defensor = _get_defensor_usuario(usuario)
        if defensor:
            pode_criar = defensor.all_atuacoes.filter(
                Q(ativo=True) &
                Q(defensoria=grupo) &
                Q(data_inicial__lte=agora) &
                (
                    Q(data_final__gte=agora) |
                    Q(data_final=None)
                )
            ).exists()
        if not pode_criar:
            msg = 'Você nao possui permissão para criar um documento para "{}"'.format(self.get_grupo_name(grupo))
            logger.info(msg="pode_criar_documento_para_grupo: {}".format(msg))
            return False, msg
        else:
            msg = 'Permissao de criação concedida'
            logger.info(msg="pode_criar_documento_para_grupo: {}".format(msg))
            return True, msg

    def pode_assinar(self, document, usuario, **kwargs):
        """Verifica se o GED pode ser assinado"""

        # se o documento estiver ativo
        if document.esta_ativo:

            grupo_assinante = kwargs.get('grupo_assinante')
            defensor = _get_defensor_usuario(usuario)
            pode = False

            if defensor:
                agora = kwargs.get('agora', None) or timezone.now()

                q = Q()
                q &= Q(ativo=True)
                q &= Q(data_inicial__lte=agora)

                if grupo_assinante:
                    q &= Q(defensoria_id=grupo_assinante.pk)

                q &= Q(data_final__gte=agora) | Q(data_final=None)
                q &= Q(pode_assinar_ged=True)

                defensorias_ids = defensor.all_atuacoes.filter(q).values_list('defensoria_id', flat=True)
                if defensorias_ids:
                    if document.grupos_assinates.filter(id__in=defensorias_ids).exists():
                        pode = True

        return pode

    def get_grupos_usuario(self, usuario):
        agora = timezone.now()
        defensorias = Defensoria.objects.none()
        defensor = _get_defensor_usuario(usuario)

        if defensor:
            #
            # defensorias = usuario.servidor.defensor.all_atuacoes.filter(
            #     Q(ativo=True) &
            #     Q(data_inicial__lte=agora) &
            #     (
            #         Q(data_final__gte=agora) |
            #         Q(data_final=None)
            #     )
            # )

            defensorias = Defensoria.objects.filter(
                Q(all_atuacoes__defensor=defensor) &
                Q(all_atuacoes__ativo=True) &
                Q(all_atuacoes__data_inicial__lte=agora) &
                (
                    Q(all_atuacoes__data_final__gte=agora) |
                    Q(all_atuacoes__data_final=None)
                )
            ).distinct()

        return defensorias

        # def pode_finalizar_documento(self, documento, usuario):
        #     agora = timezone.now()
        #     if usuario.servidor.defensor.supervisor:
        #         defensor = usuario.servidor.defensor.supervisor
        #     else:
        #         defensor = usuario.servidor.defensor
        #
        #     pode_criar = defensor.all_atuacoes.filter(
        #         Q(ativo=True) &
        #         Q(defensoria=grupo) &
        #         Q(data_inicial__lte=agora) &
        #         (
        #             Q(data_final__gte=agora) |
        #             Q(data_final=None)
        #         )
        #     ).exists()
        #     if not pode_criar:
        #         msg = 'Você nao possui permissão para criar um documento para "{}"'.format(self.get_grupo_name(grupo))
        #         logger.info(msg="pode_criar_documento_para_grupo: {}".format(msg))
        #         return False, msg
        #     else:
        #         msg = 'Permissao de criação concedida'
        #         logger.info(msg="pode_criar_documento_para_grupo: {}".format(msg))
        #         return True, msg
