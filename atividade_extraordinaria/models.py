# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Solar
from core.models import Evento as CoreEvento, TipoEvento as CoreTipoEvento

# Modulos locais
from . import managers

# Herda da classe `CoreTipoEvento` e adiciona funcionalidades específicas relacionadas a esse tipo de evento.


class AtividadeExtraordinariaTipo(CoreTipoEvento):
    class Meta:
        proxy = True
        verbose_name = u'Atividade Extraordinária Tipo'
        verbose_name_plural = u'Atividades Extraordinárias Tipos'

    objects = managers.AtividadeExtraordinariaTipoManager()

# Herda da classe `CoreEvento` e adiciona funcionalidades específicas relacionadas a essa atividade.


class AtividadeExtraordinaria(CoreEvento):

    class Meta:
        proxy = True
        verbose_name = u'Atividade Extraordinária'
        verbose_name_plural = u'Atividades Extraordinárias'

    objects = managers.AtividadeExtraordinariaManager()

    def __str__(self):
        return '{} - {}'.format(self.data_referencia, self.historico)

    def as_dict(self):
        return {
            'id': self.pk,
            'numero': self.numero,
            'titulo': self.titulo,
            'historico': self.historico,
            'data_referencia': self.data_referencia,
            'data_referencia_pt_br': self.data_referencia.strftime('%d/%m/%Y'),
            'area': {
                'id': self.area.id,
                'nome': self.area.nome,
            } if self.area else None,
            'participantes': [{
                'id': participante.usuario.id,
                'nome': participante.usuario.get_full_name(),
            } for participante in self.participante_set.ativos()],
            'setor_criacao': {
                'id': self.setor_criacao.id,
                'nome': self.setor_criacao.nome,
            },
            'tipo': {
                'id': self.tipo.id,
                'nome': self.tipo.nome,
                'eh_brinquedoteca': self.tipo.eh_brinquedoteca,
            },
            'complemento': self.complemento,
            'cadastrado_em': self.cadastrado_em,
            'cadastrado_por': {
                'nome': self.cadastrado_por.get_full_name(),
                'username': self.cadastrado_por.username,
            },
            'encerrado_em': self.encerrado_em,
            'encerrado_por': {
                'nome': self.encerrado_por.get_full_name(),
                'username': self.encerrado_por.username,
            } if self.encerrado_por else None,
        }
