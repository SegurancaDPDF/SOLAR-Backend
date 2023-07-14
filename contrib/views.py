# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import logging

from collections import OrderedDict
# Biblioteca Padrao
from datetime import datetime

# Bibliotecas de terceiros
import re
import status
from braces.views import MultiplePermissionsRequiredMixin
from dal import autocomplete
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy, reverse
from django.db import transaction, models
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.utils import timezone
import six
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.cache import cache_page, never_cache
from django.views.generic import ListView, TemplateView, View
from django.views.generic.edit import UpdateView
from djdocuments.views.mixins import FormActionViewMixin
from constance import config

# Solar
from atividade_extraordinaria.models import AtividadeExtraordinariaTipo
from contrib.utils import validar_cpf, validar_cnpj
from defensor.models import Atuacao, Defensor, Documento as DocAtuacao
from defensor.forms import LotacaoForm, ExcluirAtuacaoForm
from meritocracia.models import IndicadorMeritocracia

# Modulos locais
from . import forms
from .models import (
    CEP,
    Area,
    Bairro,
    Comarca,
    Endereco,
    Estado,
    Municipio,
    Servidor,
    Util,
    Vara,
    Defensoria
)
from .services import buscar_servidor_api_athenas_e_ldap

logger = logging.getLogger(__name__)


@login_required
def busca_rapida(request):

    filtro_texto = request.GET.get('filtro', '').strip()
    filtro_numero = re.sub('[^0-9]', '', filtro_texto)
    filtro_cpf = False

    # Verifica se número é um CPF/CNPJ válido
    if len(filtro_numero) == 11 and validar_cpf(filtro_numero):
        filtro_cpf = True
    elif len(filtro_numero) == 14 and validar_cnpj(filtro_numero):
        filtro_cpf = True

    if filtro_numero and not filtro_cpf and len(filtro_numero) != 12:
        resposta = redirect('{}?filtro={}'.format(reverse('processo_listar'), filtro_numero))
    else:
        resposta = redirect('{}?filtro={}'.format(reverse('atendimento_buscar'), filtro_texto))

    return resposta


@login_required
def listar_defensorias(request):

    agora = datetime.now()

    defensorias = Defensoria.objects.filter(ativo=True).order_by('nucleo', 'comarca', 'numero')

    resposta = []
    for defensoria in defensorias:

        obj = Util.object_to_dict(defensoria, {})
        obj['atuacoes'] = []

        atuacoes = defensoria.all_atuacoes.filter(
            Q(ativo=True) &
            Q(data_inicial__lte=agora) &
            (
                Q(data_final__gte=agora) |
                Q(data_final=None)
            )
        ).values(
            'defensor__servidor__nome',
            'data_inicial',
            'data_final',
            'tipo',
            'documento__tipo',
            'documento__numero',
            'documento__data',
        )

        for atuacao in atuacoes:
            tipo = None
            if not atuacao['documento__tipo'] is None:
                tipo = DocAtuacao.LISTA_TIPO[atuacao['documento__tipo']][1]
            documento = {
                'tipo': tipo,
                'numero': atuacao['documento__numero'],
                'data': atuacao['documento__data'],
            }

            if documento['tipo'] and documento['numero'] and documento['data']:
                documento['nome'] = '{tipo} {numero} de {data:%d/%m/%Y}'.format(**documento)

            obj['atuacoes'].append({
                'defensor': atuacao['defensor__servidor__nome'],
                'data_inicial': Util.date_to_json(atuacao['data_inicial']),
                'data_final': Util.date_to_json(atuacao['data_final']),
                'tipo': atuacao['tipo'],
                'documento': documento,
            })

        resposta.append(obj)

    return JsonResponse(resposta, safe=False)


@login_required
def get_defensoria(request, defensoria_id):
    defensoria = get_object_or_404(Defensoria, id=defensoria_id)
    agora = datetime.now()

    defensores = defensoria.all_atuacoes.filter(
        Q(data_inicial__lte=agora) &
        (
            Q(data_final__gte=agora) |
            Q(data_final=None)
        ) &
        Q(ativo=True)
    ).order_by(
        'defensor__servidor__nome'
    ).values_list(
        'defensor_id',
        'defensor__servidor_id',
        'defensor__servidor__nome',
        'defensor__eh_defensor'
    ).distinct()

    resposta = Util.object_to_dict(defensoria, {})
    resposta['defensores'] = [
        {
            'id': d[0],
            'servidor': d[1],
            'nome': d[2],
            'eh_defensor': d[3]
        } for d in defensores]

    # se a defensoria está vinculada a um núcleo, recupera qualificacoes relacionadas (apenas para tarefas)
    if defensoria.nucleo:
        qualificacoes = defensoria.nucleo.qualificacao_set.ativos().tarefas()
        resposta['qualificacoes'] = [
            Util.object_to_dict(qualificacao, {}) for qualificacao in qualificacoes
        ]
    else:
        resposta['qualificacoes'] = []

    return JsonResponse(resposta)


class DefensoriaListView(ListView):
    queryset = Defensoria.objects.ativos().select_related(
        'comarca__coordenadoria',
        'predio'
    ).order_by(
        'comarca__nome',
        'numero',
        'nome'
    )
    model = Defensoria
    paginate_by = 50
    template_name = "contrib/defensoria_buscar.html"

    def get_context_data(self, **kwargs):
        context = super(DefensoriaListView, self).get_context_data(**kwargs)
        context.update({
            'form': forms.BuscarDefensoriaForm(self.request.GET)
        })
        return context

    def get_queryset(self):

        queryset = super(DefensoriaListView, self).get_queryset()
        q = Q()

        if not self.request.user.has_perm('contrib.view_all_defensorias'):

            if hasattr(self.request.user.servidor, 'defensor') and self.request.user.servidor.defensor.ativo:
                defensorias_ids = list(self.request.user.servidor.defensor.defensorias.values_list('id', flat=True))
                defensorias_ids += list(Defensoria.objects.filter(mae__in=defensorias_ids).values_list('id', flat=True))
                q &= Q(id__in=defensorias_ids)
            else:
                q &= Q(comarca=self.request.user.servidor.comarca)

        form = forms.BuscarDefensoriaForm(self.request.GET)

        if form.is_valid():

            data = form.cleaned_data

            # Filtro por comarca
            if data.get('comarca'):
                q &= Q(comarca=data.get('comarca'))

            # Filtro por nome
            if data.get('filtro'):
                q &= Q(nome__icontains=data.get('filtro'))

        return queryset.filter(q)


class DefensoriaUpdateView(UpdateView):
    model = Defensoria
    pk_url_kwarg = 'defensoria_id'
    template_name = 'contrib/defensoria_cadastrar.html'
    form_class = forms.EditarDefensoriaForm

    def form_valid(self, form):
        self.object = form.save(commit=False)

        # Se usuário tem permissão, salva tipos de eventos associados à defensoria
        if self.request.user.has_perm('contrib.change_defensoriatipoevento'):

            form_tipos_eventos = forms.EditarDefensoriaTiposEventosForm(data=self.request.POST, instance=self.object)

            if form_tipos_eventos.is_valid():
                self.object = form_tipos_eventos.save(commit=False)

        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, u'Registro salvo com sucesso!')
        return '{}?prev={}'.format(reverse('defensoria_editar', kwargs={'defensoria_id': self.object.id}), self.request.GET.get('prev'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'form_tipos_eventos': forms.EditarDefensoriaTiposEventosForm(instance=self.object),
            'prev': self.request.GET.get('prev', reverse('defensoria_buscar')),
            'angular': 'CadastroTelefoneCtrl',
            'telefone': self.object.telefone
        })

        return context


class DefensoriaTipoEventoUpdateView(TemplateView):
    template_name = 'contrib/defensoria_associar_tipos_eventos.html'
    form_class = forms.EditarDefensoriaTiposEventosForm

    def get_context_data(self, **kwargs):

        # Recupera lista de defensorias
        defensorias = Defensoria.objects.filter(id__in=self.request.GET.getlist('defensoria'))
        # Recupera lista de tipos de eventos já associados às defensorias selecionadas
        tipos_eventos = AtividadeExtraordinariaTipo.objects.ativos().filter(
            defensorias__in=defensorias
        )

        context = super().get_context_data(**kwargs)

        context.update({
            'form': self.form_class(initial={'tipos_eventos': tipos_eventos}),
            'defensorias': defensorias
        })

        return context

    def post(self, request, *args, **kwargs):

        defensorias = Defensoria.objects.filter(id__in=self.request.POST.getlist('defensoria'))

        for defensoria in defensorias:
            form = self.form_class(data=request.POST, instance=defensoria)
            if form.is_valid():
                form.save()

        messages.success(request, u'Registros salvos com sucesso!')

        return self.get(request, *args, **kwargs)


def cep_to_json_response(cep):
    # gera dicionario com dados do cep
    data = Util.object_to_dict(cep, {})
    data['estado_id'] = cep.municipio.estado.id
    data['municipio_id'] = cep.municipio.id

    if cep.bairro:
        data['bairro'] = cep.bairro.nome
        data['bairro_id'] = cep.bairro.id

    return JsonResponse(data)


@login_required
def get_endereco_by_cep(request, numero):
    from pycep_correios import get_address_from_cep, exceptions, WebService

    """
    Recupera informacoes de endereco a partir do CEP informado
    :param request:
    :param val:
    :return:
    """

    if len(numero) != 8:
        return JsonResponse({'erro': True, 'msg': 'O cep {} está mal formatado'.format(numero)})

    # Verifica se o CEP já existe no banco de dados
    cep = CEP.objects.filter(cep=numero).first()

    # Se não encontrado ou expirado, faz busca nos Correios
    if (cep is None or cep.expirado):

        try:
            data = get_address_from_cep(numero)
        # Caso o CEP aponte como invalido, testa com um segundo webservice
        except exceptions.InvalidCEP:
            try:
                data = get_address_from_cep(numero, webservice=WebService.VIACEP)
            except exceptions.InvalidCEP:
                return JsonResponse({
                    'erro': True,
                    'servico_disponível': True,
                    'msg': 'Erro ao consultar o CEP {} no serviço externo: número inválido'.format(numero)
                })
        except exceptions.CEPNotFound:
            return JsonResponse({
                'erro': True,
                'servico_disponível': True,
                'msg': 'Erro ao consultar o CEP {} no serviço externo: não encontado'.format(numero)
            })
        except Exception as e:
            # Se serviço indisponível retorna dados salvos
            if cep:
                return cep_to_json_response(cep)
            # Se não tiver dados salvos, retorna erro
            else:
                return JsonResponse({
                    'erro': True,
                    'servico_disponível': False,
                    'msg': 'Erro ao consultar o CEP {} no serviço externo: {}'.format(numero, str(e))
                })

        municipio = None
        bairro = None

        # Procura por Município
        try:
            municipio = Municipio.objects.get(
                estado__uf=data['uf'],
                nome__unaccent__iexact=Util.normalize(data['cidade'])
            )
        except ObjectDoesNotExist:
            # O erro pode ocorrer caso o município tenha mudado de nome
            msg = 'Erro ao cadastrar o cep {}: município {} - {} não encontado'.format(numero, data['cidade'], data['uf'])  # noqa: E501
            logger.error(msg)
            return JsonResponse({'erro': True, 'msg': msg})

        # Se informado, procura ou cadastra Bairro
        if data['bairro']:
            try:
                bairro, _ = Bairro.objects.get_or_create(
                    municipio=municipio,
                    nome__unaccent__iexact=Util.normalize(data['bairro']),
                    desativado_em=None,
                    defaults={
                        # necessário por ter usado uma func no get_or_create para esse field
                        'nome': data['bairro']
                    }
                )
            except Bairro.MultipleObjectsReturned:
                bairro = Bairro.objects.filter(
                    municipio=municipio,
                    nome__unaccent__iexact=Util.normalize(data['bairro']),
                    desativado_em=None
                ).first()

        # Cria/atualiza cadastro do CEP
        cep, _ = CEP.objects.update_or_create(
            cep=numero,
            defaults={
                'municipio': municipio,
                'bairro': bairro,
                'logradouro': data['logradouro'],
                'complemento': data['complemento'],
                'eh_geral': False
            }
        )

    return cep_to_json_response(cep)


@login_required
def listar_bairro(request, municipio_id):
    lst = Bairro.objects.filter(
        municipio=municipio_id
    ).order_by(
        'nome'
    ).distinct(
        'nome'
    ).values_list(
        'nome',
        flat=True
    )
    return JsonResponse(list(lst), safe=False)


@login_required
def listar_diretoria(request):
    diretorias = OrderedDict()

    for i in Comarca.objects.coordenadorias().ativos().order_by('nome'):

        comarcas = []
        for j in i.comarcas():
            comarcas.append({'id': j.id, 'nome': j.nome})
        diretorias.update({i.nome: {'id': i.id, 'nome': i.nome, 'comarcas': comarcas}})

    return JsonResponse(diretorias)


@login_required
def listar_indicadores_meritocracia(request):
    indicadores = []

    for area in IndicadorMeritocracia.objects.filter(ativo=True):
        indicadores.append({
            'id': area.id,
            'nome': area.nome,
            'ativo': area.ativo
            })

    return JsonResponse(list(indicadores), safe=False)


@login_required
def listar_logradouro(request, municipio_id):
    lst = Endereco.objects.filter(
        municipio=municipio_id
    ).distinct(
        'logradouro'
    ).order_by(
        'logradouro'
    ).values_list(
        'logradouro',
        flat=True
    )
    return JsonResponse(list(lst), safe=False)


@login_required
def listar_municipio(request):
    lst = Municipio.objects.all().order_by('nome').values_list('nome', flat=True)
    return JsonResponse(list(lst), safe=False)


@login_required
@cache_page(60 * 60 * 24 * 7)  # 7 dias
def listar_municipio_uf(request, estado_id):
    arr = []

    lst = Municipio.objects.select_related('comarca__coordenadoria').filter(estado=estado_id).order_by('nome')
    for i in lst:
        arr.append({
            'id': i.id,
            'nome': i.nome,
            'comarca': {
                'nome': i.comarca.nome,
                'diretoria': i.comarca.coordenadoria.nome if i.comarca.coordenadoria else i.comarca.nome
            } if i.comarca else None,
        })

    return JsonResponse(arr, safe=False)


@login_required
@cache_page(60 * 60 * 24 * 7)  # 7 dias
def listar_estado(request):
    arr = []
    lst = Estado.objects.all().order_by('nome')
    for i in lst:
        arr.append({'id': i.id, 'nome': i.nome, 'uf': i.uf})

    return JsonResponse(arr, safe=False)


@login_required
def listar_area(request):
    arr = []
    for area in Area.objects.filter(ativo=True):
        arr.append({
            'id': area.id,
            'nome': area.nome,
            'ativo': area.ativo})

    return JsonResponse(arr, safe=False)


@login_required
def listar_vara(request):

    varas = Vara.objects.filter(
        ativo=True
    ).extra(
        select={'numero': 'CAST(SUBSTRING(nome FROM \'[0-9]+\') AS INTEGER)'}
    ).order_by(
        'numero', 'nome'
    )

    arr = []
    for vara in varas:
        arr.append({
            'id': vara.id,
            'nome': vara.nome,
            'comarca': vara.comarca_id,
            'grau': vara.grau,
        })

    return JsonResponse(arr, safe=False)


def remove_acentos(data):
    """
    Remove acentos de strings unicode ex: u'ção' = u'cao'
    :param data:
    :return:
    """

    import string
    import unicodedata

    return ''.join(x for x in unicodedata.normalize('NFKD', data) if x in string.ascii_letters).lower()


class BuscarServidorListView(ListView):
    template_name = "contrib/listar_servidor.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'total_ativos': self.get_queryset().filter(ativo=True).count(),
            'total_inativos': self.get_queryset().filter(ativo=False).count(),
            'form': forms.BuscarServidorForm(self.request.GET),
        })

        return context

    def get_queryset(self):

        qs = Servidor.objects.none()
        form = forms.BuscarServidorForm(self.request.GET)

        # Só filtra se valores de busca forem válidos
        if form.is_valid():

            qs = Servidor.objects.filter(uso_interno=False).order_by('-ativo', '-usuario__is_superuser', 'nome')

            if not self.request.user.is_superuser:
                qs = qs.filter(usuario__is_superuser=False)

            data = form.cleaned_data

            if data.get('comarca'):
                qs = qs.filter(comarca=data.get('comarca'))

            if data.get('papel'):
                qs = qs.filter(papel=data.get('papel'))

            for nome in data.get('nome', '').split():
                qs = qs.filter(
                    Q(nome__unaccent__icontains=nome)
                    | Q(matricula__icontains=nome)
                    | Q(usuario__username__icontains=nome)
                )

        return qs


@never_cache
@login_required
def listar_servidor_json(request):
    """Utilizado para buscar servidores em Itinerante e em Relatórios"""

    servidores_queryset = Servidor.objects.filter(
        ativo=True,
    ).values_list(
        'id',
        'nome',
        'defensor__ativo',
        'defensor__supervisor__servidor',
        'uso_interno'
    ).order_by('nome')

    servidores = []

    for servidor in servidores_queryset:
        servidores.append({
            'id': servidor[0],
            'nome': servidor[1],
            'defensor': True if servidor[2] else False,
            'supervisor': servidor[3] if servidor[2] else None,
            'uso_interno': servidor[4]
        })

    return JsonResponse(servidores, safe=False)


@login_required
def listar_servidor_por_atuacao_json(request, defensoria_id):
    queryset = Q(defensoria_id=defensoria_id)

    cargo_id = request.GET.get('cargo_id')

    if cargo_id:
        queryset &= Q(cargo_id=cargo_id)

    vigente = True

    if request.GET.get('vigente'):
        vigente = request.GET.get('vigente')

    queryset &= Q(ativo=vigente)

    atuacoes = Atuacao.objects.filter(queryset).values('defensor__servidor__id',
                                                       'defensor__servidor__nome',
                                                       'cargo_id'
                                                       )

    servidores = []

    for atuacao in atuacoes:
        servidores.append({
            'servidor_id': atuacao['defensor__servidor__id'],
            'nome': atuacao['defensor__servidor__nome'],
            'cargo_id': atuacao['cargo_id']
        })

    return JsonResponse(servidores, safe=False)


@never_cache
@login_required
@permission_required('contrib.change_servidor')
def perfil_servidor(request, servidor_id):

    servidor = Servidor.objects.get(usuario_id=servidor_id, uso_interno=False)

    if hasattr(servidor, 'defensor') and servidor.defensor.eh_defensor:
        assessores = servidor.defensor.lista_assessores
    else:
        assessores = None

    return render(request=request, template_name="contrib/perfil_servidor.html", context=locals())


@never_cache
@login_required
@permission_required('contrib.change_servidor')
def editar_servidor(request, servidor_id, lotacao_id=None):

    servidor = get_object_or_404(Servidor, usuario_id=servidor_id, uso_interno=False)

    if hasattr(servidor, 'defensor'):
        lotacoes = servidor.defensor.atuacoes().select_related(
            'defensoria',
            'cadastrado_por__usuario'
        )
    else:
        lotacoes = Atuacao.objects.none()

    if lotacao_id:
        lotacao = get_object_or_404(Atuacao, id=lotacao_id, ativo=True)
        form_excluir_lotacao = ExcluirAtuacaoForm(instance=lotacao, initial={'data_final': datetime.now().date})

    if request.POST:

        formulario = forms.ServidorForm(request.POST, instance=servidor)

        if formulario.is_valid():
            with transaction.atomic():
                servidor = formulario.save(commit=False)
                servidor.nome = servidor.usuario.get_full_name()
                servidor.save()

                servidor.usuario.is_active = servidor.ativo
                servidor.usuario.save(update_fields=['is_active'])

                # desativa as atuações de servidor caso seja inativado
                if not servidor.usuario.is_active:
                    if servidor.defensor and not servidor.defensor.eh_defensor:
                        for lotacao in lotacoes:
                            lotacao.ativo = False
                            lotacao.data_final = timezone.now()
                            lotacao.save(update_fields=['ativo', 'data_final'])

        return HttpResponseRedirect(reverse_lazy('perfil_servidor', kwargs={'servidor_id': servidor_id}))

    else:

        form = forms.ServidorForm(instance=servidor)
        url_voltar = request.META.get('HTTP_REFERER', '/')

        if hasattr(servidor, 'defensor') and not servidor.defensor.eh_defensor:
            form_lotacao = LotacaoForm(prefix='lotacao', instance=Atuacao(defensor=servidor.defensor))

        return render(request=request, template_name="contrib/editar_servidor.html", context=locals())


@login_required
def foto_servidor_pelo_username(request, username):
    try:
        servidor = Servidor.objects.get(usuario__username=username, uso_interno=False)
    except Exception:
        servidor = Servidor()

    return redirect(servidor.get_foto())


class DefensorSupervisorAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete view to Django User Based
    """

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(DefensorSupervisorAutocomplete, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated:
        #     return USER_MODEL.objects.none()
        # assinado_por = self.forwarded.get('assinado_por', None)

        qs = Defensor.objects.filter(supervisor=None, eh_defensor=True, ativo=True).order_by('servidor__nome')

        if self.q:
            qs = qs.filter(Q(servidor__nome__icontains=self.q))

        return qs

    def get_result_label(self, result):
        return result.servidor.nome


class CadastrarServidorView(MultiplePermissionsRequiredMixin, FormActionViewMixin, generic.CreateView):
    model = Servidor
    document_json_fields = ('nome', 'usuario.username')
    form_class = forms.SolarUserCreationForm
    template_name = 'contrib/criar_usuario_solar.html'
    ajax_success_message = None
    form_action = reverse_lazy('criar_usuario_solar')
    raise_exception = True
    permissions = {
        "all": ("contrib.add_servidor",),
        "any": None
    }

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(CadastrarServidorView, self).dispatch(request, *args, **kwargs)

    def get_ajax_success_message(self, object_instance=None):
        return self.ajax_success_message

    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            return super(CadastrarServidorView, self).post(request, *args, **kwargs)

    def get_success_url(self):
        url = None
        if self.object:
            usuario_pk = self.object.usuario_id
            url = reverse('editar_servidor', kwargs={'servidor_id': usuario_pk})
        return url

    def get_context_data(self, **kwargs):
        context = super(CadastrarServidorView, self).get_context_data(**kwargs)
        context['form_cpf_nome'] = forms.NomeCompletoCPFForm()
        context['angular'] = "CadastroServidorCtrl"
        return context

    def form_valid(self, form):
        response = super(CadastrarServidorView, self).form_valid(form)
        if self.request.is_ajax():
            # object_dict = model_to_dict(self.object, fields=[field.name for field in self.object._meta.fields])
            # object_instance = object_dict
            dados_instancia = {
                'nome': self.object.nome,
                'username': self.object.usuario.username,
                'email': self.object.usuario.email,
                'id': self.object.usuario_id,
                'enviar_email_ao_cadastrar_servidor': config.ENVIAR_EMAIL_AO_CADASTRAR_SERVIDOR,
            }
            data = {'object_instance': dados_instancia, 'errors': None,
                    'success_url': self.get_success_url(), 'pode_cadastrar': True}
            message = self.get_ajax_success_message(self.object)
            if message:
                messages.add_message(self.request, messages.SUCCESS, message)
            return JsonResponse(data=data)
        return response

    def get_form_fields(self):
        fields = self.document_json_fields
        if not fields:
            form = self.get_form()
            fields = six.iterkeys(form.fields)
        return fields

    def get_object_members(self):
        data = {}
        if hasattr(self, 'object'):
            if self.object:
                for field in self.get_form_fields():
                    if hasattr(self.object, field):
                        field_instance = getattr(self.object, field)
                        if isinstance(field_instance, models.Model):
                            field_data = field_instance.pk
                        else:
                            field_data = field_instance
                        data[field] = field_data
        return data

    def form_invalid(self, form):
        response = super(CadastrarServidorView, self).form_invalid(form)
        if self.request.is_ajax():
            data = {'errors': form.errors, 'success_url': self.get_success_url(), 'pode_cadastrar': True}
            # members = self.get_object_members()
            return JsonResponse(data=data, status=status.HTTP_400_BAD_REQUEST)
        return response


class ConsultarAthenasView(View):
    http_method_names = ['post']

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(ConsultarAthenasView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # if request.is_ajax():
        #     POST = simplejson.loads(request.body)
        # else:
        POST = self.request.POST

        cpf_matricula = POST.get('cpf_matricula')
        nome_completo = POST.get('nome_completo')
        dados = buscar_servidor_api_athenas_e_ldap(cpf_matricula, nome_completo)
        dados['pode_cadastrar'] = True
        if dados['errors']['__all__'] or dados['botoes']:
            dados['pode_cadastrar'] = False

        return JsonResponse(data=dados)

    def put(self, *args, **kwargs):
        return super(ConsultarAthenasView, self).post(*args, **kwargs)
