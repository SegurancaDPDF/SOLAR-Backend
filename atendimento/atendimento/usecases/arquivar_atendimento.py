from django.utils import timezone
from atendimento.atendimento.models import (
    Atendimento,
    Documento,
    Defensor as AtendimentoDefensor
)
from atendimento.atendimento.serializers import DocumentoSerializer
from atendimento.atendimento.exceptions import (
    AtendimentoArquivadoException,
    AtendimentoDesarquivadoException,
    AtendimentoNaoEncontradoException,
    AtendimentoPermissionError,
    AtendimentoLotacaoError
)
from atendimento.atendimento.permissions import (
    PERMISSAO_PARA_ARQUIVAR,
    PERMISSAO_PARA_DESARQUIVAR
)


# função para anexar um documento ao atendimento
def anexar_documento(atendimento: AtendimentoDefensor, documento: dict) -> Documento:
    documento["atendimento"] = atendimento.id
    documento["enviado_por"] = atendimento.atendido_por.id
    serializer = DocumentoSerializer(data=documento)
    serializer.is_valid(raise_exception=True)
    return serializer.save()


# função para recuperar o atendimento de origem com base no número de atendimento
def recupera_atendimento_origem(numero: int):
    return AtendimentoDefensor.objects.only('id', 'inicial_id').get(numero=numero)


# função para obter campos extras necessários para criar um novo atendimento com base em dados de requisição
def get_extra_fields(dados_requisicao):
    atendimento_origem = dados_requisicao["origem"]
    atendimento_final = dados_requisicao["origem"].at_final
    return {
        "inicial": atendimento_origem.at_inicial,
        "defensoria": atendimento_final.defensoria,
        "defensor": atendimento_final.defensor
    }


# função para atualizar a árvore de atendimento
def atualiza_arvore(atendimento):
    if hasattr(atendimento, 'arvore'):
        atendimento.arvore.ativo = False
        atendimento.arvore.save()


# função para criar um dicionário com informações do documento anexado
def documento_anexo(arquivo: object, nome: str = "") -> dict:
    return {
        "arquivo": arquivo,
        "nome": nome
    } if arquivo else None


# função para arquivar ou desarquivar um atendimento com base em dados de requisição
def arquivar_desarquivar_atendimento(atendimento, tipo_arquivamento: int, atendimento_arquivar: dict):
    campos_extras = {
        "inicial": atendimento.at_inicial,
        "origem": atendimento.at_inicial,
        "defensoria": atendimento.at_final.defensoria,
        "defensor": atendimento.at_final.defensor,
        "tipo": tipo_arquivamento,
        "data_atendimento": timezone.now()
    }
    documento = documento_anexo(atendimento_arquivar.pop("documento_arquivo", None),
                                atendimento_arquivar.pop("documento_nome", None))
    atendimento = AtendimentoDefensor(**dict(atendimento_arquivar | campos_extras))
    atendimento.save()
    if documento:
        anexar_documento(atendimento, documento)
    atualiza_arvore(atendimento.origem)
    return atendimento


# função para arquivar um atendimento com base no número do atendimento e dados de requisição
def arquivar_atendimento(user, atendimento_numero: int,
                         atendimento_arquivar: dict) -> AtendimentoDefensor:
    atendimento = Atendimento.objects.filter(numero=atendimento_numero).first()
    if not atendimento:
        raise AtendimentoNaoEncontradoException()
    if atendimento.arquivado:
        raise AtendimentoArquivadoException()
    if not (atendimento.at_final.defensoria in user.servidor.defensor.defensorias):
        raise AtendimentoLotacaoError()
    if not user.has_perm(PERMISSAO_PARA_ARQUIVAR):
        raise AtendimentoPermissionError(msg="O usuário não tem permissão para "
                                             "arquivar este atendimento.")
    return arquivar_desarquivar_atendimento(
        atendimento=atendimento,
        tipo_arquivamento=Atendimento.TIPO_ARQUIVAMENTO,
        atendimento_arquivar=atendimento_arquivar
    )


# função para desarquivar um atendimento com base no número do atendimento e dados de requisição
def desarquivar_atendimento(user, atendimento_numero: int,
                            atendimento_arquivar: dict) -> AtendimentoDefensor:
    atendimento = Atendimento.objects.filter(numero=atendimento_numero).first()
    if not atendimento:
        raise AtendimentoNaoEncontradoException()
    if not atendimento.arquivado:
        raise AtendimentoDesarquivadoException()
    if not (atendimento.at_final.defensoria in user.servidor.defensor.defensorias):
        raise AtendimentoLotacaoError()
    if not user.has_perm(PERMISSAO_PARA_DESARQUIVAR):
        raise AtendimentoPermissionError(msg="O usuário não tem permissão para "
                                             "desarquivar este atendimento.")
    return arquivar_desarquivar_atendimento(
        atendimento=atendimento,
        tipo_arquivamento=Atendimento.TIPO_DESARQUIVAMENTO,
        atendimento_arquivar=atendimento_arquivar
    )
