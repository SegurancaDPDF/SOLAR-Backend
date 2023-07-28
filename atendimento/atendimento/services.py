# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import os
import html
import uuid
from zipfile import ZipFile
from typing import List, Dict, Optional
from datetime import date
import logging
# Bibliotecas de terceiros
from constance import config
from django.conf import settings
from django.contrib import messages
from django.template import Context, Template
from django.db.models import F, Q
from djdocuments.models import Documento as DocumentoGED
from djdocuments.views.documentos import create_document_from_document_template

# Modulos locais
from atendimento.atendimento.models import (
    Atendimento,
    Qualificacao,
    Tarefa,
    Defensor as AtendimentoDefensor,
    Pessoa as AtendimentoPessoa,
    Documento as AtendimentoDocumento
)

from contrib.models import Util
from contrib.services import envia_sms, get_extensao_arquivo, envia_email
from contrib.services import GedToPDFService

logger = logging.getLogger(__name__)


def preencher_campos_ged(documento, context_conteudo, context_cabecalho=None, context_rodape=None,
                         fallback_to_conteudo=False):

    t_conteudo = Template(html.unescape(documento.conteudo))
    t_cabecalho = Template(html.unescape(documento.cabecalho))
    t_rodape = Template(html.unescape(documento.rodape))

    c_conteudo = Context(context_conteudo)
    c_cabecalho = Context(context_cabecalho or context_conteudo if fallback_to_conteudo else context_cabecalho)
    c_rodape = Context(context_rodape or context_conteudo if fallback_to_conteudo else context_rodape)

    documento.conteudo = t_conteudo.render(c_conteudo)
    documento.cabecalho = t_cabecalho.render(c_cabecalho)
    documento.rodape = t_rodape.render(c_rodape)

    return documento


def criar_ged_apartir_de_modelo(assunto, modelo, atendimento_defensor, pessoa, usuario, liberar_para_assinar=False):
    '''
        Criar automaticamente o documento GED a partir do modelo fornecido.

        Parâmetros
        ----------

        modelo : Documento
            Documento GED que será o modelo do documento Criado.

        atendimento_defensor : AtendimentoDefensor
            Dados do atendimento que será vinculado ao documento GED.

        pessoa : Pessoa
            Dados da pessoa Assistida que será vinculada ao documento GED

        usuário : User
            Usuário logado que está criando o documento GED.

        liberar_para_assinar : bool
            Liberar documento GED para o defensor assinar.

        Retorno
        -------
        Documento -> Documento GED Criado.

    '''

    documento_ged = create_document_from_document_template(
                            current_user=usuario,
                            grupo=atendimento_defensor.defensoria,
                            documento_modelo=modelo,
                            assunto=assunto
                        )

    context_conteudo = {
            'defensoria': documento_ged.grupo_dono,
            'atendimento': atendimento_defensor,
            'servidor': usuario.servidor,
            'pessoa': pessoa,
            'hoje': date.today(),
    }
    preencher_campos_ged(
        documento=documento_ged,
        context_conteudo=context_conteudo,
        fallback_to_conteudo=True
    )

    if liberar_para_assinar:
        documento_ged.esta_pronto_para_assinar = True

    documento_ged.save()

    return documento_ged


def criar_documento_ged_para_o_atendimento(modelo, atendimento_defensor, pessoa, usuario, liberar_para_assinar=False, assunto='Novo GED'):
    '''
        Criar documento GED para o requerente atendido.
    '''

    # atendimento para vincular ao documento do atendimento.
    atendimento = atendimento_defensor.atendimento_ptr

    documento_online = criar_ged_apartir_de_modelo(assunto, modelo, atendimento_defensor, pessoa, usuario, liberar_para_assinar)

    try:
        atendimento_documento = AtendimentoDocumento(
                atendimento=atendimento,
                documento_online=documento_online,
                cadastrado_por=usuario.servidor,
                nome=documento_online.assunto,
                pessoa=pessoa
            )
        atendimento_documento.save()
    except Exception as e:
        # Exluir GED criado se houver erro na criação do Documento do atendimento
        documento_online.delete()
        raise e

    return atendimento_documento


class AtendimentoService(object):

    def __init__(self, atendimento):
        self.atendimento = atendimento

    def transferir_relacionamentos(self, atendimento_destino, copiar_pessoas=False, transferir_pessoas=True,
                                   transferir_filhos=True, transferir_documentos=True):

        self.atendimento.retorno.update(inicial=atendimento_destino)  # atendimentos (retornos)
        self.atendimento.tarefa_set.update(atendimento=atendimento_destino)  # tarefas
        self.atendimento.parte_set.update(atendimento=atendimento_destino)  # partes (processo)
        self.atendimento.visualizacoes.update(atendimento=atendimento_destino)  # visualizações
        self.atendimento.participantes_atendimentos.update(atendimento=atendimento_destino)  # participantes

        # Copia relacionamentos das pessoas para atendimento destino, sem remover do atendimento origem
        if copiar_pessoas:
            for parte in self.atendimento.partes.ativos():
                if not atendimento_destino.partes.filter(pessoa=parte.pessoa).exists():
                    atendimento_destino.add_pessoa(
                        pessoa_id=parte.pessoa_id,
                        tipo=parte.tipo
                    )

        if transferir_pessoas:
            self.atendimento.partes.update(atendimento=atendimento_destino)  # pessoas (atendimento)

        if transferir_filhos:  # atividades, apoios, retornos (ignora atendimento da recepção)
            self.atendimento.filhos.exclude(
                tipo=Atendimento.TIPO_RECEPCAO
            ).update(
                origem=atendimento_destino
            )

        if transferir_documentos:
            self.atendimento.documento_set.update(atendimento=atendimento_destino)  # documentos

        # Força limpeza da árvore do atendimento
        if hasattr(atendimento_destino, 'arvore'):
            atendimento_destino.arvore.ativo = False
            atendimento_destino.arvore.save()


class ServiceDocumentoAtendimento(object):

    def __init__(self, documento):
        self.documento = documento

    def render_string_to_string(template_string, context):
        t = Template(template_string)
        c = Context(context)
        return t.render(c)

    def preencher(self, params):
        documento = self._preencher(self.documento.documento_online, context_conteudo=params, fallback_to_conteudo=True)
        documento.save()

    def _preencher(self, documento, context_conteudo, context_cabecalho=None, context_rodape=None,
                   fallback_to_conteudo=False):
        documento = preencher_campos_ged(
            documento=documento,
            context_conteudo=context_conteudo, context_cabecalho=context_cabecalho, context_rodape=context_rodape,
            fallback_to_conteudo=fallback_to_conteudo)
        return documento


def atualiza_tarefa_atendimento_origem(atendimento, resposta, servidor, finalizar=False, reabrir=False):
    # Atualiza status da tarefa do atendimento de origem
    if atendimento.origem and atendimento.tipo == Atendimento.TIPO_NUCLEO:

        # Recupera tarefa do atendimento
        tarefa = atendimento.origem.tarefa_set.filter(prioridade=Tarefa.PRIORIDADE_ALERTA).first()

        # Se nao existir tarefa vinculada ira criar uma nova
        if not tarefa:

            tarefa = Tarefa(
                atendimento=atendimento.origem,
                resposta_para=atendimento.origem.defensor.defensoria,
                setor_responsavel=atendimento.defensoria,
                titulo=atendimento.qualificacao.titulo,
                descricao=atendimento.origem.historico,
                data_inicial=atendimento.data_cadastro,
                data_final=atendimento.data_agendamento,
                prioridade=Tarefa.PRIORIDADE_ALERTA
            )

        if finalizar:
            tarefa.status = Tarefa.STATUS_CUMPRIDO
        elif reabrir:
            tarefa.status = Tarefa.STATUS_PENDENTE

        tarefa.ativo = True
        tarefa.save()

        tarefa.responder(resposta, servidor, tarefa.status)

        return tarefa


def envia_sms_exclusao(request, atendimento, modelo_sms):
    """""Método que envia um SMS informando exclusão do agendamento"""

    # Prepara a mensagem a ser enviada
    conteudo_sms = modelo_sms.replace(
        "SMS_DEF_SIGLA", settings.SIGLA_INSTITUICAO
    ).replace(
        "SMS_NUMERO_ATENDIMENTO", str(atendimento.numero)
    )

    # Se tem que remover os acentos, remove
    if (config.SMS_REMOVER_ACENTOS):
        conteudo_sms = Util.unaccent(conteudo_sms)

    # Envia o SMS para o assistido informando do agendamento
    telefone = atendimento.telefone_para_sms

    # Se o telefone não for encontrado, retorna mensagem de erro
    if (not telefone['telefone']):
        mensagem = "Nenhum SMS enviado!"
        if (telefone['no_valid_cell']):
            mensagem += " Nenhum telefone válido"
        messages.error(request, mensagem)
    else:
        # Formata o telefone e envia
        telefone_numero = '55{}{}'.format(telefone['telefone'].ddd, telefone['telefone'].numero)
        envio = envia_sms(conteudo_sms, telefone_numero)

        # se não foi possível enviar, adiciona mensagem de erro
        if not (envio.status_code >= 200 and envio.status_code < 300):
            mensagem = "Não foi possível enviar o SMS! Código do erro: {}".format(envio.status_code)
            messages.error(request, mensagem)
        else:
            # verifica se a flag envio pelo facilita sms se sim faz tratamento de erro para o retorno da FACILITA Movel
            if (config.FACILITA_SMS_AUTH):
                statusresposta = envio.content.decode('utf-8').split(';')
                if (statusresposta[0] != '6'):
                    logger.error("DPE >> Erro de Envio de SMS status facilita SMS: {}".format(statusresposta))
                    mensagem = "Não foi possível enviar o SMS! Código do erro: {}".format(statusresposta[0])
                    messages.error(request, mensagem)
                else:
                    mensagem = "SMS enviado com sucesso!"
                    messages.success(request, mensagem)
            else:
                mensagem = "SMS enviado com sucesso!"
                messages.success(request, mensagem)


def envia_email_exclusao(request, atendimento, modelo_sms):
    """""Método que envia um Email com os dados do atendimento"""

    logger.info("DPEAC >> atendimento.numero: {}".format(atendimento.numero))

    # Prepara a mensagem a ser enviada
    conteudo_sms = modelo_sms.replace(
        "SMS_DEF_SIGLA", settings.SIGLA_INSTITUICAO
    ).replace(
        "SMS_NUMERO_ATENDIMENTO", str(atendimento.numero)
    ).replace(
        "MOTIVO_EXCLUSAO", str(atendimento.tipo_motivo_exclusao)
    )

    # Envia o Email para o assistido informando do agendamento
    email = atendimento.requerente.pessoa.email
    logger.info("DPEAC >> atendimento.assistido email: {}".format(email))
    if (email):
        resposta = envia_email(conteudo_sms, email, config.ASSUNTO_EMAIL_NOTIFICACAO)
        if (resposta == 0):
            mensagem = "O email não foi enviado!"
            messages.error(request, mensagem)
        else:
            mensagem = "Email enviado com sucesso!"
            messages.success(request, mensagem)
    else:
        mensagem = "Assistido não tem e-mail cadastrado"
        messages.error(request, mensagem)


def gera_identificador_unico(length: Optional[int] = None) -> str:
    uid = str(uuid.uuid4()).replace("-", "")
    return uid[0:length]


def checar_possibilidade_retorno(atendimento):

    if config.ATIVAR_INIBICAO_RETORNO:
        hoje = date.today()

        check = AtendimentoDefensor.objects.filter(
            ativo=True,
            data_agendamento__year=hoje.year,
            data_agendamento__month=hoje.month,
            data_agendamento__day=hoje.day,
            defensoria=atendimento.defensoria,
            defensor=atendimento.defensor,
            atendimento_ptr__qualificacao=atendimento.qualificacao,
        )

        if atendimento.tipo != 1:
            check = check.filter(inicial=atendimento.at_inicial)
        else:
            check = check.filter(id=atendimento.id)

        return not check.exists()
    else:
        return True


def cria_nome_unico(nome_arquivo: str) -> str:
    id_unico = gera_identificador_unico(4)
    extensao_arquivo = get_extensao_arquivo(nome_arquivo)

    if extensao_arquivo:
        nome_partes = nome_arquivo.split(".")
        nome_partes.remove(extensao_arquivo)
        extensao_arquivo = "." + extensao_arquivo

        return ".".join(nome_partes) + f"({id_unico}){extensao_arquivo}"

    return f"{nome_arquivo}({id_unico})"


def compacta_documentos(arquivos: Dict[str, List[str]], nome_arquivo: str) -> object:
    CAMINHO_ARQUIVO = 0
    NOME_DESCRITIVO = 1

    with ZipFile(nome_arquivo, 'w') as arquivo_compactado:
        for nome_pasta in arquivos.keys():
            lista_nomes_arquivos = []
            for arquivo in arquivos[nome_pasta]:
                caminho_arquivo = arquivo[CAMINHO_ARQUIVO]
                nome_original = caminho_arquivo.split("/")[-1]

                nome_temporario = ""
                nome_descritivo = arquivo[NOME_DESCRITIVO]

                if nome_descritivo:
                    extensao_arquivo = get_extensao_arquivo(nome_original)
                    nome_temporario = f"{nome_descritivo}.{extensao_arquivo}" if extensao_arquivo else nome_descritivo
                else:
                    nome_temporario = nome_original

                if lista_nomes_arquivos.count(nome_temporario):
                    nome_temporario = cria_nome_unico(nome_temporario)

                lista_nomes_arquivos.append(nome_temporario)

                novo_nome = f"{nome_pasta}/{nome_temporario}"
                arquivo_compactado.writestr(novo_nome, open(caminho_arquivo, 'rb').read())

        return arquivo_compactado.filename


def filtra_valida_download_ged(documentos_ged: List[str]) -> List[object]:
    baixar_somente_assinado = not config.GED_PODE_BAIXAR_DOCUMENTO_NAO_ASSINADO
    documentos_filtrados = DocumentoGED.objects.filter(pk_uuid__in=documentos_ged)

    if baixar_somente_assinado:
        documentos_filtrados = documentos_filtrados.filter(esta_assinado=True)

    return documentos_filtrados


def cria_diretorio(dir_path: str):
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def converte_ged_pdf(documento_ged: object, filename: str) -> str:
    ged_pdf_service = GedToPDFService(documento_ged)
    ged_pdf_service.export_to_file(filename)

    return filename


def filtra_documentos_atendimento(documentos_solicitados: List[int],
                                  atendimento_numero: str) -> object:
    atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero)

    return atendimento.documentos.filter(id__in=documentos_solicitados)


def filtra_documentos_assistido(atendimento_numero: str,
                                arquivos_solicitados: List[int]) -> List[str]:
    atendimento = AtendimentoDefensor.objects.get(numero=atendimento_numero)

    assistido_documentos = AtendimentoPessoa.objects.filter(
            pessoa__documentos__ativo=True,
            atendimento=atendimento.at_inicial,
            ativo=True,
            pessoa__documentos__pk__in=arquivos_solicitados
        ).annotate(
            arquivo=F('pessoa__documentos__arquivo'),
            nome_descritivo=F('pessoa__documentos__nome')
        ).values('arquivo', 'nome_descritivo')

    return (((settings.MEDIA_URL + documento['arquivo'])[1:],
             documento["nome_descritivo"])
            for documento in assistido_documentos)


def filtro_situacoes(situacoes: List[int]) -> Q:
    '''
        Retorna query com filtros para a lista de situações fornecidas

            Parameters:
                    situacoes (List[int]): lista com os ids das situações a serem filtradas

            Returns:
                    query (Q): Query com todos os fitros por situação
    '''
    filtro_situacao = {
        Tarefa.TAREFA_FINALIZADA: Q(data_finalizado__isnull=False),
        Tarefa.TAREFA_CUMPRIDA: Q(data_finalizado=None, status=Tarefa.STATUS_CUMPRIDO),
        Tarefa.TAREFA_PENDENCIA: Q(data_finalizado=None, status=Tarefa.STATUS_PENDENTE),
        Tarefa.TAREFA_ATRASADA: Q(data_finalizado=None, status=Tarefa.STATUS_CADASTRO, data_final__lt=date.today()),
        Tarefa.TAREFA_AGUARDANDO: Q(data_finalizado=None, status=Tarefa.STATUS_CADASTRO) & (
                                    Q(data_final__gte=date.today()) | Q(data_final__isnull=True)),
        Tarefa.TAREFA_EXCLUIDA: Q(ativo=False)
    }

    q = Q()

    for situacao in situacoes:
        q |= filtro_situacao[situacao]

    return q


def filtro_prioridades(prioridades: List[int]) -> Q:
    '''
        Retorna query com filtros para a lista de prioridades fornecidas

            Parameters:
                    prioridades (List[int]): lista com os ids das prioridades a serem filtradas

            Returns:
                    query (Q): Query com todos os fitros por situação
    '''

    filtro_prioridade = {
        Tarefa.PRIORIDADE_URGENTE: Q(ativo=True, prioridade=Tarefa.PRIORIDADE_URGENTE),
        Tarefa.PRIORIDADE_ALTA: Q(ativo=True, prioridade=Tarefa.PRIORIDADE_ALTA),
        Tarefa.PRIORIDADE_NORMAL: Q(ativo=True, prioridade=Tarefa.PRIORIDADE_NORMAL),
        Tarefa.PRIORIDADE_BAIXA: Q(ativo=True, prioridade=Tarefa.PRIORIDADE_BAIXA),
        Tarefa.PRIORIDADE_ALERTA: Q(ativo=True, prioridade=Tarefa.PRIORIDADE_ALERTA),
        Tarefa.PRIORIDADE_COOPERACAO: Q(ativo=True, prioridade=Tarefa.PRIORIDADE_COOPERACAO)
    }

    q = Q()

    for prioridade in prioridades:
        q |= filtro_prioridade[prioridade]

    return q


def filtra_tarefas(dados_filtragem) -> Q:
    """
        Retorna query com filtros para os dados fornecidos. Esta função foi baseada nos
        filtros que eram contidos na view de listar tarefas.

        Parameters:
                dados_filtragem (Dict[str, Any]): dicionário com os dados a serem utilizados nos filtros

        Returns:
                query (Q): Query com todos os fitros para os dados fornecidos
    """
    q = Q()

    # Filtro por prazo maior ou igual a data inicial
    if dados_filtragem.get('data_inicial'):
        q &= Q(data_final__gte=dados_filtragem.get('data_inicial'))

    # Filtro por prazo menor ou igual a data final
    if dados_filtragem.get('data_final'):
        q &= Q(data_final__lte=dados_filtragem.get('data_final'))

    # Filtro por setor responsável (defensoria)
    if dados_filtragem.get('setor_responsavel'):
        q &= Q(setor_responsavel=dados_filtragem.get('setor_responsavel'))

    # Filtro por servidor responsável
    responsavel = dados_filtragem.get('responsavel')
    if responsavel:
        q &= Q(responsavel__defensor=responsavel)

    # Filtro por situação
    situacoes = dados_filtragem.get('situacao')
    if situacoes is not None:
        q &= filtro_situacoes(situacoes)

    # Filtro por prioridade
    prioridades = dados_filtragem.get('prioridade')
    if prioridades is not None:
        q &= filtro_prioridades(prioridades)

    if (not situacoes) or (Tarefa.TAREFA_EXCLUIDA not in situacoes):
        # Por padrão as tarefas excluídas não devem ser exibidas para coincidir com total exibido no painel
        q &= Q(ativo=True)

    return q


def swap_ordenacao_tarefas(ordena_por: str) -> str:
    """
        Retorna nome de coluna invertendo a ordenação de entrada (ASC/DESC)
        Parameters:
                ordena_por (str): Nome da coluna a ser invertida
        Returns:
                coluna (str): Nome da coluna ASC/DESC
    """

    ordenacao = {
        "data_final": "-data_final",
        "-data_final": "data_final"
    }

    return ordenacao.get(ordena_por, "")


def get_tarefas_propac():
    """
        Retorna queryset com Tarefas de propac/procedimento para ser utilizado na tela de listagem de tarefas
        Returns:
                queryset (Q): queryset com tarefas propac/procedimento
    """
    return Tarefa.objects.annotate(
        respondido_por=F('all_respostas__finalizado__nome'),
        respondido_por_username=F('all_respostas__finalizado__usuario__username'),
    ).filter(
        movimento__isnull=False
    ).order_by(
        'data_inicial',
        'prioridade',
        'data_final',
        'id'
    ).distinct(
        'data_inicial',
        'prioridade',
        'data_final',
        'id'
    )


def arquivamento_esta_habilitado() -> bool:
    return Qualificacao.objects.filter(tipo__in=[
        Qualificacao.TIPO_ARQUIVAMENTO_COM_RESOLUCAO,
        Qualificacao.TIPO_ARQUIVAMENTO_SEM_RESOLUCAO,
        Qualificacao.TIPO_DESARQUIVAMENTO
    ]).exists()


def consulta_status_arquivado(atendimentos_ids: List[int]) -> dict:
    atendimentos = Atendimento.objects.filter(numero__in=atendimentos_ids).all()
    return {atendimento.numero: atendimento.arquivado for atendimento in atendimentos}
