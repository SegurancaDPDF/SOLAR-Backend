from unittest import TestCase, skip
from atendimento.atendimento.services import (
    gera_identificador_unico,
    cria_nome_unico
)
from contrib.services import get_extensao_arquivo


class TestServices(TestCase):

    def test_deve_gerar_identificador_unico(self):
        uid1 = gera_identificador_unico()
        uid2 = gera_identificador_unico()

        self.assertNotEqual(uid1, uid2)

    def test_deve_gerar_identificador_unico_com_tamanho_de_5_caracteres(self):
        uid = gera_identificador_unico(length=5)
        self.assertEqual(len(uid), 5)

    def test_deve_recuperar_extensao_do_nome_do_arquivo(self):
        arquivos = (
            ("arquivo.py", "py"),
            ("arquivo.teste.pdf", "pdf"),
            ("arquivo_sem_extensao", "")
        )

        for arquivo, extensao in arquivos:
            with self.subTest(arquivo=arquivo, extensao=extensao):
                self.assertEqual(get_extensao_arquivo(arquivo), extensao)

    def test_deve_criar_nome_unico(self):
        nome_original = "arquivo_teste.pdf"
        nome_unico = cria_nome_unico(nome_original)

        self.assertNotEqual(nome_original, nome_unico)

    @skip("TODO: implementar este teste")
    def test_deve_filtrar_e_validar_permissao_de_documentos_ged(self, *args, **kwargs):
        """
            TODO implementar este teste assim que resolver o problema das migrations do Solar,
            O TestCase default do django não conseguiu aplicar todas migrations
            Também ocorreram problemas ao tentar utilizar o pytest-django para mockar os models.
        """
        self.fail("Isso não deveria acontecer")

    @skip("TODO: implementar este teste")
    def test_deve_exportar_documento_ged_para_pdf(self, *args, **kwargs):
        """
            TODO implementar este teste assim que resolver o problema das migrations do Solar,
            O TestCase default do django não conseguiu aplicar todas migrations
            Também ocorreram problemas ao tentar utilizar o pytest-django para mockar os models.
        """
        self.fail("Isso não deveria acontecer")
