'''
    Propriedade intelectual pertencente a Mateus Mota
'''

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Case, IntegerField, Q, Sum, Value, When
import json
import datetime
from django.core.urlresolvers import reverse

from atendimento.atendimento.models import Atendimento, Documento
from djdocuments.models import Documento as DjDocDocumento
from contrib.models import Servidor
from defensor.models import Atuacao

@login_required
def index(request):

    if(request.method == 'POST'):

        status_dict = [
            {'id': 0, 'status': 'Todos'},
            {'id': 1, 'status': 'Em Edicao'},
            {'id': 2, 'status': 'Prontos Para Assinar'},
            {'id': 3, 'status': 'Assinados'},
            {'id': 4, 'status': 'Prontos Para Finalizar'},
            {'id': 5, 'status': 'Finalizados'},
        ]
        # retorna um JSON contendo um dicionário de status
        return JsonResponse(status_dict, safe=False)
    else:
        query_documento = Q(documento_online__esta_ativo=True)
        query_documento &= Q(documento_online__eh_modelo=False)
        query_documento &= Q(documento_online__eh_modelo_padrao=False)
        usuario_grupo_ids = get_grupos_usuario(request)
        query_documento &= Q(documento_online__grupo_dono__in=usuario_grupo_ids)
        documentos_em_edicao_qtd = len(get_documentos_em_edicao(request,query_documento))
        documentos_prontos_para_assinar_qtd = len(get_documentos_prontos_para_assinar(request,query_documento))
        documentos_assinados_qtd = len(get_documentos_assinados(request,query_documento))
        documentos_prontos_para_finalizar_qtd = len(get_documentos_prontos_para_finalizar(request,query_documento))
        documentos_finalizados_qtd = len(get_documentos_finalizados(request,query_documento))
    return render(request, "gestordocs/index.html", locals())


@login_required
def buscar_documentos(request):

    if(request.method == 'POST'):
        # extrai os dados da requisição e realiza consultas no banco de dados para buscar documentos com base 
        # nos critérios fornecidos
        requisicao_unicode = request.body.decode('utf-8')
        requisicao = json.loads(requisicao_unicode)
        conteudo = requisicao

        titulo_documento = conteudo['titulo_documento']
        numero_documento = conteudo['numero_documento']
        numero_atendimento = conteudo['numero_atendimento']
        data_inicial = datetime.datetime.strptime(conteudo['data_inicial'], "%d/%m/%Y").strftime("%Y-%m-%d") if(conteudo['data_inicial']) else ''
        data_final = datetime.datetime.strptime(conteudo['data_final'], "%d/%m/%Y").strftime("%Y-%m-%d") if(conteudo['data_final']) else ''
        status_documento = int(conteudo['status_documento']) if conteudo['status_documento'] else 0

        query_documento = Q(documento_online__esta_ativo = True)
        query_documento &= Q(documento_online__eh_modelo = False)
        query_documento &= Q(documento_online__eh_modelo_padrao = False)
        usuario_grupo_ids = get_grupos_usuario(request)
        query_documento &= Q(documento_online__grupo_dono__in = usuario_grupo_ids)

        if(titulo_documento):
            query_documento &= Q(documento_online__assunto__contains = titulo_documento)

        if(numero_documento):
            query_documento &= Q(documento_online__id = numero_documento)

        if(numero_atendimento):
            query_documento &= Q(atendimento__numero__icontains = numero_atendimento)

        if(data_inicial):
            query_documento &= Q(documento_online__criado_em__gte = data_inicial)

        if(data_final):
            query_documento &= Q(documento_online__criado_em__lte = data_final)

        documentos = None

        if(status_documento == 0):
            documentos = retornar_documentos(request, query_documento)

        elif(status_documento == 1):
            documentos = get_documentos_em_edicao(request, query_documento)

        elif(status_documento == 2):
            documentos = get_documentos_prontos_para_assinar(request, query_documento)

        elif(status_documento == 3):
            documentos = get_documentos_assinados(request, query_documento)

        elif(status_documento == 4):
            documentos = get_documentos_prontos_para_finalizar(request, query_documento)

        elif(status_documento == 5):
            documentos = get_documentos_finalizados(request, query_documento)

        documentos = documentos.values(
            'atendimento__numero',
            'documento_online__id',
            'documento_online__assunto',
            'documento_online__criado_por__first_name',
            'documento_online__criado_por__last_name',
            'documento_online__criado_por__username',
            'atendimento__defensor__defensoria__nome',
            'pessoa__nome',
            'documento_online__criado_em',
            'documento_online__versao_numero',
            'documento_online__pk_uuid',
        ).order_by('-documento_online__criado_em')

        documentos_lst = []
        for documento in documentos:
            documento = {
                'pk_uuid': documento['documento_online__pk_uuid'],
                'numero_atendimento': documento['atendimento__numero'],
                'numero_documento': documento['documento_online__id'],
                'titulo_documento': documento['documento_online__assunto'],
                'atendente': documento['documento_online__criado_por__first_name'] + ' ' + documento['documento_online__criado_por__last_name'],
                'atendente_login': documento['documento_online__criado_por__username'],
                'defensoria': documento['atendimento__defensor__defensoria__nome'],
                'assistido': documento['pessoa__nome'],
                'criado_em': documento['documento_online__criado_em'].strftime('%d/%m/%Y %H:%M'),
                'numero_versao': documento['documento_online__versao_numero'],
            }
            documentos_lst.append(documento)

        return JsonResponse({'documentos': documentos_lst})

    return JsonResponse({'success': False})

@login_required
def buscar_documento(request):

    if(request.method == 'POST'):

        requisicao_unicode = request.body.decode('utf-8')
        requisicao = json.loads(requisicao_unicode)
        conteudo = requisicao

        pk_uuid = conteudo['pk_uuid']

        documento = DjDocDocumento.objects.get(pk_uuid=pk_uuid)

        if (not documento.esta_pronto_para_assinar and documento.pode_editar(request.user) and not documento.possui_assinatura_assinada):
            pode_editar_documento = True
        else:
            pode_editar_documento = False

        atendimentos_relacionados = documento.documento_set.ativos().atendimento_ativo().values(
            'id',
            'atendimento__tipo',
            'atendimento__numero',
            'atendimento__origem__numero'
        )

        atendimentos = []
        for atendimento in atendimentos_relacionados:

            atendimento_atividade = atendimento['atendimento__tipo'] == Atendimento.TIPO_ATIVIDADE

            if atendimento_atividade:
                atendimento_numero = atendimento['atendimento__origem__numero']
            else:
                atendimento_numero = atendimento['atendimento__numero']

            atendimentos.append({
                'numero': atendimento_numero,
                'atividade': atendimento_atividade,
                'url': reverse('atendimento_atender', args=[atendimento_numero]),
                'documento_id': atendimento['id']
            })

        documento_propac = documento.documentopropac_set.filter(ativo=True).first()

        documento_retorno = {
            'tipo_documento': documento.tipo_documento.titulo,
            'esta_assinado': documento.esta_assinado,
            'esta_pronto_para_assinar': documento.esta_pronto_para_assinar,
            'finalizar_url': documento.get_finalizar_url,
            'pronto_para_finalizar': documento.pronto_para_finalizar,
            'grupo_dono': documento.grupo_dono.nome,
            'id_documento': documento.id,
            'versao': documento.versao_numero,
            'assunto': documento.assunto,
            'criado_por': documento.criado_por_nome,
            'criado_em': (documento.criado_em).strftime('%d/%m/%Y %H:%M'),
            'pk_uuid': documento.pk_uuid,
            'pode_editar_documento': pode_editar_documento,
            'documento_propac': True if documento_propac else False,
            'atendimento': [] if not len(atendimentos) else atendimentos[0],
            'doc_num_versao': documento.identificador_versao
        }

        return JsonResponse({'documento': documento_retorno})

    return JsonResponse({'success': False})

@login_required
def get_grupos_usuario(request):
    # retorna os IDs dos grupos aos quais o usuário autenticado pertence
    try:
        atuacoes_id = None
        if request.user.is_superuser:
            atuacoes_id = Atuacao.objects.filter(ativo=True).values_list('defensoria_id', flat=True)
        else:
            servidor = Servidor.objects.get(usuario__id = request.user.id)

            query_atuacoes_servidor = Q(defensor__servidor=servidor.id)
            query_atuacoes_servidor &= Q(defensor__ativo=True)
            query_atuacoes_servidor &= Q(ativo = True)

            atuacoes_id = Atuacao.objects.filter(query_atuacoes_servidor).values_list('defensoria_id', flat=True)

        return atuacoes_id

    except:

        return JsonResponse({'success': False})


@login_required()
# recebe uma query e retorna uma lista de documentos com base nessa consulta
def retornar_documentos(request, query):
    return Documento.objects.filter(query)


@login_required()
def get_documentos_em_edicao(request, query):
    query &= Q(documento_online__esta_pronto_para_assinar = False)
    query &= Q(documento_online__esta_assinado = False)
    return retornar_documentos(request, query)

@login_required()
def get_documentos_prontos_para_assinar(request, query):
    query &= Q(documento_online__esta_pronto_para_assinar = True)
    query &= Q(documento_online__esta_assinado = False)
    return retornar_documentos(request, query)

@login_required()
def get_documentos_assinados(request, query):
    # possui_assinaturas_concluidas = document.assinaturas.filter(grupo_assinante__in=grupos,
    #                                                             esta_assinado=True).exists()

    query &= (Q(documento_online__assinatura_hash='') | Q(documento_online__assinatura_hash=None))
    query &= Q(documento_online__esta_assinado=False)
    docs= Documento.objects.filter(query).annotate(
        assinaturas_pendentes=Sum(
            Case(
                When(
                    Q(documento_online__assinaturas__esta_assinado=False) & Q(
                        documento_online__assinaturas__ativo=True),
                    then=Value(1)
                ),
                default=0,
                output_field=IntegerField()
            )
        ),
        assinaturas_prontas = Sum(
            Case(
                When(
                    Q(documento_online__assinaturas__esta_assinado=True) & Q(
                        documento_online__assinaturas__ativo=True),
                    then=Value(1)
                ),
                default=0,
                output_field=IntegerField()
            )
        )
    ).exclude(assinaturas_pendentes=0,assinaturas_prontas=0)
    return  docs

@login_required()
# esses documentos estão prontos para finalizar, mas ainda não estão assinados
def get_documentos_prontos_para_finalizar(request, query):
    query &= (Q(documento_online__assinatura_hash='') | Q(documento_online__assinatura_hash=None))
    query &= Q(documento_online__esta_assinado = False)
    docs= Documento.objects.filter(query).annotate(
        assinaturas_pendentes=Sum(
            Case(
                When(
                    Q(documento_online__assinaturas__esta_assinado=False) & Q(
                        documento_online__assinaturas__ativo=True),
                    then=Value(1)
                ),
                default=0,
                output_field=IntegerField()
            )
        ),
        assinaturas_prontas = Sum(
            Case(
                When(
                    Q(documento_online__assinaturas__esta_assinado=True) & Q(
                        documento_online__assinaturas__ativo=True),
                    then=Value(1)
                ),
                default=0,
                output_field=IntegerField()
            )
        )
    ).filter(assinaturas_pendentes=0).exclude(assinaturas_prontas=0)
    return docs

@login_required()
# esses documentos estão assinados e possuem um hash de assinatura
def get_documentos_finalizados(request, query):
    query &= Q(documento_online__esta_assinado = True)
    query &= (~Q(documento_online__assinatura_hash = '') | ~Q(documento_online__assinatura_hash = None))
    return retornar_documentos(request, query)

