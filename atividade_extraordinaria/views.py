# -*- coding: utf-8 -*-
# Importações necessárias
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import json as simplejson
from datetime import datetime, time, timedelta

# Bibliotecas de terceiros
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.views.generic import ListView, TemplateView
from djdocuments.views.documentos import create_document_from_document_template

# Solar
from atendimento.atendimento.services import preencher_campos_ged
from contrib.models import Defensoria, Servidor, Area
from core.models import (
    Documento as CoreDocumento,
    Participante as CoreParticipante,
)
from core.views import EventoUpdateView
from defensor.models import Atuacao
from nucleo.nadep.models import EstabelecimentoPenal
from nucleo.nucleo.models import Formulario, Pergunta, Resposta

from . import forms
from . import models

# Classe responsável por exibir uma lista de atividades extraordinárias


class AtividadeExtraordinariaListView(ListView):
    queryset = models.AtividadeExtraordinaria.objects.prefetch_related(
        'participantes'
    ).select_related(
        'tipo',
        'setor_criacao'
    ).ativos()

    model = models.AtividadeExtraordinaria
    ordering = ['-data_referencia']
    paginate_by = 50
    template_name = "atividade_extraordinaria/buscar.html"

    def get_context_data(self, **kwargs):
        # Adiciona o formulário de busca no contexto

        context = super(AtividadeExtraordinariaListView, self).get_context_data(**kwargs)

        context.update({
            'form': forms.BuscarAtividadeExtraordinariaForm(self.request.GET),
        })

        return context

    def get_queryset(self):

        queryset = super(AtividadeExtraordinariaListView, self).get_queryset()
        q = Q()

        form = forms.BuscarAtividadeExtraordinariaForm(self.request.GET)

        if form.is_valid():

            data = form.cleaned_data

            if data.get('data_inicial') and data.get('data_final'):
                q &= Q(data_referencia__range=[data['data_inicial'], datetime.combine(data['data_final'], time.max)])

            if data.get('participante'):
                q &= Q(participantes=data['participante'])

            if data.get('defensoria'):
                q &= Q(setor_criacao=data['defensoria'])

            if data.get('tipo'):
                q &= Q(tipo=data['tipo'])

            if data.get('filtro'):
                if data['filtro'].isnumeric():
                    q &= Q(id=data['filtro'])
                else:
                    q &= Q(titulo__icontains=data['filtro'])

            # Filtro para perguntas de formulários dinâmicos
            if self.request.GET.get('pergunta'):
                q &= Q(respostas__pergunta=self.request.GET['pergunta'])

            # Filtro para respostas de formulários dinâmicos
            if self.request.GET.get('resposta'):
                q &= Q(respostas__texto=self.request.GET['resposta'])

        if len(q):
            return queryset.filter(q)
        else:
            return queryset.none()

# Classe responsável por atualizar uma atividade extraordinária


class AtividadeExtraordinariaUpdateView(EventoUpdateView):
    form_class = forms.EditarAtividadeExtraordinariaForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtém lista de formularios que podem ser usados nas at. extra.
        # Filtra os formulários ativos que estão associados a documentos e exibem em atividades extraordinárias.
        formularios = Formulario.objects.filter(
            exibir_em_atividade_extraordinaria=True,
            core_modelos_documentos__isnull=False,
            core_modelos_documentos__desativado_em=None
        ).distinct().only('id', 'texto')
        # Filtra os formulários preenchidos para a atividade atual.
        formularios_preenchidos = formularios.filter(
            pergunta__resposta__evento=self.object
        )

        context['formularios'] = formularios
        context['formularios_preenchidos'] = formularios_preenchidos

        return context

    def get_success_url(self):
        kwargs = {'pk': self.object.pk}
        return reverse('atividade_extraordinaria:editar', kwargs=kwargs)

# Classe responsável por encerrar uma atividade extraordinária


class AtividadeExtraordinariaCloseView(AtividadeExtraordinariaUpdateView):
    form_class = forms.EncerrarAtividadeExtraordinariaForm

    def get_initial(self):
        initial = super(AtividadeExtraordinariaCloseView, self).get_initial()
        initial.update({
            'data_referencia': datetime.now()
        })
        return initial

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.encerrado_em = datetime.now()
        self.object.encerrado_por = self.request.user
        return super(AtividadeExtraordinariaCloseView, self).form_valid(form)

# Classe responsável por exibir um formulário de atividade extraordinária


class FormularioView(TemplateView):
    template_name = 'atividade_extraordinaria/formulario.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        # Carrega dados necessários para exibir as perguntas e as respostas
        atividade = models.AtividadeExtraordinaria.objects.get(id=kwargs.get('pk'))
        formulario = Formulario.objects.ativos().get(id=kwargs.get('formulario_pk'))

        # Carrega respostas salvas
        respostas = {}
        for resposta in Resposta.objects.filter(evento=atividade).values('pergunta_id', 'texto'):
            respostas[resposta['pergunta_id']] = resposta['texto']

        # Cria lista das sessões do formulário e respectivas perguntas e respostas salvas
        sessoes = []
        for sessao in formulario.perguntas.filter(tipo=Pergunta.TIPO_SESSAO):
            sessoes.append({
                'id': sessao.id,
                'texto': sessao.texto,
                'perguntas': [{
                    'id': pergunta.id,
                    'texto': pergunta.texto,
                    'texto_complementar': pergunta.texto_complementar,
                    'tipo': pergunta.tipo,
                    'classe_css': pergunta.classe_css,
                    'alternativas': pergunta.alternativas,
                    'alternativas_url': pergunta.lista_url,
                    'resposta': respostas.get(pergunta.id, ''),
                    'respostas': respostas.get(pergunta.id, '').split(',')
                } for pergunta in sessao.pergunta_set.ativos()]
            })

        context.update({
            'formulario': formulario,
            'sessoes': sessoes
        })

        return context

    def post(self, request, *args, **kwargs):

        # Carrega dados necessários para salvar as respostas
        acao = request.POST.get('acao')
        atividade = models.AtividadeExtraordinaria.objects.get(id=kwargs.get('pk'))
        formulario = Formulario.objects.ativos().get(id=kwargs.get('formulario_pk'))
        perguntas = formulario.perguntas.exclude(tipo=Pergunta.TIPO_SESSAO).values('id', 'tipo')

        # Cria/atualiza resposta para cada pergunta do formulário
        for pergunta in perguntas:

            # Força conversão para string p/ obter a key do POST corretamente
            pergunta_key = str(pergunta['id'])

            if pergunta['tipo'] == Pergunta.TIPO_LISTA_MULTIPLA:
                resposta = ','.join(request.POST.getlist(pergunta_key))
            else:
                resposta = request.POST.get(pergunta_key, '')

            Resposta.objects.update_or_create(
                evento=atividade,
                pergunta_id=pergunta_key,
                defaults={
                    'texto': resposta
                }
            )

        if acao == 'salvar_e_assinar':
            if self.criar_documento_ged(atividade=atividade, formulario=formulario) is None:
                return HttpResponseRedirect(self.request.path_info)

        return redirect(reverse('atividade_extraordinaria:editar', kwargs={'pk': kwargs.get('pk')}))

    def criar_documento_ged(self, atividade, formulario):
        '''
        Cria documento GED a partir das respostas do formulário
        '''

        if not formulario.core_modelos_documentos.exclude(ged_modelo=None).exists():
            messages.error(self.request, 'Não existe modelo configurado para criar um documento GED!')
            return None

        perguntas = formulario.perguntas.filter(tipo=Pergunta.TIPO_SESSAO).order_by('posicao')
        respostas = atividade.respostas.order_by('pergunta__sessao_posicao', 'pergunta__posicao')

        modelo = formulario.core_modelos_documentos.exclude(ged_modelo=None).first()
        modelo_ged = modelo.ged_modelo

        # Verifica se existe algum documento anterior e inativa antes de criar um novo
        documento_anterior = CoreDocumento.objects.ativos().filter(
            evento=atividade,
            tipo=modelo.tipo_documento,
            modelo=modelo,
        ).first()

        if documento_anterior:
            documento_anterior.documento.delete(current_user=self.request.user)
            documento_anterior.desativar(usuario=self.request.user)

        context_conteudo = {
            'defensoria': atividade.setor_criacao,
            'atividade': atividade,
        }

        for sessao in perguntas.order_by('posicao'):
            context_conteudo['respostas_{}'.format(sessao.posicao+1)] = respostas.filter(pergunta__sessao=sessao)

        # TODO: Identificar range de sessões de forma dinâmica
        respostas_agrupadas_por_sessao = []
        for sessao in perguntas.filter(posicao__range=[1, 16]).order_by('posicao'):
            respostas_agrupadas_por_sessao.append({
                'nome': sessao.texto,
                'respostas': respostas.filter(pergunta__sessao=sessao.id).order_by('pergunta__posicao')
            })

        context_conteudo['sessoes'] = respostas_agrupadas_por_sessao

        # Identifica pergunta e resposta com os dados do estabelecimento penal
        # TODO: Identificar model de forma dinânica
        pergunta_estabelecimento = formulario.perguntas.filter(lista_url='/api/v1/estabelecimentos-penais/').first()

        if pergunta_estabelecimento:
            try:
                nome_estabelecimento = respostas.filter(pergunta=pergunta_estabelecimento).first().texto
                context_conteudo['estabelecimento'] = EstabelecimentoPenal.objects.get(nome=nome_estabelecimento)
            except EstabelecimentoPenal.DoesNotExist:
                messages.error(self.request, 'O estabelecimento penal {} não está cadastrado! Escolha uma das opções válidas.'.format(nome_estabelecimento))  # noqa: E501
                return None

        documento_online = create_document_from_document_template(
            current_user=self.request.user,
            grupo=atividade.setor_criacao,
            documento_modelo=modelo_ged,
            assunto=modelo_ged.modelo_descricao
        )

        preencher_campos_ged(
            documento=documento_online,
            context_conteudo=context_conteudo,
            fallback_to_conteudo=True
        )

        documento_online.esta_pronto_para_assinar = True
        documento_online.save()

        documento = CoreDocumento.objects.create(
            evento=atividade,
            tipo=modelo.tipo_documento,
            modelo=modelo,
            nome=documento_online.assunto,
            documento=documento_online
        )

        return documento


@login_required
@permission_required('atendimento.view_defensor')
def get_atividades_extraordinarias(request):

    if request.method == 'POST' and request.is_ajax():
        # Verifica se a solicitação é do tipo POST e é assíncrona (AJAX)
        dados = simplejson.loads(request.body)

        if hasattr(request.user.servidor, 'defensor'):
            # Verifica se o usuário logado possui a propriedade "defensor"
            agora = datetime.now()
            defensor = request.user.servidor.defensor
            defensoria = dados.get('defensoria')

            data = dados.get('data')
            data = datetime.strptime(data, '%Y-%m-%dT%H:%M:%S.%fZ') if data else agora
            data -= timedelta(days=30)

            # TODO: Verificar impacto quando usuário está lotado em múltiplas defensorias na mesma comarca
            # filta atuações vigentes do usuário na defensoria selecionada
            atuacoes_usuario = defensor.all_atuacoes.vigentes().filter(
                defensoria__in=defensoria,
                defensoria__pode_cadastrar_atividade_extraordinaria=True
            )

            atuacoes_defensores = Atuacao.objects.vigentes().filter(
                defensoria__in=atuacoes_usuario.values('defensoria_id')
            ).order_by(
                '-defensor__eh_defensor',
                'defensor__servidor__nome'
            )

            # obtém lista de defensorias e transforma em json
            defensorias = Defensoria.objects.filter(id__in=atuacoes_defensores.values('defensoria_id'))

            json_defensorias = [{
                'id': item.id,
                'nome': item.nome
            } for item in defensorias]

            # obtém lista de defensores e transforma em json
            defensores = atuacoes_defensores.values(
                'defensor_id',
                'defensor__eh_defensor',
                'defensor__servidor__usuario_id',
                'defensor__servidor__nome'
            ).distinct()

            json_defensores = [{
                'id': item['defensor_id'],
                'usuario_id': item['defensor__servidor__usuario_id'],
                'nome': item['defensor__servidor__nome'],
                'selecionar': item['defensor__eh_defensor'] or item['defensor__servidor__usuario_id'] == request.user.id
            } for item in defensores]

            # obtém lista de atividades registradas nas defensorias onde o usuário está lotado
            q = Q(setor_criacao__in=atuacoes_usuario.values('defensoria_id'))
            q &= Q(setor_criacao__pode_cadastrar_atividade_extraordinaria=True)
            q &= Q(data_referencia__gte=data)

            # filtro para exibir apenas atividades onde o usuário é participante
            if not dados.get('mostrar_todas', True):
                q &= Q(participantes=request.user)

            atividades = models.AtividadeExtraordinaria.objects.ativos().filter(q).distinct().order_by('-id')
            json_atividades = [atividade.as_dict() for atividade in atividades]

            # verifica se núcleo é multidisciplinar
            eh_multidisciplinar = Defensoria.objects.filter(
                id__in=defensoria,
                nucleo__multidisciplinar=True
            ).exists()

            # verifica se núcleo pode registrar atividades da briquedoteca
            pode_registrar_tipo_brinquedoteca = eh_multidisciplinar and \
                models.AtividadeExtraordinariaTipo.objects.ativos().tipo_brinquedoteca().exists()

            # filtra a lista de Atividades (core.TipoEvento) conforme a Defensoria
            lista_atividades_defensoria = models.AtividadeExtraordinariaTipo.objects.filter(
                defensorias__id__in=defensoria
            ).all().order_by('nome').distinct()

            lista_atividades_permitidas = []
            for row in lista_atividades_defensoria:
                lista_atividades_permitidas.append({
                    'id': row.id,
                    'nome': row.nome,
                    'tipo': row.tipo,
                    'eh_brinquedoteca': row.eh_brinquedoteca,
                })
            # Cria uma lista de tipos de atividades permitidas
            areas = Area.objects.filter(ativo=True).order_by('-id')

            lista_areas = []
            for row in areas:
                lista_areas.append({
                    'id': row.id,
                    'nome': row.nome,
                    'ativo': row.ativo,
                    'penal': row.penal,
                })
            # Obtém a lista de áreas e suas informações
            return JsonResponse({
                'atividades': json_atividades,
                'atividades_tipos': lista_atividades_permitidas,
                'areas': lista_areas,
                'defensorias': json_defensorias,
                'defensores': json_defensores,
                'perms': {
                    'pode_registrar_tipo_brinquedoteca': pode_registrar_tipo_brinquedoteca,
                }
            }, safe=False)

        return JsonResponse({'success': False})


@login_required
@permission_required('atendimento.view_defensor')
def salvar_atividade_extraordinaria(request):
    if request.method == 'POST' and request.is_ajax():

        form_data = request.POST.copy()
        form = forms.AtividadeExtraordinariaForm(
            data=form_data,
            instance=models.AtividadeExtraordinaria(em_edicao=True)
        )

        try:

            atividade_id = form_data.get('id')

            if atividade_id:
                instance = models.AtividadeExtraordinaria.objects.get(pk=atividade_id)
                form = forms.AtividadeExtraordinariaForm(data=form_data, instance=instance)
            # Verifica se o ID da atividade está presente e atualiza a instância do formulário
            if form.is_valid():

                instance = form.save(commit=False)

                # Se data encerramento informada, define usuário atual como quem encerrou
                if instance.encerrado_em:
                    instance.encerrado_por = request.user

                instance.save()

                # Desativa participantes já vinculados antes de vincular os novos
                CoreParticipante.objects.filter(
                    evento=instance
                ).update(
                    desativado_em=datetime.now(),
                    desativado_por=request.user,
                )

                participantes = request.POST.getlist('participantes')

                if participantes:

                    for participante in participantes:

                        if participante.isdigit():

                            servidor = Servidor.objects.get(usuario=participante)

                            CoreParticipante.objects.update_or_create(
                                evento=instance,
                                usuario=servidor.usuario,
                                defaults={
                                    'papel': servidor.papel,
                                    'desativado_em': None,
                                    'desativado_por': None
                                }
                            )

                # Se nenhum participante vinculado, adiciona usuário logado
                if not CoreParticipante.objects.ativos().filter(evento=instance).exists():
                    CoreParticipante.objects.update_or_create(
                        evento=instance,
                        usuario=request.user,
                        defaults={
                            'papel': request.user.servidor.papel,
                            'desativado_em': None,
                            'desativado_por': None
                        }
                    )

                return JsonResponse({
                    'id': instance.id,
                    'success': True
                })

            raise Exception()

        except Exception as e:
            errors = [str(e)] if e.args else form.errors
            return JsonResponse({'success': False, 'errors': errors})

    return JsonResponse({'success': False})


@login_required
@permission_required('atendimento.view_defensor')
# A função lida com a solicitação de exclusão de uma atividade extraordinária.
def excluir_atividade_extraordinaria(request):
    is_success = False
    if request.method == 'POST':
        dados = simplejson.loads(request.body)
        atividade = models.AtividadeExtraordinaria.objects.get(pk=dados.get('atividade_id'))
        # Recupera a atividade extraordinária do banco de dados com base no ID fornecido
        atividade.desativar(usuario=request.user)
        is_success = True
    return JsonResponse({'success': is_success})
