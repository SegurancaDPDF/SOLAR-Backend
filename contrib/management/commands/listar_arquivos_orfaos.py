# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import io

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path  # pip install pathlib2

from django.conf import settings
from django.template.defaultfilters import filesizeformat
from django.core.management.base import BaseCommand
import six
from atendimento.atendimento.models import Documento as DocumentoAtendimento
from assistido.models import Documento as DocumentoAssistido


def get_media_path_instance(subpath_of_media):
    # retorna uma instância do objeto Path representando o caminho completo do subdiretório dentro do diretório de mídia
    return Path(settings.MEDIA_ROOT, subpath_of_media)


def get_all_media_files_set_of_folder(folder_name):
    media_path = get_media_path_instance(folder_name)
    # retorna um conjunto de todos os arquivos (como strings) presentes na pasta, incluindo subdiretórios
    return {six.text_type(arq) for arq in media_path.glob('**/*') if arq.is_file()}


def sum_sizes(files_path_list):
    root_path = Path(settings.ROOT_PATH)
    # retorna a soma total dos tamanhos dos arquivos na lista de caminhos fornecida
    return sum((root_path.joinpath(arq).stat().st_size for arq in files_path_list))


class Command(BaseCommand):
    help = "Lista todos os arquivos que existem em disco, mas que não existem em banco"

    def handle(self, *args, **options):
        media_path = Path(settings.ROOT_PATH, 'media')
        ###############################################################
        print("processando atendimento....")
        arqs_atendimento_em_disco = get_all_media_files_set_of_folder('atendimento')
        arqs_atendimento_em_banco = {six.text_type(media_path.joinpath(arq)) for arq in
                                     DocumentoAtendimento.objects.exclude(arquivo=None).filter(ativo=True).values_list(
                                         'arquivo', flat=True)}

        arqs_atendimento_so_existem_em_disco = arqs_atendimento_em_disco - arqs_atendimento_em_banco
        atendimento_size = filesizeformat(sum_sizes(arqs_atendimento_so_existem_em_disco))

        with io.open(file='docs_orfaos_atendimento.txt', mode='w', encoding='utf-8') as f:
            print("gravando docs_orfaos_atendimento.txt...")
            f.write("\n".join(arqs_atendimento_so_existem_em_disco))
            f.write("\n____\n")
            f.write("total tamanho em disco: {}".format(atendimento_size))

        ###############################################################
        print("processando assistido....")
        arqs_assistido_em_disco = get_all_media_files_set_of_folder('assistido')

        arqs_assistido_em_banco = {six.text_type(media_path.joinpath(arq)) for arq in
                                   DocumentoAssistido.objects.exclude(arquivo=None).filter(ativo=True).values_list(
                                       'arquivo', flat=True)}

        arqs_assistido_so_existem_em_disco = arqs_assistido_em_disco - arqs_assistido_em_banco
        assistido_size = filesizeformat(sum_sizes(arqs_assistido_so_existem_em_disco))

        with io.open(file='docs_orfaos_assistido.txt', mode='w', encoding='utf-8') as t:
            print("gravando docs_orfaos_assistido.txt...")
            t.write("\n".join(arqs_assistido_so_existem_em_disco))
            t.write("\n____\n")
            t.write("total tamanho em disco: {}".format(assistido_size))
