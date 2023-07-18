# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
from datetime import datetime

# Bibliotecas de terceiros
import json as simplejson
import re
import reversion
from constance import config
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from django.http import JsonResponse, Http404
from django.shortcuts import redirect, render

# Solar
from contrib.models import Util, Servidor
from contrib.forms import ServidorFotoForm
from procapi_client.services import APIManifestante, APISistema
from defensor.models import Defensor


@login_required
def editar_perfil(request):

    if request.user.servidor.uso_interno:
        raise Http404
    else:

        defensor = None
        tem_atuacoes = False
        credenciais = []

        if hasattr(request.user.servidor, 'defensor'):

            defensor = request.user.servidor.defensor

            # Busca as atuações em que o chat está habilitado para configurar na modal Visualizar Chat (por atuação)
            atuacoes = defensor.atuacoes_vigentes().filter(
                Q(habilitado_chat_edefensor=True)
            ).order_by('data_cadastro')

            tem_atuacoes = atuacoes.exists()

            # Busca credenciais de acesso ao MNI
            if config.ATIVAR_PROCAPI:

                sistemas = APISistema().listar_todos(params={'deve_enviar_manifestante': True})
                consultantes = APIManifestante().listar_todos(params={'cpf': request.user.servidor.cpf})

                for sistema in sistemas:
                    sistema_adicionado = False
                    for consultante in consultantes:
                        if sistema['nome'] in consultante['sistema']:
                            consultante['sistema'] = sistema['nome']
                            credenciais.append(consultante)
                            sistema_adicionado = True
                            break
                    if not sistema_adicionado:
                        credenciais.append({
                            'sistema': sistema['nome']
                        })

    return render(request=request, template_name="perfil/editar_dados_usuario.html", context={
        'defensor': defensor,
        'tem_atuacoes': tem_atuacoes,
        'atuacoes': atuacoes,
        'credenciais': credenciais,
        'tab': request.GET.get('tab', 0),
        'angular': 'PerfilUsuarioCtrl'
    })


@login_required
@reversion.create_revision(atomic=False)
def editar_foto(request):
    if request.method == 'POST':

        form = ServidorFotoForm(request.POST, request.FILES)
        if form.is_valid():
            servidor = Servidor.objects.get(pk=request.user.servidor.id)
            servidor.foto.save('nomealeatorio.jpeg', form.cleaned_data['foto'], save=True)
            messages.success(request, u'Foto do perfil alterada com sucesso!')

    return redirect('editar_perfil')


@login_required
@reversion.create_revision(atomic=False)
def editar_email(request):
    erro = True
    mensagem = 'Dados inválidos'
    if request.method == 'POST':
        dados = simplejson.loads(request.body)
        user = request.user
        email = dados['email']
        valid_mail = re.search(r'[\w.-]+@[\w.-]+.\w+', dados['email'])
        if email and valid_mail:
            user.email = email
            user.save()
            mensagem = 'E-mail alterado com sucesso!'
            reversion.set_user(request.user)
            reversion.set_comment(Util.get_comment_save(request.user, user, False))
            erro = False
        else:
            mensagem = 'E-mail inválido!'

    return JsonResponse({'erro': erro, 'mensagem': mensagem})


@login_required
@reversion.create_revision(atomic=False)
def configurar_visualizacao_chat_por_atuacao(request):
    erro = True
    mensagem = 'Dados inválidos'

    if request.method == 'POST':

        if hasattr(request.user.servidor, 'defensor'):
            dados = simplejson.loads(request.body)
            user = request.user

            # Pega o defensor interno do servidor
            defensor = request.user.servidor.defensor

            # Pega a lista de ids das atuações a ativar (ou manter ativada)
            atuacoes_a_ativar_id_list = dados['atuacoes_a_ativar_id_list']
            atuacoes_a_ativar_id_list = simplejson.loads(atuacoes_a_ativar_id_list)

            # Busca as atuações vigentes do usuário cuja id seja uma passada para o formulário
            atuacoes = defensor.atuacoes_vigentes().filter(
                Q(habilitado_chat_edefensor=True)
            ).order_by('data_cadastro')

            # Cria uma consulta filtrando estas atuações para obter só as que serão "ativadas" e ativa elas
            atuacoes.filter(
                Q(id__in=atuacoes_a_ativar_id_list)
            ).update(
                visualiza_chat_edefensor=True
            )
            # Cria uma consulta filtrando estas atuações para obter só as que NÃO serão "ativadas" e desativa elas
            atuacoes.exclude(
                Q(id__in=atuacoes_a_ativar_id_list)
            ).update(
                visualiza_chat_edefensor=False
            )

            mensagem = 'Dados alterados com sucesso!'
            reversion.set_user(request.user)
            reversion.set_comment(Util.get_comment_save(request.user, user, False))
            erro = False

        else:
            mensagem = 'Algo deu errado ao tentar obter informações do usuário'

    return JsonResponse({'erro': erro, 'mensagem': mensagem})


@login_required
@reversion.create_revision(atomic=False)
def editar_senha(request):
    erro = True
    mensagem = 'Dados inválidos'

    if request.method == 'POST':
        dados = simplejson.loads(request.body)
        user = request.user
        senha_antiga = dados['senha_antiga']
        senha_nova = dados['senha_nova']
        senha_confirma = dados['senha_confirma']

        if senha_antiga and senha_nova and senha_confirma:
            if senha_nova == senha_confirma:
                if user.check_password(senha_antiga):
                    try:
                        validate_password(senha_nova, user)
                    except Exception:
                        mensagem = 'A nova senha não atende aos critérios de segurança!'
                    else:
                        user.set_password(senha_confirma)
                        mensagem = 'Dados alterados com sucesso!'
                        user.save()
                        reversion.set_user(request.user)
                        reversion.set_comment(Util.get_comment_save(request.user, user, False))
                        erro = False
                else:
                    mensagem = 'Senha atual inválida!'
            else:
                mensagem = 'Nova senha não confere!'

    return JsonResponse({'erro': erro, 'mensagem': mensagem})


@login_required
@reversion.create_revision(atomic=False)
def editar_senha_eproc(request):

    sucesso = False
    mensagem = 'As credenciais informadas não são válidas!'

    if request.method == 'POST':

        dados = simplejson.loads(request.body)

        # Valida credenciais informadas pelo manifestante
        sucesso, _ = APIManifestante().validar_credenciais(
            sistema_webservice=dados.get('sistema'),
            usuario=dados.get('usuario'),
            senha=dados.get('senha_eproc'),
            cpf=request.user.servidor.cpf
        )

        if sucesso:
            mensagem = 'As credenciais foram validadas com sucesso!'

    return JsonResponse({'sucesso': sucesso, 'mensagem': mensagem})


@login_required
@reversion.create_revision(atomic=False)
def editar_usuario_projudi(request):

    sucesso = False
    mensagem = 'Método ativo somente para POST'

    if request.method == 'POST':

        dados = simplejson.loads(request.body)
        usuario_eproc = dados.get('usuario_projudi')
        user = request.user

        if usuario_eproc is None:
            usuario_eproc = ""

        user.servidor.defensor.usuario_eproc = usuario_eproc
        user.save()

        Defensor.objects.filter(
            servidor__cpf=request.user.servidor.cpf
        ).update(
            usuario_eproc=usuario_eproc
        )

        mensagem = 'A credencial foi atualizada com sucesso!'
        reversion.set_user(request.user)
        reversion.set_comment(Util.get_comment_save(request.user, user, False))
        sucesso = True

    return JsonResponse({'sucesso': sucesso, 'mensagem': mensagem})


@login_required
def atualizacoes(request):
    from contrib.models import Atualizacao

    servidor = request.user.servidor

    if servidor.data_atualizacao is None:
        novas = Atualizacao.objects.filter(ativo=True).order_by('-data')
        velhas = []
    else:
        novas = Atualizacao.objects.filter(ativo=True, data__gt=servidor.data_atualizacao).order_by('-data')
        velhas = Atualizacao.objects.filter(ativo=True, data__lt=servidor.data_atualizacao).order_by('-data')

    servidor.data_atualizacao = datetime.now()
    servidor.save()

    return render(request=request, template_name="perfil/atualizacoes.html", context=locals())


@user_passes_test(lambda u: u.is_superuser)
def perfil_admin(request):

    services = [
        {
            'name': 'SOLAR',
            'description': 'Configurações Gerais',
            'internal': True,
            'arguments': [
                {
                    'name': 'NOME_INSTITUICAO',
                    'type': 'text',
                    'label': 'Nome da Defensoria',
                    'constance': True,
                },
                {
                    'name': 'CNPJ_INSTITUICAO',
                    'type': 'text',
                    'label': 'CNPJ da Defensoria (somente números)',
                    'constance': True,
                },
                {
                    'name': 'SIGLA_INSTITUICAO',
                    'type': 'text',
                    'label': 'Sigla da Instituição'
                },
                {
                    'name': 'SIGLA_UF',
                    'type': 'text',
                    'label': 'Sigla UF',
                    'readyonly': True
                },
                {
                    'name': 'LOGO_MENU',
                    'type': 'text',
                    'label': 'Url da logo da defensoria'
                },
                {
                    'name': 'LOGO_POSITION_LEFT',
                    'type': 'bool',
                    'label': 'Se a logo estará do lado esquerdo'
                },
                {
                    'name': 'NOME_INSTITUICAO_NO_HEADER',
                    'type': 'bool',
                    'label': 'Se o nome da instituição aparece no topo'
                },
                {
                    'name': 'COR_HEADER_BG',
                    'type': 'color',
                    'label': 'Altera a cor do background do header sistema'
                },
                {
                    'name': 'COR_HEADER_FONT',
                    'type': 'color',
                    'label': 'Altera a cor das letras do header'
                },
                {
                    'name': 'COR_MENU_BG',
                    'type': 'color',
                    'label': 'Altera a cor do background do menu do sistema'
                },
                {
                    'name': 'COR_MENU_ICON',
                    'type': 'color',
                    'label': 'Altera a cor das letras do menu'
                },
                {
                    'name': 'JSVERSION',
                    'type': 'number',
                    'label': 'Versão dos arquivos .js (Formato: AAAAMMDDHHmm)'
                },
                {
                    'name': 'URL_DO_ASSINADOR',
                    'type': 'text',
                    'label': 'URL da Aplicação Desktop do Assinador que esteja escutando requisições'
                },
                {
                    'name': 'PORTA_DO_ASSINADOR',
                    'type': 'text',
                    'label': 'URL da Aplicação Desktop do Assinador que esteja escutando requisições'
                },
                {
                    'name': 'URL_THOTH_SIGNER',
                    'type': 'text',
                    'label': 'URL do assinador Thoth Signer, ex: http://ipouhostname:9001/'
                },
                {
                    'name': 'FORMATO_SUPORTADO_UPLOADS',
                    'type': 'text',
                    'label': '[DEPRECIADO] Define o formato de arquivos aceito no upload dos formulários, utilizar o padrão: .pdf,.mp3,.mp4,.ogg,.doc,.docx etc... '  # noqa: E501
                },
                {
                    'name': 'ATIVAR_ETIQUETA_SIMPLIFICADA',
                    'type': 'bool',
                    'label': 'Ativa a função de criação simplificada de etiquetas'
                }
            ],
        },
        {
            'name': 'SOLAR > Assistidos',
            'description': 'Configurações no Cadastro de Assistidos',
            'internal': True,
            'arguments': [
                {
                    'name': 'EXIBIR_ALERTA_HIPOSSUFICIENCIA',
                    'type': 'bool',
                    'label': 'Exibir alerta de hipossuficiência no cadastro do usuário e no atendimento?',
                },
                {
                    'name': 'EXIBIR_ALERTA_AVALIACAO_ASSISTIDO',
                    'type': 'bool',
                    'label': 'Exibir alerta de avaliação do assistido?',
                },
                {
                    'name': 'MENSAGEM_ALERTA_AVALIACAO_ASSISTIDO',
                    'type': 'textarea',
                    'label': 'Mensagem de alerta na avaliação do assistido'
                },
                {
                    'name': 'MENSAGEM_RENDA_ASSISTIDO_INDIVIDUAL',
                    'type': 'textarea',
                    'label': 'Mensagem no campo "Renda Individual" no Cadastro do Assistido'
                },
                {
                    'name': 'MENSAGEM_RENDA_ASSISTIDO_FAMILIAR',
                    'type': 'textarea',
                    'label': 'Mensagem no campo "Renda Familiar" no Cadastro do Assistido'
                },
                {
                    'name': 'MENSAGEM_VALOR_SALARIO_FUNCIONARIO',
                    'type': 'textarea',
                    'label': 'Mensagem no campo "Salário do Funcionário" no Cadastro do Assistido'
                },
                {
                    'name': 'MENSAGEM_VALOR_INVESTIMENTOS',
                    'type': 'textarea',
                    'label': 'Mensagem no campo "Investimentos" no Cadastro do Assistido'
                },
                {
                    'name': 'EXIBIR_NAO_POSSUI_NOS_CAMPOS_OPCIONAIS',
                    'type': 'bool',
                    'label': 'Exibir "Não possui" nos campos opicionais do cadastro do assistido?'
                },
                {
                    'name': 'ATIVAR_ZAP_DEFENSORIA',
                    'type': 'bool',
                    'label': 'Ativa/Desativa a opção Zap Defensoria'
                },
                {
                    'name': 'CALCULAR_RENDA_FAMILIAR_E_MEMBROS_ASSISTIDO',
                    'type': 'bool',
                    'label': 'Calcular a renda familiar e número de membros no cadastro do assistido automaticamente?'
                },
                {
                    'name': 'SITUACOES_SIGILOSAS',
                    'type': 'text',
                    'label': 'Códigos (sem caracteres especiais) das situações do assistido onde deverá ser aplicado o sigilo caso seja selecionada. Utilize vírgula para separar caso exista mais de uma.'  # noqa: E501
                },
                {
                    'name': 'NOTIFICACAO_SOLICITACAO_SIGILO',
                    'type': 'bool',
                    'label': 'Enviar email notificando usuários do pedido de solicitação de acesso? (necessário configurar DEFAULT_FROM_EMAIL no .env)',  # noqa: E501
                },
                {
                    'name': 'ATIVAR_BOTAO_PRE_CADASTRO',
                    'type': 'bool',
                    'label': 'Caso ativado, ficará disponível o botão PRE CADASTRAR REQUERIDO/REQUERENTE, que possibilita a criação e vinculação de assistido com um numero de informações resumidas',  # noqa: E501
                },
                {
                    'name': 'EXIBIR_ALERTA_PRE_CADASTRO',
                    'type': 'bool',
                    'label': 'Exibi alerta no pré cadastro do assistido?',
                },
                {
                    'name': 'MENSAGEM_ALERTA_PRE_CADASTRO',
                    'type': 'textarea',
                    'label': 'Mensagem de alerta no pré cadastro do assitido'
                },
                {
                    'name': 'ASSISTIDO_ENDERECO_VALIDAR_CEP',
                    'type': 'bool',
                    'label': 'Validar CEP nos Correios (Bloqueia preenchimento da UF, município, bairro e logradouro)'
                },
                {
                    'name': 'ASSISTIDO_TELEFONE_TIPO_PADRAO',
                    'type': 'select',
                    'label': 'Tipo de Telefone Padrão no Cadastro do Assistido',
                    'options': {
                        0: 'Celular',
                        1: 'Residencial',
                        2: 'Comercial',
                        3: 'Recado',
                        4: 'WhatsApp',
                        5: 'SMS',
                    },
                },
            ],
        },
        {
            'name': 'SOLAR > 129',
            'description': 'Configurações do módulo 129',
            'internal': True,
            'arguments': [
                {
                    'name': 'EXIBIR_ALERTA_AVALIACAO_ASSISTIDO_129',
                    'type': 'bool',
                    'label': 'Exibir alerta de avaliação do assistido no 129?',
                },
                {
                    'name': 'MENSAGEM_ALERTA_AVALIACAO_ASSISTIDO_129',
                    'type': 'textarea',
                    'label': 'Mensagem de alerta na avaliação do assistido no 129'
                },
                {
                    'name': 'MODO_EXIBICAO_ENDERECO_129',
                    'type': 'select',
                    'label': 'Modo de exibição do endereço no 129',
                    'options': {
                        0: 'Apenas Município/UF',
                        1: 'Completo',
                    },
                },
                {
                    'name': 'LEMBRETE_129_EMAIL_ENCAMINHAMENTO',
                    'type': 'textarea',
                    'label': 'Template de e-mail para procedimento 129 de encaminhamento'
                },
                {
                    'name': 'LEMBRETE_129_EMAIL_DUVIDAS',
                    'type': 'textarea',
                    'label': 'Template de e-mail para procedimento 129 de dúvidas'
                },
                {
                    'name': 'LEMBRETE_129_EMAIL_RECLAMACAO',
                    'type': 'textarea',
                    'label': 'Template de e-mail para procedimento 129 de reclamação'
                },
                {
                    'name': 'LEMBRETE_129_EMAIL_INFORMACAO',
                    'type': 'textarea',
                    'label': 'Template de e-mail para procedimento 129 de informação'
                },
                {
                    'name': 'LEMBRETE_129_EMAIL_AGENDAMENTO',
                    'type': 'textarea',
                    'label': 'Template de e-mail para procedimento 129 de agendamento'
                },
                {
                    'name': 'LEMBRETE_EMAIL_AGENDAMENTO_ONLINE',
                    'type': 'textarea',
                    'label': 'Template de e-mail agendamento on-line (DPE-AM)'
                },
            ],
        },
        {
            'name': 'SOLAR > Agenda/Agendamento',
            'description': 'Configurações do módulo Agenda/Agendamento',
            'internal': True,
            'arguments': [
                {
                    'name': 'HORA_INICIAL_AGENDA_DEFENSOR',
                    'type': 'time',
                    'label': 'Hora padrão para cadastro de agenda de defensor',
                },
                {
                    'name': 'SIMULTANEOS_AGENDA_DEFENSOR',
                    'type': 'number',
                    'label': 'Valor padrão do campo simultâneos para cadastro de agenda de defensor',
                },
                {
                    'name': 'MODO_EXIBICAO_ATUACAO_AO_AGENDAR',
                    'type': 'select',
                    'label': 'Modo de exibição defensor/defensoria no agendamento',
                    'options': {
                        '{atuacao.defensor.nome} - {atuacao.defensoria.nome}': 'Defensor - Defensoria',
                        '{atuacao.defensoria.nome} - {atuacao.defensor.nome}': 'Defensoria - Defensor',
                        '{atuacao.defensoria.nome}': 'Defensoria',
                        '{atuacao.defensoria.atuacao} - {atuacao.defensoria.nome} - {atuacao.defensor.nome}': 'Atuação - Defensoria - Defensor',
                        '{atuacao.defensor.nome} - {atuacao.defensoria.nome} - {atuacao.defensoria.atuacao}': 'Defensor - Defensoria - Atuação'
                    },
                },
                {
                    'name': 'COR_HOJE_AGENDA',
                    'type': 'color',
                    'label': 'Altera a cor do background do dia de hoje na agenda'
                },
                {
                    'name': 'EXIBIR_OFICIO_AGENDAMENTO',
                    'type': 'bool',
                    'label': 'Ativa/Desativa informações de ofício no agendamento',
                },
                {
                    'name': 'EXIBIR_PRESENCIAL_REMOTO_AGENDAMENTO',
                    'type': 'bool',
                    'label': 'Ativa/Desativa identificação Presencial/Remoto nas agendas e agendamento',
                },
                {
                    'name': 'CONVERTER_PRIMEIRO_ENCAMINHAMENTO_EM_INICIAL',
                    'type': 'bool',
                    'label': 'Ativa/Desativa conversão do primeiro encaminhamento em inicial (multidisciplinar > defensoria)',  # noqa: E501
                },
                {
                    'name': 'EXIBIR_DATA_ATUACAO',
                    'type': 'bool',
                    'label': 'Mostra/Oculta informações de datas do período de atuação',
                },
                {
                    'name': 'EXIBIR_ATUACAO_DEFENSORIA',
                    'type': 'bool',
                    'label': 'Mostra/Oculta informação da atuação do ofício/defensoria',
                },
                {
                    'name': 'WHATSAPP_INCLUIR_NOME_DEFENSOR',
                    'type': 'bool',
                    'label': 'Incluir nome do defensor na mensagem Whatsapp?',
                },
                {
                    'name': 'SOMENTE_DEFENSORIAS_MESMA_AREA',
                    'type': 'bool',
                    'label': 'Filtra pelas defensorias da mesma área (família, cível etc) da qualificação selecionada ao ser feito um agendamento',
                },
                {
                    'name': 'BLOQUEAR_AGENDAMENTO_ENTRE_DEFENSORIAS',
                    'type': 'bool',
                    'label': 'Bloqueia o agendamento entre as defensorias. Somente quem atua na defensoria ou que faça parte do GrupoDeDefensoriasParaAgendamento podem agendar.',
                },

            ],
        },
        {
            'name': 'SOLAR > Atendimento',
            'description': 'Configurações do módulo Atendimento',
            'internal': True,
            'arguments': [
                {
                    'name': 'NOME_MODULO_ATENDIMENTO',
                    'type': 'text',
                    'label': 'Nome alternativo para o módulo "Atendimento"',
                },
                {
                    'name': 'NOME_ANOTACAO_DEFENSOR',
                    'type': 'text',
                    'label': 'Descrição alternativa para o campo "Anotações do Defensor"',
                },
                {
                    'name': 'ATIVAR_ORDENACAO_ATENDIMENTO_DECRESCENTE',
                    'type': 'bool',
                    'label': 'Ativa/Desativa ordenação de atendimentos na aba histórico forma decrescente (mais novo primeiro)'  # noqa: 501
                },
                {
                    'name': 'LIBERAR_ATENDIMENTO_PJ_SEM_PF',
                    'type': 'bool',
                    'label': 'Liberar atendimentos de requerente Pessoa Jurídica sem ter Pessoa Física vinculada'
                },
                {
                    'name': 'REGISTRAR_ANOTACAO_EM_AGENDAMENTO',
                    'type': 'bool',
                    'label': 'Registrar anotação em agendamento?'
                },
                {
                    'name': 'REGISTRAR_VISUALIZACAO_ATENDIMENTO_SUPERUSUARIO',
                    'type': 'bool',
                    'label': 'Registrar visualização de tarefa se superusuário?'
                },
                {
                    'name': 'BUSCAR_ATENDIMENTOS_FILTRO_NOME_MIN_CARACTERES',
                    'type': 'number',
                    'label': 'Mínimo de caracteres para busca de atendimentos pelo nome da pessoa'
                },
                {
                    'name': 'BUSCAR_ATENDIMENTOS_FILTRO_NOME_MAX_PESSOAS',
                    'type': 'number',
                    'label': 'Máximo de pessoas para busca de atendimentos pelo nome da pessoa'
                },
                {
                    'name': 'BUSCAR_ATENDIMENTO_EXIBIR_COL_RESPONSAVEL',
                    'type': 'bool',
                    'label': 'Se True, adiciona coluna responsável pelo atendimento na Busca de Atendimentos'
                },
                {
                    'name': 'MODO_EXIBICAO_ACESSO_ATENDIMENTO',
                    'type': 'select',
                    'label': 'Modo de exibição mensagem acesso atendimento público/privado',
                    'options': {
                        0: 'Não Exibir',
                        1: 'Exibir - Apenas para Iniciais',
                        2: 'Exibir - Para todos tipos'
                    },
                },
                {
                    'name': 'MODO_EXIBICAO_LISTA_DE_ATENDIMENTOS_DO_ASSISTIDO',
                    'type': 'text',
                    'label': 'Define quais informações aparecerão sobre o atendimento: (1) Anotação da recepção, (2) Anotação do agendamento, (3) Anotação do Defensor, (4) Mensagem de "Nenhum processo vinculado"'  # noqa: E501
                },
                {
                    'name': 'ATIVA_EXIBICAO_ANOTACAO_DEFENSOR_HISTORICO_DE_ATENDIMENTO',
                    'type': 'bool',
                    'label': 'Se True, as anotações do defensor serão exibidas no histórico de atendimentos acima do accordion de "Mostrar/Ocultar Detalhes"'  # noqa: E501
                },
                {
                    'name': 'CONTABILIZAR_ACORDO_TIPO_AMBOS',
                    'type': 'bool',
                    'label': 'Contabilizar como atendimento o acordo em que ambas partes não compareceram?'
                },
                {
                    'name': 'NOME_FORMA_ATENDIMENTO_PADRAO',
                    'type': 'text',
                    'label': 'Nome da Forma de Atendimento Padrão'
                },
                {
                    'name': 'URL_CONDEGE_PETICIONAMENTO',
                    'type': 'text',
                    'label': 'Link para página de Peticionamento Integrado do CONDEGE'
                },
                {
                    'name': 'ATIVAR_BOTAO_ATENDER_AGORA',
                    'type': 'bool',
                    'label': 'Se ativado, exibirá na página de atendimento o botão Atender Agora, que torna a criação de agendamento/atendimento do tipo retorno mais simples, no qual esse botão cria e libera o agendamento/atendimento com 1 click'  # noqa: E501
                },
                {
                    'name': 'ATIVAR_BOTAO_REMETER_ATENDIMENTO',
                    'type': 'bool',
                    'label': 'Se ativado, exibirá na página de atendimento o botão Remeter, que possibilita o encaminhamento para outra defensoria sem marcar um agendamento'  # noqa: E501
                },
                {
                    'name': 'ATIVAR_SIGILO_ABAS_ATENDIMENTO',
                    'type': 'text',
                    'label': 'Define quais abas do atendimento sigiloso ficarão restritas: (1) Documentos, (2) Tarefas / Cooperações, (3) Processos, (4) Outros e (5) Propacs'  # noqa: E501
                },
                {
                    'name': 'EXIBIR_VULNERABILIDADE_DIGITAL',
                    'type': 'bool',
                    'label': 'Exibirá na paǵina de atendimento opções sobre vulnerabilidade digital'
                },
                {
                    'name': 'MENSAGEM_VULNERABILIDADE_DIGITAL',
                    'type': 'textarea',
                    'label': 'Mensagem que ficará no tooltip da vulnerabilidade digital'
                },
                {
                    'name': 'VINCULAR_PROCESSO_COM_ATENDIMENTO_EM_ANDAMENTO',
                    'type': 'bool',
                    'label': 'Permite adicionar processos enquanto estiver em atendimento'
                },
                {
                    'name': 'EXIBIR_NOME_DA_DEFENSORIA_NA_BUSCA_ATENDIMENTOS',
                    'type': 'bool',
                    'label': 'Exibe o nome da defensoria em vez do código na busca de atendimentos'
                },
                {
                    'name': 'ATIVAR_INIBICAO_RETORNO',
                    'type': 'bool',
                    'label': 'Caso ativado, bloqueia os botões de retorno sempre que houver a tentative de abertura de um novo retorno para um atendimento que tenha como data de registro o dia corrente (para o mesmo defensor, mesma defensoria e mesma qualificação)',
                },
                {
                    'name': 'MENSAGEM_INIBICAO_RETORNO',
                    'type': 'textarea',
                    'label': 'Mensagem que ficará no tooltip da inibição do retorno'
                },
            ],
        },
        {
            'name': 'SOLAR > Tarefas',
            'description': 'Configurações das Tarefas',
            'internal': True,
            'arguments': [
                {
                    'name': 'HERDAR_TAREFAS_DOS_SUPERVISIONADOS',
                    'type': 'bool',
                    'label': 'Exibir todas tarefas de servidores supervisionados?'
                },
                {
                    'name': 'EXIBIR_COOPERACOES_CUMPRIDAS_PARA_RESPONSAVEL',
                    'type': 'bool',
                    'label': 'Exibir cooperações cumpridas para o setor responsável?'
                },
                {
                    'name': 'REGISTRAR_VISUALIZACAO_TAREFA_SUPERUSUARIO',
                    'type': 'bool',
                    'label': 'Registrar visualização de tarefa se superusuário?'
                },
                {
                    'name': 'PRE_FILTRAR_TAREFAS_USUARIO_LOGADO',
                    'type': 'bool',
                    'label': 'Pré-filtrar tarefas na tela de listagem pelo usuário logado?'
                },
                {
                    'name': 'DIA_LIMITE_EXIBICAO_TAREFAS_CUMPRIDAS',
                    'type': 'number',
                    'label': 'Dias limite para exibir tarefas cumpridas (Ex: =0 não limita, >0 dia limite exibição'
                },
                {
                    'name': 'NOME_STATUS_TAREFA_0',
                    'type': 'text',
                    'label': 'Nome do status para tarefa com devolução'
                },
                {
                    'name': 'NOME_STATUS_TAREFA_1',
                    'type': 'text',
                    'label': 'Nome do status para tarefa pendente'
                },
                {
                    'name': 'NOME_STATUS_TAREFA_2',
                    'type': 'text',
                    'label': 'Nome do status para tarefa cumprida'
                },
            ],
        },
        {
            'name': 'SOLAR > Painel de Senhas',
            'description': 'Configurações do Painel de Senhas',
            'internal': True,
            'arguments': [
                {
                    'name': 'PAINEL_SENHA_LOGO_URL',
                    'type': 'text',
                    'label': 'URL da logo do painel de senhas'
                },
                {
                    'name': 'PAINEL_SENHA_CORREGEDORIA_ID',
                    'type': 'number',
                    'label': 'ID da Corregedoria'
                },
            ],
        },
        {
            'name': 'SOLAR > Usuários/Lotações',
            'description': 'Configurações de Login, Usuários e Lotações',
            'internal': True,
            'arguments': [
                {
                    'name': 'ENVIAR_EMAIL_AO_CADASTRAR_SERVIDOR',
                    'type': 'bool',
                    'label': 'Enviar email com token para criação de senha ao cadastrar usuário'
                },
                {
                    'name': 'ATIVAR_MULTIPLAS_ATUACOES',
                    'type': 'bool',
                    'label': 'Ativar registro de multiplas atuações na mesma defensoria simultaneamente'
                },
                {
                    'name': 'SHOW_INSCRICAO_PLANTAO',
                    'type': 'bool',
                    'label': 'Ativa/Desativa acesso ao módulo de inscrição a edital de concorrência de plantões'
                }
            ],
            'tasks': [
                {
                    'name': 'Atuações - Desativa atuações encerradas',
                    'description': 'Desativa atuações que atingiram a data final. Obs: Essa task será desativada no futuro após a verificação de validade ser feita exclusivamente pelo período de vigência',  # noqa: E501
                    'task': 'defensor.tasks.desativa_atuacao_encerrada',
                    'arguments': [],
                    'periodic_tasks': [],
                },
            ],
        },
        {
            'name': 'SOLAR > Processos',
            'description': 'Configuração do módulo Processos',
            'internal': True,
            'arguments': [
                {
                    'name': 'NOME_PROCESSO_TJ',
                    'type': 'text',
                    'label': 'Nome do sistema de processos judiciais'
                },
                {
                    'name': 'URL_PROCESSO_TJ',
                    'type': 'text',
                    'label': 'Link para consulta pública processual'
                },
                {
                    'name': 'MODO_EXIBICAO_EVENTOS_PROCESSO_TJ',
                    'type': 'select',
                    'label': 'Modo de exibição dos eventos de processos na aba MNI',
                    'options': {
                        'table': 'Tabela',
                        'timeline': 'Linha do tempo'
                    },
                },
                {
                    'name': 'SHOW_SIDEBAR_PROCESSOS_PENDENTES',
                    'type': 'bool',
                    'label': 'Mostrar caixa de processos pendentes?'
                },
                {
                    'name': 'DIA_LIMITE_CADASTRO_FASE',
                    'type': 'number',
                    'label': 'Dia limite para cadastro de fase do mês anterior (Ex: =0 não corrige, >0 dia limite alteração)'  # noqa: E501
                },
                {
                    'name': 'EXIBIR_DATA_HORA_TERMINO_CADASTRO_AUDIENCIA',
                    'type': 'bool',
                    'label': 'Exibir campo data/hora término no cadastro de audiências'
                },
                {
                    'name': 'VERIFICA_ATUALIZACAO_HONORARIOS',
                    'type': 'bool',
                    'label': 'Gerar alertas de honorarios para cada movimentacao do eproc'
                },
                {
                    'name': 'PROCESSO_CALCULADORA_CALCULO_URL',
                    'type': 'text',
                    'label': 'URL da Calculadora Judicial (Cálculo)'
                },
                {
                    'name': 'PROCESSO_CALCULADORA_CONSULTA_URL',
                    'type': 'text',
                    'label': 'URL da Calculadora Judicial (Consulta)'
                },
                {
                    'name': 'BUSCAR_PROCESSO_DIGITAL_AUTOMATICAMENTE',
                    'type': 'bool',
                    'label': 'Habilita na tela de cadastro de processo a busca automática no PROCAPI caso seja digitado os 20 digitos de um processo'  # noqa: E501
                },
                {
                    'name': 'PERMITE_CADASTRAR_PROCESSO_NAO_LOCALIZADO_OU_COM_ERRO_WEBSERVICE_DO_TJ',
                    'type': 'bool',
                    'label': 'Habilita a possibilidade de deixar usuário cadastrar processo não localizado como físico'  # noqa: E501
                },
                {
                    'name': 'PROCAPI_PERMITE_CADASTRAR_PROCESSO_SIGILOSO',
                    'type': 'bool',
                    'label': 'Se Habilitado, SOLAR irá cadastrar processos não localizados no PROCAPI, presumindo que eles existem e estão sigilosos no TJ'  # noqa: E501
                },
                {
                    'name': 'PERMITE_CADASTRAR_PROCESSO_NAO_LOCALIZADO_COMO_FISICO',
                    'type': 'bool',
                    'label': 'Habilita a possibilidade de deixar usuário cadastrar processo caso a defensoria não esteja habilitado em processo sigiloso ou o webservice do tribunal de justiça apresente erro de conexão no PROCAPI'  # noqa: E501
                },
                {
                    'name': 'VINCULAR_NA_DISTRIBUICAO_AVISO_A_DEFENSORIA_AUTOMATICAMENTE',
                    'type': 'bool',
                    'label': 'Habilita na tela de distribuição de processos a sugestão de defensoria responsável ao aviso automaticamente'  # noqa: E501
                },
                {
                    'name': 'VINCULAR_NA_DISTRIBUICAO_AVISO_A_DEFENSOR_AUTOMATICAMENTE',
                    'type': 'bool',
                    'label': 'Habilita na tela de distribuição de processos a  a sugestão de defensor responsável ao aviso automaticamente'  # noqa: E501
                },
                {
                    'name': 'VINCULAR_NA_DISTRIBUICAO_AVISO_A_PROCESSO_CADASTRADO',
                    'type': 'bool',
                    'label': 'Habilita na tela de distribuição de processos a sugestão a partir de processo previamente cadastrado'  # noqa: E501
                },
                {
                    'name': 'AVISOS_FILTER_DISTRIBUIDO_OPERADOR_LOGICO',
                    'type': 'select',
                    'label': 'AND para filtrar por cpf e defensoria (Padrão); OR para filtrar por cpf ou defensoria.',
                    'options': {
                        'AND': 'CPF e Defensoria (AND)',
                        'OR': 'CPF ou Defensoria (OR)'
                    },
                },
                {
                    'name': 'SUGERIR_DEFENSORIA_E_DEFENSOR_NA_DISTRIBUICAO',
                    'type': 'bool',
                    'label': 'Habilita na tela de distribuição a sugestão de defensoria ou defensor de acordo com a distribuição usada.(por defensoria e/ou defensor)'  # noqa: E501
                },
                {
                    'name': 'HABILITAR_LISTAGEM_GERAL_DE_AVISOS',
                    'type': 'bool',
                    'label': 'Habilita na tela de distribuição a listagem de todos os avisos, pendentes e abertos, quando todos os filtros de busca não forem selecionados.'  # noqa: E501
                },
                {
                    'name': 'LISTA_TIPOS_DOCUMENTOS_EMENDA_INICIAL',
                    'type': 'text',
                    'label': 'Tipos de documentos correspondentes a emenda à inicial'  # noqa: E501
                },
                {
                    'name': 'MAXIMO_DE_RETRY_CELERY',
                    'type': 'number',
                    'label': 'Define numero máximo de tentativas de execução de um task do celery'  # noqa: E501
                },
                {
                    'name': 'ID_FASE_PROCESSUAL_PADRAO_NA_ABERTURA_DE_PRAZOS',
                    'type': 'text',
                    'label': 'Se preenchido, ao ser aberto o prazo de um aviso pelo SOLAR será criado uma fase processual no processo com ID especificado (auditoria)'  # noqa: E501
                },
                {
                    'name': 'ATIVAR_ACOMPANHAMENTO_PROCESSO',
                    'type': 'bool',
                    'label': 'Ativar acompanhamento processual (status parte do processo)'
                },
                {
                    'name': 'DIAS_ACOMPANHAMENTO_PROCESSO',
                    'type': 'number',
                    'label': 'Período para acompanhar a situação do processo no painel do defensor a partir de sua última modificação.'
                },
                {
                    'name': 'EMAIL_PROCESSO_MANIFESTACAO_PROTOCOLO',
                    'type': 'textarea',
                    'label': 'Mensagem a ser enviada ao assistido via e-mail ao protocolar manifestação'
                },
                {
                    'name': 'WHATSAPP_PROCESSO_MANIFESTACAO_PROTOCOLO',
                    'type': 'textarea',
                    'label': 'Mensagem a ser enviada ao assistido via whatsapp ao protocolar manifestação'
                },
            ],
            'tasks': [
                {
                    'name': 'Processos - Verificar Processos',
                    'description': 'Consulta ProcAPI para verificar quais processos precisam ser atualizados',
                    'task': 'processo.processo.tasks.procapi_verificar_processos',
                    'arguments': [],
                    'periodic_tasks': [],
                },
                {
                    'name': 'Processos - Atualizar Processos',
                    'description': 'Atualiza processos que foram marcados como desatualizados pela task "Processos - Verificar Processos"',  # noqa: E501
                    'task': 'processo.processo.tasks.procapi_atualizar_processos',
                    'arguments': [
                        {
                            'name': 'limite',
                            'type': 'number',
                            'label': 'Nº de registros'
                        }
                    ],
                    'periodic_tasks': [],
                },
                {
                    'name': 'Processos - Atualizar Manifestações',
                    'description': 'Consulta ProcAPI para verificar quais manifestações (petições) precisam ser atualizadas',  # noqa: E501
                    'task': 'processo.processo.tasks.procapi_atualizar_manifestacoes',
                    'arguments': [
                        {
                            'name': 'limite',
                            'type': 'number',
                            'label': 'Nº de registros'
                        }
                    ],
                    'periodic_tasks': [],
                },
                {
                    'name': 'Processos - Enviar Manifestações',
                    'description': 'Envia para ProcAPI as novas manifestações (petições) analisadas',
                    'task': 'processo.processo.tasks.procapi_enviar_manifestacoes',
                    'arguments': [
                        {
                            'name': 'limite',
                            'type': 'number',
                            'label': 'Nº de registros'
                        }
                    ],
                    'periodic_tasks': [],
                },
                {
                    'name': 'Processos - Atualizar Tipos das Fases Processuais',
                    'description': 'Atualiza tipo genérico das fases processuais (audiências, sentenças, júris, recursos)',  # noqa: E501
                    'task': 'processo.processo.tasks.eproc_set_fase_tipo',
                    'arguments': [],
                    'periodic_tasks': [],
                },
                {
                    'name': 'Processos - Corrige Data de Cadastro das Fases Processuais',
                    'description': 'Corrige data de cadastro das fases incluídas no mês corrente, mas que foram protocoladas no mês anterior, desde que o dia de hoje não ultrapasse a dia definido na configuração "DIA_LIMITE_CADASTRO_FASE"',  # noqa: E501
                    'task': 'processo.processo.tasks.eproc_corrige_data_cadastro',
                    'arguments': [],
                    'periodic_tasks': [],
                },
                {
                    'name': 'Processos - Cadastra processos e partes automaticamente a partir de avisos (intimações) do Procapi',  # noqa: E501
                    'description': 'O cadastro automático é realizado a partir das associações entre defensorias e varas criadas, sendo que somente serão cadastradas os processos e partes definidos (caso seja definida parte em que exista advogado particular o processo não será cadastrado)',  # noqa: E501
                    'task': 'processo.processo.tasks.procapi_cadastrar_processos_avisos',
                    'arguments': [],
                    'periodic_tasks': [],
                },
                {
                    'name': 'Processos - Envia e-mail com extrato de processos distribuídos',
                    'description': 'Envia e-mail para os defensores com o extrato dos processos distribuídos',
                    'task': 'defensor.tasks.enviar_email_extrato_processos_distribuidos',
                    'arguments': [],
                    'periodic_tasks': [],
                },
            ],
        },
        {
            'name': 'SOLAR > Honorários',
            'description': 'Configurações do módulo Honorários',
            'internal': True,
            'arguments': [
                {
                    'name': 'HONORARIO_VINCULAR_AO_TITULAR_DO_SETOR',
                    'type': 'bool',
                    'label': 'True: vincula honorário ao titular do setor de honorários; False: vincula ao defensor que cadastrou a sentença'  # noqa: E501
                },
            ],
        },
        {
            'name': 'SOLAR > Eventos',
            'description': 'Configurações do módulo Eventos',
            'internal': True,
            'arguments': [
                {
                    'name': 'AREA_NO_CADASTRO_ATIVIDADE_EXTRAORDINARIA',
                    'type': 'bool',
                    'label': 'Insere/Remove o campo Área do cadastro de atividades extraordinárias'  # noqa: E501
                },
            ],
        },
        {
            'name': 'SOLAR > Procedimentos',
            'description': 'Configurações do módulo Procedimentos/Propac',
            'internal': True,
            'arguments': [
                {
                    'name': 'AREA_NO_CADASTRO_PROCEDIMENTOS',
                    'type': 'bool',
                    'label': 'Insere/Remove o campo Área do cadastro de procedimentos/propacs'  # noqa: E501
                },
            ],
        },
        {
            'name': 'SOLAR > Livre',
            'description': 'Configurações do módulo Livre',
            'internal': True,
            'arguments': [
                {
                    'name': 'ATIVAR_LIVRE_API',
                    'type': 'bool',
                    'label': 'Ativa/Desativa consulta na API do Livre (SEEU)'
                },
                {
                    'name': 'LIVRE_API_URL',
                    'type': 'text',
                    'label': 'URL da API do Livre (SEEU)'
                },
                {
                    'name': 'SHOW_PAINEL_LIVRE',
                    'type': 'bool',
                    'label': 'Mostrar novo painel do LIVRE'
                },
                {
                    'name': 'ID_PERGUNTA_FORMULARIO_INSPECAO_LIVRE',
                    'type': 'number',
                    'label': 'ID da Pergunta o Formulário de Inspeção que contém o nome do Estabelecimento Penal'
                }
            ],
        },
        {
            'name': 'GED',
            'description': 'Configurações do Gestor de Documentos (GED)',
            'active': False,
            'active_argument': 'SHOW_DJDOCUMENTS',
            'arguments': [
                {
                    'name': 'SHOW_DJDOCUMENTS',
                    'type': 'bool',
                    'label': 'Ativa/Desativa djdocuments (somente remove as URL nos templates)'
                },
                {
                    'name': 'SUPER_USER_CAN_EDIT_DOCUMENT',
                    'type': 'bool',
                    'label': 'Ativa/Desativa A possibilidade de um superusuario editar um documento em djdocuments'
                },
                {
                    'name': 'SUPER_USER_CAN_EXCLUDE_DOCUMENT',
                    'type': 'bool',
                    'label': 'Ativa/Desativa A possibilidade de um superusuario excluir um documento em djdocuments'
                },
                {
                    'name': 'GED_PODE_INCLUIR_IMAGENS_EXTERNAS',
                    'type': 'bool',
                    'label': 'Permite incluir imagens externas. Se habilitado, as imagens externas serão baixadas ao liberar documento para assinatura.'  # noqa: E501
                },
                {
                    'name': 'GED_PODE_BAIXAR_DOCUMENTO_NAO_ASSINADO',
                    'type': 'bool',
                    'label': 'Permite baixar documentos do GED sem a necessidade da assinatura'
                },
                {
                    'name': 'BLOQUEAR_TELA_AO_CRIAR_EDITAR_GED',
                    'type': 'bool',
                    'label': 'Bloqueia a tela de documentos / atendimento ao criar ou editar um GED (caso false, GED será aberto em nova aba)'  # noqa: E501
                },
                {
                    'name': 'DATA_UPLOAD_MAX_MEMORY_SIZE',
                    'type': 'number',
                    'label': 'Tamanho máximo de uploads no GED (Padrão do Django 2.5 MB)'
                },
                {
                    'name': 'GED_EXIBIR_FORMULAS_MODELO',
                    'type': 'bool',
                    'label': 'Exibir fórmulas GED ao editar modelo de documento'
                },
            ],
        },
        {
            'name': 'ProcAPI',
            'description': 'API Rest para o acesso ao webservice do MNI',
            'active': False,
            'active_argument': 'ATIVAR_PROCAPI',
            'arguments': [
                {
                    'name': 'ATIVAR_PROCAPI',
                    'type': 'bool',
                    'label': 'Ativa/Desativa consulta na API de processos'
                },
                {
                    'name': 'ATIVAR_ESAJ',
                    'type': 'bool',
                    'label': 'Ativa/Desativa modificações para utilização do eSAJ'
                },
                {
                    'name': 'PROCAPI_ATIVAR_INFORMAR_PERFIL_PROJUDI',
                    'type': 'bool',
                    'label': 'Habilita opção informar nome de usuário do Projudi na edição de perfil de usuário'
                },
                {
                    'name': 'PROCAPI_ASSUNTO_CAMPO_EXIBICAO',
                    'type': 'select',
                    'label': 'Campo usado para exibição dos assuntos no peticionamento inicial',
                    'options': {
                        'nome': 'Nome',
                        'descricao': 'Descrição',
                    },
                },
                {
                    'name': 'PROCAPI_URL',
                    'type': 'text',
                    'label': 'URL'
                },
            ],
        },
        {
            'name': 'Chronus',
            'description': 'Gerar relatórios via JasperServer',
            'active': False,
            'active_argument': 'CHRONUS_URL',
            'arguments': [
                {
                    'name': 'CHRONUS_URL',
                    'type': 'text',
                    'label': 'URL'
                },
                {
                    'name': 'CHRONUS_PODE_GERAR_XLSX_SEM_PAGINACAO',
                    'type': 'bool',
                    'label': 'Pode gerar XLSX sem paginação?'
                },
            ],
        },
        {
            'name': 'Metabase',
            'description': 'Visualizar Dashboards (Painéis) do Metabase',
            'active': False,
            'active_argument': 'METABASE_SITE_URL',
            'arguments': [

                {
                    'name': 'METABASE_SITE_URL',
                    'type': 'text',
                    'label': 'URL do Metabase'
                },
                {
                    'name': 'METABASE_SECRET_KEY',
                    'type': 'text',
                    'label': 'Chave Secreta do Metabase'
                },
                {
                    'name': 'METABASE_EXPIRATION_IN_MINUTES',
                    'type': 'number',
                    'label': 'Tempo de expiração dos links gerados pelo Metabase (em minutos)'
                },
                {
                    'name': 'METABASE_DISPLAY_IN_IFRAME',
                    'type': 'bool',
                    'label': 'Ativa/Desativa exibição embutida no SOLAR. Se desativado exibe em uma nova aba'
                },
            ],
        },
        {
            'name': 'Luna Chatbot',
            'description': 'Notificar assistido via Luna Chatbot',
            'active': False,
            'active_argument': 'USAR_NOTIFICACOES_ASSISTIDO_VIA_CHATBOT',
            'arguments': [
                {
                    'name': 'USAR_NOTIFICACOES_ASSISTIDO_VIA_CHATBOT',
                    'type': 'bool',
                    'label': 'Ativa/Desativa utilização de notificações via Luna Chatbot'
                },
                {
                    'name': 'CHATBOT_LUNA_API_TOKEN',
                    'type': 'text',
                    'label': 'Token'
                },
                {
                    'name': 'CHATBOT_LUNA_WEBHOOK_URL',
                    'type': 'text',
                    'label': 'Webhook URL'
                },
                {
                    'name': 'LUNA_MENSAGEM_AGENDAMENTO_INICIAL',
                    'type': 'textarea',
                    'label': 'Mensagem a ser enviada ao assistido via Luna ao realizar agendamento inicial'
                },
                {
                    'name': 'LUNA_MENSAGEM_AGENDAMENTO_RETORNO',
                    'type': 'textarea',
                    'label': 'Mensagem a ser enviada ao assistido via Luna ao realizar agendamento de retorno'
                },
                {
                    'name': 'LUNA_MENSAGEM_AGENDAMENTO_REMARCACAO',
                    'type': 'textarea',
                    'label': 'Mensagem a ser enviada ao assistido via Luna ao remarcar agendamento'
                },
                {
                    'name': 'LUNA_MENSAGEM_AGENDAMENTO_EXCLUSAO',
                    'type': 'textarea',
                    'label': 'Mensagem a ser enviada ao assistido via Luna ao excluir agendamento'
                },
                {
                    'name': 'LUNA_MENSAGEM_ANOTACAO',
                    'type': 'textarea',
                    'label': 'Mensagem a ser enviada ao assistido via Luna ao fazer uma anotação'
                },
                {
                    'name': 'LUNA_MENSAGEM_DOCUMENTO_PENDENTE',
                    'type': 'textarea',
                    'label': 'Mensagem a ser enviada ao assistido via Luna ao registrar um documento pendente'
                },
                {
                    'name': 'LUNA_MENSAGEM_ENCAMINHAMENTO_EXTERNO',
                    'type': 'textarea',
                    'label': 'Mensagem a ser enviada ao assistido via Luna ao encaminhar p/ órgão externo'
                },
            ],
        },
        {
            'name': 'e-Defensor',
            'description': 'Habilitar chat com app e-Defensor (DPE-RR)',
            'active': False,
            'active_argument': 'USAR_EDEFENSOR',
            'arguments': [
                {
                    'name': 'USAR_EDEFENSOR',
                    'type': 'bool',
                    'label': 'Usar chat do e-Defensor?'
                },
                {
                    'name': 'EDEFENSOR_CATEGORIA_AGENDA_ID',
                    'type': 'number',
                    'label': 'ID da Categoria de Agenda usada pelo e-Defensor'
                },
                {
                    'name': 'EDEFENSOR_CHAT_WEBSERVICE_TOKEN_URL',
                    'type': 'text',
                    'label': 'URL de obtenção do token do webservice e-Defensor'
                },
                {
                    'name': 'EDEFENSOR_CHAT_WEBSERVICE_TOKEN_USERNAME',
                    'type': 'text',
                    'label': 'Usuário de obtenção do token do webservice e-Defensor'
                },
                {
                    'name': 'EDEFENSOR_CHAT_WEBSERVICE_TOKEN_PASSWORD',
                    'type': 'text',
                    'label': 'Senha de obtenção do token do webservice e-Defensor'
                },
                {
                    'name': 'EDEFENSOR_CHAT_WEBSERVICE_APP_SYSTEM',
                    'type': 'text',
                    'label': 'Chave de middleware do webservice e-Defensor'
                },
            ],
        },
        {
            'name': 'Movile SMS',
            'description': 'Notificar assistido via Movile SMS',
            'active': False,
            'active_argument': 'USAR_SMS',
            'arguments': [
                {
                    'name': 'USAR_SMS',
                    'type': 'bool',
                    'label': 'Usar o envio de SMS'
                },
                {
                    'name': 'SERVICO_SMS_DISPONIVEL',
                    'type': 'bool',
                    'label': 'Habilitar o serviço de envio de SMS'
                },
                {
                    'name': 'MOVILE_API_URL',
                    'type': 'text',
                    'label': 'URL'
                },
                {
                    'name': 'MOVILE_AUTH_TOKEN',
                    'type': 'text',
                    'label': 'TOKEN'
                },
                {
                    'name': 'MOVILE_AUTH_USER',
                    'type': 'text',
                    'label': 'USER'
                },
                {
                    'name': 'FACILITA_SMS_AUTH',
                    'type': 'bool',
                    'label': 'Habilitar o serviço de envio de SMS por meio da plataforma Facilita Móvel'
                },
                {
                    'name': 'FACILITA_SMS_API_URL',
                    'type': 'text',
                    'label': 'URL'
                },
                {
                    'name': 'FACILITA_SMS_AUTH_USER',
                    'type': 'text',
                    'label': 'USER'
                },
                {
                    'name': 'FACILITA_SMS_AUTH_TOKEN',
                    'type': 'text',
                    'label': 'TOKEN'
                },
                {
                    'name': 'MENSAGEM_SMS_AGENDAMENTO_INICIAL',
                    'type': 'textarea',
                    'label': 'Mensagem de SMS a ser enviada ao assistido ao realizar agendamento inicial'
                },
                {
                    'name': 'MENSAGEM_SMS_AGENDAMENTO_RETORNO',
                    'type': 'textarea',
                    'label': 'Mensagem de SMS a ser enviada ao assistido ao realizar agendamento de retorno'
                },
                {
                    'name': 'MENSAGEM_SMS_AGENDAMENTO_REMARCACAO',
                    'type': 'textarea',
                    'label': 'Mensagem de SMS a ser enviada ao assistido ao realizar remarcação de agendamento'
                },
                {
                    'name': 'MENSAGEM_SMS_AGENDAMENTO_EXCLUSAO',
                    'type': 'textarea',
                    'label': 'Mensagem de SMS a ser enviada ao assistido ao excluir agendamento'
                },
                {
                    'name': 'MENSAGEM_SMS_ANOTACAO',
                    'type': 'textarea',
                    'label': 'Mensagem de SMS a ser enviada ao assistido ao fazer uma anotação de qualificação SMS'
                },
                {
                    'name': 'SMS_REMOVER_ACENTOS',
                    'type': 'bool',
                    'label': 'Remover os acentos dos textos ao digitar SMS enquanto a qualificação for SMS'
                },
            ],
        },
        {
            'name': 'Notificação Email',
            'description': 'Notificar assistido via serviço de Email SMTP',
            'active': False,
            'active_argument': 'USAR_EMAIL',
            'arguments': [
                {
                    'name': 'USAR_EMAIL',
                    'type': 'bool',
                    'label': 'Usar email para envio de agendamento, retorno, encaminhamento.'
                },
                {
                    'name': 'ASSUNTO_EMAIL_NOTIFICACAO',
                    'type': 'text',
                    'label': 'Assunto dos email de notificação'
                },
                {
                    'name': 'MENSAGEM_EMAIL_AGENDAMENTO_INICIAL',
                    'type': 'textarea',
                    'label': 'Mensagem de Email a ser enviada ao assistido ao realizar agendamento inicial'
                },
                {
                    'name': 'MENSAGEM_EMAIL_AGENDAMENTO_RETORNO',
                    'type': 'textarea',
                    'label': 'Mensagem de Email a ser enviada ao assistido ao realizar agendamento de retorno'
                },
                {
                    'name': 'MENSAGEM_EMAIL_AGENDAMENTO_REMARCACAO',
                    'type': 'textarea',
                    'label': 'Mensagem de Email a ser enviada ao assistido ao realizar remarcação de agendamento'
                },
                {
                    'name': 'MENSAGEM_EMAIL_AGENDAMENTO_EXCLUSAO',
                    'type': 'textarea',
                    'label': 'Mensagem de Email a ser enviada ao assistido ao excluir agendamento'
                },
            ],
        },
        {
            'name': 'Athenas',
            'description': 'Validar cadastro de novo usuário no Athenas',
            'active': False,
            'active_argument': 'USAR_API_ATHENAS',
            'arguments': [
                {
                    'name': 'USAR_API_ATHENAS',
                    'type': 'bool',
                    'label': 'Ativa/Desativa a consulta a API do ATHENAS no momento de cadastro de novos usuario'
                },
                {
                    'name': 'ATHENAS_API_URL',
                    'type': 'text',
                    'label': 'URL'
                },
            ],
        },
        {
            'name': 'LDAP',
            'description': 'Validar cadastro de novo usuário no LDAP',
            'active': False,
            'active_argument': 'USAR_API_LDAP',
            'arguments': [
                {
                    'name': 'USAR_API_LDAP',
                    'type': 'bool',
                    'label': 'Ativa/Desativa a consulta a API ao LDAP (Active Directory) no momento de cadastro de novos usuario'  # noqa: E501
                },
                {
                    'name': 'LDAP_AUTH_SERVER_URI',
                    'type': 'text',
                    'label': 'SERVER URI'
                },
                {
                    'name': 'LDAP_AUTH_BIND_DN',
                    'type': 'text',
                    'label': 'BIND DN'
                },
                {
                    'name': 'LDAP_AUTH_BIND_PASSWORD',
                    'type': 'text',
                    'label': 'BIND PASSWORD'
                },
                {
                    'name': 'LDAP_AUTH_BIND_SUFFIX',
                    'type': 'text',
                    'label': 'BIND SUFFIX'
                },
            ],
        },
        {
            'name': 'Égide',
            'description': 'Autenticar usuários com Égide',
            'active': False,
            'active_argument': 'USAR_API_EGIDE_AUTH',
            'arguments': [
                {
                    'name': 'USAR_API_EGIDE_AUTH',
                    'type': 'bool',
                    'label': 'URL'
                },
                {
                    'name': 'EGIDE_URL_ALTERAR_SENHA',
                    'type': 'text',
                    'label': 'Link para redirecionamento quando usuário tentar alterar a senha pelo SOLAR'
                },
                {
                    'name': 'EGIDE_URL',
                    'type': 'text',
                    'label': 'URL'
                },
                {
                    'name': 'EGIDE_REDIRECT_URI',
                    'type': 'text',
                    'label': 'Redirect URI'
                },
                {
                    'name': 'EGIDE_CLIENT_ID',
                    'type': 'text',
                    'label': 'Client ID'
                },
                {
                    'name': 'EGIDE_CLIENT_SECRET',
                    'type': 'text',
                    'label': 'Client Secret'
                },
                {
                    'name': 'EGIDE_MENSAGEM_USUARIO_NAO_CADASTRADO',
                    'type': 'textarea',
                    'label': 'Mensagem exibida quando um usuário do ÉGIDE não está cadastrado no SOLAR'
                },
            ],
        },
        {
            'name': 'Signo',
            'description': 'Notificações assíncronas com Signo',
            'active': False,
            'active_argument': 'USAR_NOTIFICACOES_SIGNO',
            'arguments': [
                {
                    'name': 'USAR_NOTIFICACOES_SIGNO',
                    'type': 'bool',
                    'label': 'Ativa/Desativa utilização do SIGNO para notificações no sistema'
                },
                {
                    'name': 'SIGNO_REST_API_URL',
                    'type': 'text',
                    'label': 'URL'
                },
                {
                    'name': 'SIGNO_WEBSOCKET_URL',
                    'type': 'text',
                    'label': 'Websocket URL'
                },
                {
                    'name': 'NOTIFICAR_ALTERACAO_CADASTRO_ASSISTIDO',
                    'type': 'bool',
                    'label': 'Ativa/Desativa notificação do sistema ao alterar cadastro do assistido'
                },
                {
                    'name': 'NOTIFICAR_LIBERACAO_ATENDIMENTO_RECEPCAO',
                    'type': 'bool',
                    'label': 'Ativa/Desativa notificação do sistema ao liberar atendimento pela recepção'
                },
                {
                    'name': 'NOTIFICAR_DOCUMENTO_PRONTO_PARA_ASSINAR',
                    'type': 'bool',
                    'label': 'Ativa/Desativa notificação do sistema quando documento for marcado como pronto para assinar'  # noqa: E501
                },
                {
                    'name': 'NOTIFICAR_DOCUMENTO_FINALIZADO',
                    'type': 'bool',
                    'label': 'Ativa/Desativa notificação do sistema quando documento for marcado como finalizado'
                },
                {
                    'name': 'NOTIFICAR_DOCUMENTO_ASSINATURA_PENDENTE',
                    'type': 'bool',
                    'label': 'Ativa/Desativa notificação do sistema ao adicionar nova pendência de assinatura'
                },
                {
                    'name': 'NOTIFICAR_MANIFESTACAO_EM_ANALISE',
                    'type': 'bool',
                    'label': 'Ativa/Desativa notificação do sistema ao ser criado uma petição para analise pelo módulo peticionamento'  # noqa: E501
                },
                {
                    'name': 'NOTIFICAR_MANIFESTACAO_PROTOCOLADA',
                    'type': 'bool',
                    'label': 'Ativa/Desativa notificação do sistema ao ser protocolado uma petição pelo módulo peticionamento'  # noqa: E501
                },
                {
                    'name': 'NOTIFICAR_PROCESSO_DE_INDEFERIMENTO',
                    'type': 'bool',
                    'label': 'Ativa/Desativa notificação do sistema ao ser tramitado um processo de indeferimento/impedimento/suspeição'  # noqa: E501
                },
            ],
        },
        {
            'name': 'Plantão',
            'description': 'API Rest para acesso aos plantões ativos',
            'active': False,
            'active_argument': 'PLANTAO_API_URL',
            'arguments': [
                {
                    'name': 'PLANTAO_API_URL',
                    'type': 'text',
                    'label': 'URL'
                },
            ],
            'tasks': [
                {
                    'name': 'Plantão - Criar lotação dos plantonistas',
                    'description': 'Cria automaticamente a lotação do defensor na defensoria de plantão a partir da consulta à API dos Plantões',  # noqa: E501
                    'task': 'defensor.tasks.verifica_plantao_api',
                    'arguments': [],
                    'periodic_tasks': [],
                },
                {
                    'name': 'Plantão - Atualizar movimentações processuais',
                    'description': 'Vincula fases processuais criadas durante o período de plantão ao plantão',
                    'task': 'processo.processo.tasks.eproc_set_fase_plantao',
                    'arguments': [
                        {
                            'name': 'dias',
                            'type': 'number',
                            'label': 'Dias'
                        }
                    ],
                    'periodic_tasks': [],
                },
            ],
        },
        {
            'name': 'Google Analytics',
            'description': 'Rastreio de tráfego de acesso do sistema',
            'active': False,
            'active_argument': 'GOOGLE_ANALYTICS_ID',
            'arguments': [
                {
                    'name': 'GOOGLE_ANALYTICS_ID',
                    'type': 'text',
                    'label': 'URL do Universal Analytics (UA)'
                },
                {
                    'name': 'GOOGLE_ANALYTICS_4_ID',
                    'type': 'text',
                    'label': 'URL do Google Analytics 4 (GA4)'
                },
            ],
        },
        {
            'name': 'Sentry',
            'description': 'Monitorar erros do sistema',
            'active': False,
            'active_argument': 'SENTRY_DSN',
            'arguments': [
                {
                    'name': 'SENTRY_DSN',
                    'type': 'text',
                    'label': 'DSN do Sentry'
                },
                {
                    'name': 'SENTRY_TRACES_SAMPLE_RATE',
                    'type': 'text',
                    'label': 'Taxa de Amostragem (Ex: 0.5 rastreia 50% dos erros)'
                },
            ],
        },
        {
            'name': 'Calculadora Jurídica',
            'description': 'Calculadora Jurídica',
            'internal': True,
            'arguments': [
                {
                    'name': 'ATIVAR_CALCULADORA',
                    'type': 'bool',
                    'label': 'Ativar calculadora jurídica na defensoria'
                },
                {
                    'name': 'URL_CARTILHA_EXEC_PENAL',
                    'type': 'text',
                    'label': 'URL para cartilha de execução penal utilizado na calculadora'
                },
            ],
        },
    ]

    # Carrega configurações originárias do .env
    for service in services:
        for argument in service['arguments']:
            if hasattr(settings, argument['name']):
                argument['value'] = getattr(settings, argument['name'])
        if 'tasks' not in service:
            service['tasks'] = []
        for task in service['tasks']:
            task['enabled'] = False

    return render(request=request, template_name="perfil/perfil_admin.html", context={
        'angular': 'PerfilAdminCtrl',
        'services': services
    })


@login_required
def get_config_situacoes_sigilosas(request):
    resposta = {'success': True, 'errors': {}, 'sigiloso': True if config.SITUACOES_SIGILOSAS else False, 'situacoes': config.SITUACOES_SIGILOSAS}  # noqa: E501
    return JsonResponse(resposta)


@login_required
def perfil_comarcas(request):

    procapi_versao_compativel = True
    if config.ATIVAR_PROCAPI:
        from procapi_client.services import APIConfig
        procapi_versao_compativel = APIConfig().versao_compativel()

    return render(request=request, template_name="perfil/perfil_comarcas.html", context={
        'procapi_versao_min': settings.PROCAPI_VERSAO_MIN,
        'procapi_versao_compativel': procapi_versao_compativel,
        'angular': 'PerfilComarcasCtrl'
    })
