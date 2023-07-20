import logging
from typing import List, Dict, Any
from django.core.exceptions import ObjectDoesNotExist
from propac.exceptions import TarefaNaoEncontradaException
from contrib.models import Servidor
from django.http.request import QueryDict
from django.utils.datastructures import MultiValueDict
from atendimento.atendimento.models import Documento, Tarefa
from atendimento.atendimento.forms import DocumentoForm
from defensor.models import Atuacao
from propac.models import Movimento
from django.core.files.base import ContentFile
from propac.models import DocumentoPropac
from datetime import datetime


logger = logging.getLogger(__name__)


def salvar_documento_tarefa(POST: QueryDict, FILES: MultiValueDict, user) -> Documento:
    documento = Documento(cadastrado_por=user.servidor)

    documento.data_enviado = datetime.now()
    documento.enviado_por = user.servidor

    # Se possuía versão assinada, desativa e remove vínculo
    if documento.documento_assinado:
        documento.documento_assinado.desativar(usuario=user)
        documento.documento_assinado = None

    form = DocumentoForm(POST, FILES, instance=documento)

    return form.save() if form.is_valid() else None


def responder_tarefa(user, tarefa_id: int, resposta: str,
                     status: int, POST: QueryDict,
                     FILES: MultiValueDict) -> Tarefa:
    servidor = Servidor.objects.get(usuario_id=user.id)

    tarefa = Tarefa.objects.get(id=tarefa_id)
    resposta = tarefa.responder(resposta, servidor, status)

    if FILES:
        resposta.documento = salvar_documento_tarefa(POST, FILES, user)
        resposta.save()

    if tarefa.status != resposta.status:
        tarefa.status = resposta.status
        tarefa.save()

    return resposta


def finalizar_tarefa(servidor, tarefa_id: int) -> Tarefa:
    try:
        tarefa = Tarefa.objects.get(id=tarefa_id, ativo=True, finalizado=None)
        tarefa.finalizar(servidor)

        return tarefa
    except ObjectDoesNotExist:
        logger.error("Tarefa não encontrada id: {tarefa_id}")
        raise TarefaNaoEncontradaException()
    except Exception:
        logger.error(f"Ocorreu um erro ao finalizar a tarefa: {tarefa_id}")
        raise


def excluir_tarefa(tarefa: Tarefa, servidor) -> Tarefa:
    try:
        if tarefa.ativo and tarefa.finalizado is None:
            tarefa.excluir(excluido_por=servidor)

        return tarefa

    except Exception as error:
        logger.error(f"Ocorreu um erro ao excluir a tarefa: {tarefa.id}")
        logger.error(error)
        raise


def listar_defensorias(user) -> dict:
    """
        Esta listagem de defensorias foi baseada na listagem utilizada em tarefas de atendimento
    """

    if not hasattr(user.servidor, 'defensor'):
        return {
            'defensorias': [],
            'resposta_para': []
        }

    defensorias_atuacao = Atuacao.objects.prefetch_related(
        "defensoria__nucleo"
    ).vigentes_por_defensor(
        defensor=user.servidor.defensor
    ).values(
        "defensoria__id",
        "defensoria__nome",
        "defensoria__nucleo__multidisciplinar",
        "defensoria__nucleo__diligencia",
        "defensoria__nucleo__indeferimento",
        "defensoria__nucleo__agendamento"
    ).all()

    defensorias = []
    # Marca quais das defensorias participam do atendimento/processo
    for defensoria_atuacao in defensorias_atuacao:
        # Só permite o cadastro de tarefas para setores com acesso ao Painel do Defensor (ver nucleo.views.index)
        defensoria_atuacao['pode_cadastrar_tarefa'] = True

        if defensoria_atuacao.get('defensoria__nucleo__multidisciplinar'):
            defensoria_atuacao['pode_cadastrar_tarefa'] = False
        elif defensoria_atuacao.get('defensoria__nucleo__diligencia'):
            defensoria_atuacao['pode_cadastrar_tarefa'] = False
        elif (defensoria_atuacao.get('defensoria__nucleo__indeferimento')
              and not defensoria_atuacao.get('defensoria__nucleo__agendamento')):
            defensoria_atuacao['pode_cadastrar_tarefa'] = False

        defensorias.append({
            'id': defensoria_atuacao['defensoria__id'],
            'nome': defensoria_atuacao['defensoria__nome'],
            'pode_cadastrar_tarefa': defensoria_atuacao["pode_cadastrar_tarefa"]
        })

    return {
        'defensorias': defensorias,
        'resposta_para': defensorias
    }


def filename(arquivo) -> str:
    return arquivo.name.split("/")[-1]


def documento_tarefa(tarefa, resposta) -> dict:
    documento = resposta.documento

    return {
        'tarefa_titulo': tarefa.titulo,
        'documento_id': documento.pk,
        'documento_nome': documento.nome or filename(documento.arquivo),
        'movimento': tarefa.movimento.pk,
        'tipo_anexo': ''
    }


def recupera_documentos_tarefas(movimento: Movimento) -> List[Dict[str, Any]]:
    # tarefas = movimento.tarefas.select_related('documento').order_by('pk').filter(ativo=True)
    tarefas = movimento.tarefas.prefetch_related('all_respostas').order_by('pk').filter(ativo=True)

    documentos = []
    for tarefa in tarefas:
        for resposta in tarefa.all_respostas.all():
            if resposta.ativo and resposta.documento:
                documentos.append(documento_tarefa(tarefa, resposta))

    return documentos


def cria_documentos_propac(request_data, servidor) -> List:
    doc_ids = (doc["documento_id"] for doc in request_data)
    documentos = Documento.objects.filter(id__in=doc_ids)

    doc_arquivos = {
        documento.pk: documento.arquivo
        for documento in documentos.all()
    }

    propac_documentos = []

    for data in request_data:
        arquivo_original = doc_arquivos[data['documento_id']]
        nome_arquivo_original = arquivo_original.name.split("/")[-1]

        new_doc = ContentFile(arquivo_original.read(),
                              name=nome_arquivo_original)

        propac_documentos.append(
            DocumentoPropac(
                anexo=new_doc,
                tipo_anexo_id=data['tipo_anexo'],
                movimento_id=data["movimento"],
                cadastrado_por=servidor,
                nome=data.get('documento_nome') or nome_arquivo_original,
                anexo_original_nome_arquivo=nome_arquivo_original
            )
        )

    return DocumentoPropac.objects.bulk_create(propac_documentos)


__all__ = ('salvar_documento_tarefa', 'responder_tarefa', 'finalizar_tarefa',
           'excluir_tarefa', 'listar_defensorias', 'recupera_documentos_tarefas',
           'cria_documentos_propac')
