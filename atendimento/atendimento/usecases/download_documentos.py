from typing import List, Dict
from atendimento.atendimento.services import (compacta_documentos,
                                              gera_identificador_unico,
                                              cria_diretorio, converte_ged_pdf,
                                              filtra_valida_download_ged,
                                              filtra_documentos_atendimento,
                                              filtra_documentos_assistido)


DOC_TMP_DIR = "/tmp/sisat/"
# DOCUMENTOS_ATENDIMENTO = 1
DOCUMENTOS_ASSISTIDO = -1


def formata_url_documentos(documentos: List[object]):
    return map(lambda x: (x.arquivo.url[1:], x.nome),
               filter(lambda x: x.arquivo or False,
                      documentos))


def download_documentos(arquivos_solicitados: List[Dict[str, str]],
                        prefixo_arquivo: str, atendimento_numero: str,
                        tipo_documentos: int) -> str:

    documentos_compactar = dict()
    cria_diretorio(DOC_TMP_DIR)
    id_arquivo = gera_identificador_unico(6)
    if tipo_documentos == DOCUMENTOS_ASSISTIDO:
        # Documentos Assistido
        documentos_assistido = filtra_documentos_assistido(atendimento_numero, arquivos_solicitados)
        documentos_compactar = dict(documentos_assistido=documentos_assistido)
    else:
        # Documentos Atendimento / GED
        documentos_atendimento = filtra_documentos_atendimento(arquivos_solicitados, atendimento_numero)
        documentos_anexos = formata_url_documentos(documentos_atendimento)

        documentos_compactar = dict(documentos_atendimento=documentos_anexos)

        documentos_ged = list(map(lambda x: x.documento_online.pk_uuid,
                              filter(lambda x: x.documento_online or False, documentos_atendimento)))

        if documentos_ged:
            ged_temp_dir = cria_diretorio(f"{DOC_TMP_DIR}{id_arquivo}")
            documentos_ged = filtra_valida_download_ged(documentos_ged)
            lista_ged = ((converte_ged_pdf(documento, f"{ged_temp_dir}/{documento.pk_uuid}.pdf"),
                          documento.assunto)
                         for documento in documentos_ged)

            documentos_compactar["ged"] = lista_ged

    arquivo_nome = f"{DOC_TMP_DIR}{prefixo_arquivo}({id_arquivo}).zip"
    arquivo_path = compacta_documentos(documentos_compactar, arquivo_nome)

    return arquivo_path
