# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from cacheops import invalidate_model
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed, post_save
from django.dispatch.dispatcher import receiver
from .models import Servidor, Endereco, EnderecoHistorico, Papel


@receiver(post_save, sender=User)
def post_save_user(sender, instance, **kwargs):
    if hasattr(instance, 'servidor') and instance.servidor.id:
        # ATENÇÃO! Não use instance.servidor.save() pois gerará um RecursionError
        Servidor.objects.filter(pk=instance.servidor.id).update(ativo=instance.is_active, nome=instance.get_full_name())


@receiver(post_save, sender=Endereco)
def post_save_endereco(sender, instance, **kwargs):

    EnderecoHistorico(
        endereco_id=instance.id,
        logradouro=instance.logradouro,
        numero=instance.numero,
        complemento=instance.complemento,
        cep=instance.cep,
        bairro=instance.bairro,
        municipio=instance.municipio,
        tipo_area=instance.tipo_area,
        principal=instance.principal,
        tipo=instance.tipo,
        cadastrado_em=instance.cadastrado_em,
        modificado_em=instance.modificado_em,
        desativado_em=instance.desativado_em,
        cadastrado_por=instance.cadastrado_por,
        modificado_por=instance.modificado_por,
        desativado_por=instance.desativado_por
    ).save()


def grupos_changed(sender, **kwargs):
    """
    Intercepta alteração dos grupos de Papel e aplica a todos os usuários vinculados
    """
    if kwargs['action'] in ['post_add', 'post_remove']:
        papel = kwargs['instance']
        grupos = papel.grupos.all()
        for servidor in papel.servidores.all():
            servidor.usuario.groups.clear()
            servidor.usuario.groups.add(*grupos)

    invalidate_model(User)
    invalidate_model(Servidor)


m2m_changed.connect(grupos_changed, sender=Papel.grupos.through)
