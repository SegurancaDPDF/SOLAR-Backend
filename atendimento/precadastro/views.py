# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
import json
import logging
import smtplib
from datetime import datetime, time

# Bibliotecas de terceiros
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q, Case, When, Value, IntegerField
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView
from django.views.generic.edit import UpdateView
from django.urls import reverse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Solar
from django.views.decorators.cache import never_cache
from assistido.models import PessoaAssistida
from atendimento.agendamento.utils import formata_mensagem_whatsapp_procedimentos_efetuados
from atendimento.atendimento.models import Pessoa as AtendimentoPessoa
from atendimento.atendimento.models import (
    Atendimento,
    Cronometro,
    Defensor as AtendimentoDefensor,
    Procedimento,
    Reclamacao
)
from constance import config
from contrib import constantes
from contrib.models import Dados, Defensoria, Deficiencia, Estado, Util, Endereco, Bairro
from defensor.models import Atuacao
from processo.processo.models import Processo
from relatorios.models import Local, Relatorio
from evento.models import Categoria

# Modulos locais
from .forms import EnderecoForm, PainelForm


logger = logging.getLogger(__name__)


@never_cache
@login_required
@permission_required('atendimento.view_atendimento')
def atendimento(request, ligacao_numero):
    request.session['atendimento_processo_id'] = None

    try:
        ligacao = Atendimento.objects.get(numero=ligacao_numero)
    except ObjectDoesNotExist:
        return redirect('precadastro_index')

    if ligacao.requerente:

        assistido = ligacao.requerente.pessoa

        # ATENDIMENTOS EXCLUIDOS
        atendimentos_excluidos = AtendimentoPessoa.objects.filter(
            pessoa=assistido,
            tipo=AtendimentoPessoa.TIPO_REQUERENTE,
            ativo=True,
            atendimento__tipo__in=[Atendimento.TIPO_INICIAL, Atendimento.TIPO_VISITA],
            atendimento__inicial=None,
            atendimento__remarcado=None,
            atendimento__ativo=False,
            atendimento__partes__ativo=True,
            atendimento__partes__responsavel=True
        ).values(
            'atendimento__numero',
            'atendimento__data_agendamento',
            'atendimento__data_atendimento',
            'atendimento__data_exclusao',
            'atendimento__motivo_exclusao',
            'atendimento__excluido_por__nome',
            'atendimento__partes__tipo',
            'atendimento__partes__pessoa__nome',
            'atendimento__partes__pessoa__email',
            'atendimento__defensor__defensor__servidor__nome',
            'atendimento__defensor__defensoria__nome',
            'atendimento__defensor__nucleo__nome',
            'atendimento__qualificacao__titulo',
            'atendimento__qualificacao__area__nome',
        ).order_by(
            '-atendimento__data_atendimento', 'atendimento__data_agendamento', 'atendimento__numero'
        )

        atendimentos = []
        for parte in atendimentos_excluidos:

            if not atendimentos or parte['atendimento__numero'] != atendimentos[-1]['numero']:
                atendimentos.append({
                    'numero': parte['atendimento__numero'],
                    'data_agendamento': parte['atendimento__data_agendamento'],
                    'data_atendimento': parte['atendimento__data_atendimento'],
                    'data_exclusao': parte['atendimento__data_exclusao'],
                    'motivo_exclusao': parte['atendimento__motivo_exclusao'],
                    'excluido_por': parte['atendimento__excluido_por__nome'],
                    'defensor': parte['atendimento__defensor__defensor__servidor__nome'],
                    'defensoria': parte['atendimento__defensor__defensoria__nome'],
                    'nucleo': parte['atendimento__defensor__nucleo__nome'],
                    'qualificacao': parte['atendimento__qualificacao__titulo'],
                    'area': parte['atendimento__qualificacao__area__nome'],
                    'requerente_email': None,
                    'requerente': None,
                    'requerido': None
                })

            if parte['atendimento__partes__tipo'] == 0:
                atendimentos[-1]['requerente'] = parte['atendimento__partes__pessoa__nome']
                atendimentos[-1]['requerente_email'] = parte['atendimento__partes__pessoa__email']
            else:
                atendimentos[-1]['requerido'] = parte['atendimento__partes__pessoa__nome']

        atendimentos_excluidos = atendimentos

        # ATENDIMENTOS COMO REQUERENTE
        atendimentos_requerente = AtendimentoPessoa.objects.filter(
            pessoa=assistido,
            tipo=AtendimentoPessoa.TIPO_REQUERENTE,
            ativo=True,
            atendimento__tipo__in=[Atendimento.TIPO_INICIAL, Atendimento.TIPO_VISITA],
            atendimento__inicial=None,
            atendimento__remarcado=None,
            atendimento__ativo=True,
            atendimento__partes__ativo=True,
            atendimento__partes__responsavel=True
        ).values(
            'atendimento__numero',
            'atendimento__data_agendamento',
            'atendimento__data_atendimento',
            'atendimento__partes__tipo',
            'atendimento__partes__pessoa__nome',
            'atendimento__partes__pessoa__email',
            'atendimento__defensor__defensor__servidor__nome',
            'atendimento__defensor__defensoria__nome',
            'atendimento__defensor__nucleo__nome',
            'atendimento__qualificacao__titulo',
            'atendimento__qualificacao__area__nome',
        ).order_by(
            '-atendimento__data_atendimento', 'atendimento__data_agendamento', 'atendimento__numero'
        )

        atendimentos = []
        for parte in atendimentos_requerente:

            if not atendimentos or parte['atendimento__numero'] != atendimentos[-1]['numero']:
                atendimentos.append({
                    'numero': parte['atendimento__numero'],
                    'data_agendamento': parte['atendimento__data_agendamento'],
                    'data_atendimento': parte['atendimento__data_atendimento'],
                    'defensor': parte['atendimento__defensor__defensor__servidor__nome'],
                    'defensoria': parte['atendimento__defensor__defensoria__nome'],
                    'nucleo': parte['atendimento__defensor__nucleo__nome'],
                    'qualificacao': parte['atendimento__qualificacao__titulo'],
                    'area': parte['atendimento__qualificacao__area__nome'],
                    'requerente': None,
                    'requerente_email': None,
                    'requerido': None
                })

            if parte['atendimento__partes__tipo'] == 0:
                atendimentos[-1]['requerente'] = parte['atendimento__partes__pessoa__nome']
                atendimentos[-1]['requerente_email'] = parte['atendimento__partes__pessoa__email']
            else:
                atendimentos[-1]['requerido'] = parte['atendimento__partes__pessoa__nome']

        atendimentos_como_requerente = atendimentos

        # ATENDIMENTOS COMO REQUERIDO
        atendimentos_requerido = AtendimentoPessoa.objects.filter(
            pessoa=assistido,
            tipo=AtendimentoPessoa.TIPO_REQUERIDO,
            ativo=True,
            atendimento__tipo__in=[Atendimento.TIPO_INICIAL, Atendimento.TIPO_VISITA],
            atendimento__inicial=None,
            atendimento__remarcado=None,
            atendimento__ativo=True,
            atendimento__partes__ativo=True,
            atendimento__partes__responsavel=True
        ).values(
            'atendimento__numero',
            'atendimento__data_agendamento',
            'atendimento__data_atendimento',
            'atendimento__partes__tipo',
            'atendimento__partes__pessoa__nome',
            'atendimento__partes__pessoa__email',
            'atendimento__defensor__defensor__servidor__nome',
            'atendimento__defensor__defensoria__nome',
            'atendimento__defensor__nucleo__nome',
            'atendimento__qualificacao__titulo',
            'atendimento__qualificacao__area__nome',
        ).order_by(
            '-atendimento__data_atendimento', 'atendimento__data_agendamento', 'atendimento__numero'
        )

        atendimentos = []
        for parte in atendimentos_requerido:

            if not atendimentos or parte['atendimento__numero'] != atendimentos[-1]['numero']:
                atendimentos.append({
                    'numero': parte['atendimento__numero'],
                    'data_agendamento': parte['atendimento__data_agendamento'],
                    'data_atendimento': parte['atendimento__data_atendimento'],
                    'defensor': parte['atendimento__defensor__defensor__servidor__nome'],
                    'defensoria': parte['atendimento__defensor__defensoria__nome'],
                    'nucleo': parte['atendimento__defensor__nucleo__nome'],
                    'qualificacao': parte['atendimento__qualificacao__titulo'],
                    'area': parte['atendimento__qualificacao__area__nome'],
                    'requerente': None,
                    'requerente_email': None,
                    'requerido': None
                })

            if parte['atendimento__partes__tipo'] == 0:
                atendimentos[-1]['requerente'] = parte['atendimento__partes__pessoa__nome']
                atendimentos[-1]['requerente_email'] = parte['atendimento__partes__pessoa__email']
            else:
                atendimentos[-1]['requerido'] = parte['atendimento__partes__pessoa__nome']

        atendimentos_como_requerido = atendimentos

        # PROCESSOS
        atendimentos_processo = AtendimentoPessoa.objects.filter(
            pessoa=assistido,
            tipo=AtendimentoPessoa.TIPO_REQUERENTE,
            ativo=True,
            atendimento__tipo=Atendimento.TIPO_PROCESSO,
            atendimento__inicial=None,
            atendimento__remarcado=None,
            atendimento__ativo=True,
            atendimento__partes__ativo=True,
            atendimento__partes__responsavel=True,
            atendimento__defensor__parte__ativo=True,
            atendimento__defensor__parte__processo__ativo=True,
        ).values(
            'atendimento__numero',
            'atendimento__data_agendamento',
            'atendimento__data_atendimento',
            'atendimento__partes__tipo',
            'atendimento__partes__pessoa__nome',
            'atendimento__partes__pessoa__email',
            'atendimento__defensor__parte__parte',
            'atendimento__defensor__parte__data_cadastro',
            'atendimento__defensor__parte__processo__tipo',
            'atendimento__defensor__parte__processo__numero',
            'atendimento__defensor__parte__processo__acao__nome',
            'atendimento__defensor__parte__processo__vara__nome',
            'atendimento__defensor__parte__processo__area__nome',
        )

        atendimentos = []
        for parte in atendimentos_processo:

            if not atendimentos or parte['atendimento__numero'] != atendimentos[-1]['numero']:
                atendimentos.append({
                    'numero': parte['atendimento__numero'],
                    'processo': parte['atendimento__defensor__parte__processo__numero'],
                    'processo_parte': parte['atendimento__defensor__parte__parte'],
                    'processo_acao': parte['atendimento__defensor__parte__processo__acao__nome'],
                    'processo_vara': parte['atendimento__defensor__parte__processo__vara__nome'],
                    'processo_area': parte['atendimento__defensor__parte__processo__area__nome'],
                    'processo_tipo': Processo.LISTA_TIPO[parte['atendimento__defensor__parte__processo__tipo']][1],
                    'processo_data_cadastro': parte['atendimento__defensor__parte__data_cadastro'],
                    'requerente': None,
                    'requerente_email': None,
                    'requerido': None
                })

            if parte['atendimento__partes__tipo'] == 0:
                atendimentos[-1]['requerente'] = parte['atendimento__partes__pessoa__nome']
                atendimentos[-1]['requerente_email'] = parte['atendimento__partes__pessoa__email']
            else:
                atendimentos[-1]['requerido'] = parte['atendimento__partes__pessoa__nome']

        atendimentos_processo = atendimentos

        if not atendimentos_como_requerente and not atendimentos_como_requerido and not atendimentos_processo:
            return redirect('qualificacao_index', ligacao_numero)
        else:
            angular = 'AtendimentosPessoaCtrl'
            return render(request=request, template_name="atendimento/precadastro/atendimentos.html", context=locals())

    return redirect('precadastro_continuar', ligacao_numero)


@never_cache
@login_required
@permission_required('atendimento.add_atendimento')
def continuar(request, ligacao_numero):
    if request.session.get('ligacao_id') is None:
        return redirect('precadastro_index')

    try:

        ligacao = Atendimento.objects.get(id=request.session.get('ligacao_id'))

        if ligacao.cronometro.expirado():
            return encerrar(request, ligacao.numero, Cronometro.MOTIVO_TEMPO_EXPIRADO)

    except Exception as e:
        erro = 'Erro ao continuar ligação %s \n %s ' % (ligacao_numero, e)
        logger.error(erro)

        return redirect('precadastro_iniciar')

    if ligacao.requerente is None:
        return redirect('precadastro_iniciar')

    pessoa = ligacao.requerente.pessoa

    # cria arrays para CheckboxList (requerido para AngularJS)
    deficiencias = Deficiencia.objects.all()

    endereco_form_initial = {
        'estado': Estado.objects.get(uf__iexact=settings.SIGLA_UF)
    }

    # forms
    if pessoa.endereco:
        endereco_form_initial = {
            'estado': pessoa.endereco.municipio.estado,
            'municipio': pessoa.endereco.municipio
        }

    endereco_form = EnderecoForm(initial=endereco_form_initial)

    # se parametro nao corresponde ao numero da ligacao, redireciona para link correto
    if int(ligacao.numero) != int(ligacao_numero):
        return redirect('precadastro_continuar', ligacao.numero)

    relatorios = Relatorio.objects.filter(
        papeis=request.user.servidor.papel,
        locais__pagina=Local.PAG_PRECADASTRO_INDEX
    ).ativos()

    angular = 'BuscarPessoaModel'

    # formata uma mensagem para whatsapp
    if ligacao.get_procedimentos().exists():
        fonezap = pessoa.telefone_para_whatsapp
        mensagem_whatsapp_com_documentos = formata_mensagem_whatsapp_procedimentos_efetuados(ligacao, True)
        mensagem_whatsapp_sem_documentos = formata_mensagem_whatsapp_procedimentos_efetuados(ligacao, False)
        ultimo_procedimento = ligacao.get_procedimentos().filter(
            tipo__in=[
                Procedimento.TIPO_AGENDAMENTO_INICIAL,
                Procedimento.TIPO_AGENDAMENTO_RETORNO,
                Procedimento.TIPO_REAGENDAMENTO]
            ).last()
        if ultimo_procedimento is not None:
            agendamento = ultimo_procedimento.agendamento

    return render(request=request, template_name="atendimento/precadastro/iniciar.html", context=locals())


@never_cache
@login_required
@permission_required('atendimento.add_atendimento')
def encerrar(request, ligacao_numero=None, motivo_finalizou_ligacao=0):

    if request.session.get('ligacao_id'):

        ligacao = Atendimento.objects.filter(id=request.session.get('ligacao_id')).first()

        if ligacao:
            ligacao.cronometro.finalizar(motivo_finalizou_ligacao)
            messages.success(request, u'Ligação finalizada')
        else:
            messages.error(request, u'Ligação já foi finalizada')

    else:

        messages.error(request, u'Ligação já foi finalizada')

    if 'ligacao_id' in request.session:
        del request.session['ligacao_id']

    if 'pessoa_id' in request.session:
        del request.session['pessoa_id']

    if request.GET.get('next'):
        return redirect(request.GET.get('next'))
    else:
        return redirect('precadastro_index')


@never_cache
@login_required
def enviar_lembrete_email(request):
    email = request.POST.get('email')
    ligacao_id = request.session.get('ligacao_id')
    numero = request.POST.get('numero')
    body_html = ''

    if ligacao_id:
        ligacao = Atendimento.objects.get(id=ligacao_id)
        # Fazer a mensagem
        if ligacao.get_procedimentos() and not numero:
            for procedimento in ligacao.get_procedimentos():
                if procedimento.tipo == procedimento.TIPO_ENCAMINHAMENTO:
                    body_html = '''
                        {0}<br>
                        <strong>{1}</strong>
                    '''.format(
                        config.LEMBRETE_129_EMAIL_ENCAMINHAMENTO,
                        str(procedimento.TIPO_ENCAMINHAMENTO)
                    )
                elif procedimento.tipo == procedimento.TIPO_INFORMACAO:
                    body_html = '''
                        {0}<br>
                        <strong>{1}</strong>
                    '''.format(
                        config.LEMBRETE_129_EMAIL_DUVIDAS,
                        str(procedimento.TIPO_INFORMACAO)
                    )
                elif procedimento.tipo == procedimento.TIPO_RECLAMACAO:
                    body_html = '''
                        <br>
                        <strong>Protocolo de reclamação: </strong> {0}
                        {1}<br>
                    '''.format(
                        str(procedimento.attprocedimento.numero),
                        config.LEMBRETE_129_EMAIL_RECLAMACAO,
                    )
                elif procedimento.tipo == procedimento.TIPO_INFORMACAO_ASSISTIDO:
                    body_html = '''
                        <br>
                        <strong>Protocolo de informação: </strong> {0}
                        {1}<br>
                    '''.format(
                        str(procedimento.attprocedimento.numero),
                        config.LEMBRETE_129_EMAIL_INFORMACAO,
                    )
                else:
                    body_html = '{0}{1}'.format(
                        procedimento.agendamento.text_mail(),
                        config.LEMBRETE_129_EMAIL_AGENDAMENTO
                    )
        else:
            # Agendamento Online
            atendimento = Atendimento.objects.get(numero=numero)
            body_html = '{}{}'.format(
                atendimento.text_mail(),
                config.LEMBRETE_EMAIL_AGENDAMENTO_ONLINE,
            )

    body_html = '''
        <html>
            <head></head>
            <body>{0}</body>
        </html>
    '''.format(body_html)

    # Enviar email aqui
    fromaddr = settings.EMAIL_DISK
    toaddr = email
    msg = MIMEMultipart()
    msg['Subject'] = "DISK 129 - DEFENSORIA PÚBLICA DO ESTADO DO AMAZONAS"
    msg['From'] = fromaddr
    msg['To'] = toaddr

    msg.attach(MIMEText(body_html, 'html'))
    server = smtplib.SMTP(settings.EMAIL_DISK_SMTP, settings.EMAIL_DISK_SMTP_PORT)

    if settings.EMAIL_USE_TLS:
        server.starttls()

    server.login(fromaddr, settings.EMAIL_DISK_PASSWORD)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    if config.ENVIAR_COPIA_EMAIL_DISK:
        server.sendmail(fromaddr, config.EMAIL_PARA_ENVIO_DE_COPIA_DISK, text)
    server.quit()
    return JsonResponse({'error': False})


@never_cache
@login_required
def enviar_reclamacao_email(request):
    if request.method == 'POST':
        if request.session.get('ligacao_id'):
            ligacao = Atendimento.objects.filter(id=request.session.get('ligacao_id')).first()
            ligacao_reclamacao = Atendimento.objects.create(origem=ligacao, tipo=Atendimento.TIPO_RECLAMACAO,
                                                            ativo=True)

            procedimento, msg = Procedimento.objects.get_or_create(ligacao_id=ligacao.id,
                                                                   atendente=request.user,
                                                                   tipo=Procedimento.TIPO_RECLAMACAO,
                                                                   attprocedimento=ligacao_reclamacao)
            procedimento.save()

            # Salvar dados da reclamação no banco

            request_body = json.loads(request.body)
            data = datetime.now()
            assistido = str(ligacao.get_requerentes()[0])
            atendente = str(request.user.servidor)
            reclamacao = request_body["reclamacaoDetalhes"]
            nome_estabelecimento = request_body["nomeDoEstabelecimento"]
            tipo_estabelecimento = int(request_body["tipoDoEstabelecimento"])

            reclamacao_atendimento, msg = Reclamacao.objects.get_or_create(data=data, assistido=assistido,
                                                                           atendente=atendente,
                                                                           reclamacao=reclamacao,
                                                                           nome_estabelecimento=nome_estabelecimento,
                                                                           tipo_estabelecimento=tipo_estabelecimento)

            logradouro = request_body['logradouroDenuncia']
            numero = str(request_body['numeroDenuncia'])
            complemento = request_body['complementoDenuncia'] if 'complementoDenuncia' in request_body else ''
            bairro_id = request_body['bairroId']
            municipio_id = request_body['municipioId']
            cep = request_body['cepDenuncia']

            endereco = Endereco.objects.create(logradouro=logradouro, numero=numero, complemento=complemento,
                                               cep=cep, bairro_id=bairro_id, municipio_id=municipio_id)
            reclamacao_atendimento.endereco_estabelecimento = endereco
            reclamacao_atendimento.save()

            from_address = settings.EMAIL_DISK
            to_addresses = settings.EMAIL_CORREGEDORIA
            msg = MIMEMultipart()
            msg['From'] = from_address
            msg['To'] = ",".join(to_address for to_address in to_addresses)
            msg['Subject'] = "DEFENSORIA PÚBLICA DO ESTADO DO AMAZONAS - ENCAMINHAMENTO DE RECLAMAÇÃO"
            body_html = """
                <h4 style="text-align: center;">INFORMAÇÕES DA DENÚNCIA</h4>
                <p style="text-align: justify;">Esta mensagem foi enviada por meio do canal de comunicação da Defensoria Pública do Estado do Amazonas, segue abaixo as informações do local que não está seguindo as recomendações propostas pelo Governo.</p>  # noqa: E501
                <p style="text-align: justify;"><strong>Nome do Estabelecimento:</strong> {}</p>
                <p style="text-align: justify;"><strong>Tipo do Estabelecimento:</strong> {}</p>
                <p style="text-align: justify;"><strong>Endereço do Estabelecimento:</strong> {}</p>
                <p style="text-align: justify;"><strong>Descrição da Denúncia:</strong> {}</p>
                <p style="text-align: justify;"><strong>Horário da Denúncia:</strong> {}</p>
                <p style="text-align: justify;">&nbsp;</p>
                <p style="text-align: center;">Este e um e-mail automático, não é necessário respondê-lo.</p>
                <p style="text-align: center;">Defensoria Pública do Estado do Amazonas</p>
            """.format(reclamacao_atendimento.nome_estabelecimento, reclamacao_atendimento.get_tipo_estabelecimento_display(),  # noqa: E501
                       reclamacao_atendimento.endereco_estabelecimento, reclamacao_atendimento.reclamacao, reclamacao_atendimento.data.strftime("%d/%m/%y %H:%M"))  # noqa: E501

            msg.attach(MIMEText(body_html, 'html'))
            server = smtplib.SMTP(settings.EMAIL_DISK_SMTP, settings.EMAIL_DISK_SMTP_PORT)

            if settings.EMAIL_USE_TLS:
                server.starttls()

            server.login(from_address, settings.EMAIL_DISK_PASSWORD)
            text = msg.as_string()
            server.sendmail(from_address, to_addresses, text)
            if config.ENVIAR_COPIA_EMAIL_DISK:
                server.sendmail(from_address, config.EMAIL_PARA_ENVIO_DE_COPIA_DISK, text)
            server.quit()
            messages.success(request, u'Email enviado com sucesso à corregedoria.')

            return redirect('precadastro_continuar', request.session.get('ligacao_id'))


@never_cache
@login_required
def get_pessoa(request):
    try:
        ligacao = Atendimento.objects.get(id=request.session.get('ligacao_id'))
        data = ligacao.requerente.pessoa.to_dict()
    except Exception:
        data = {'success': False}

    return JsonResponse(data)


@never_cache
@login_required
@permission_required('atendimento.add_atendimento')
def index(request):

    request.session['nucleo'] = None
    next = request.GET.get('next')

    if request.session.get('ligacao_id'):

        ligacao = Atendimento.objects.get(id=request.session.get('ligacao_id'))

        if ligacao.cronometro.expirado():
            return encerrar(request, ligacao.numero, Cronometro.MOTIVO_TEMPO_EXPIRADO)

    else:

        ligacao = None

    return render(request=request, template_name="atendimento/precadastro/index.html", context=locals())


@never_cache
@login_required
@permission_required('atendimento.add_atendimento')
def iniciar(request):
    if request.method == 'POST':

        data = Dados(request.body)

        q = Q(desativado_em=None)

        if data['cpf'] is not None and data['cpf'] != '':
            q &= Q(cpf=data['cpf'])

        elif data['id'] is not None and data['id'] != '':
            q &= Q(id=data['id'])

        else:

            # Busca por nome
            if data['nome'] is not None and data['nome'] != '':

                # Verifica se foi informado o mínimo de caracteres no filtro do nome
                if config.BUSCAR_ATENDIMENTOS_FILTRO_NOME_MIN_CARACTERES and len(data['nome']) < config.BUSCAR_ATENDIMENTOS_FILTRO_NOME_MIN_CARACTERES:  # noqa: E501
                    return JsonResponse({
                        'sucesso': False,
                        'mensagem': 'Erro: Aumente o texto para {} caracter(es) ou mais e tente novamente.'.format(
                            config.BUSCAR_ATENDIMENTOS_FILTRO_NOME_MIN_CARACTERES
                        )
                    })

                nomes = Util.text_to_soundex(data['nome'])
                q_nome = Q()

                for nome in nomes:
                    q_nome &= Q(nome_soundex__icontains=nome)

                # Só busca por nome social caso seja tipo pessoa física
                q_nome_social = Q(
                    Q(tipo=constantes.TIPO_PESSOA_FISICA) &
                    Q(nome_social__icontains=data['nome'])
                )

                # Só busca por nome fantasia (apelido) caso seja tipo pessoa jurídica
                q_nome_fantasia = Q(
                    Q(tipo=constantes.TIPO_PESSOA_JURIDICA) &
                    Q(apelido__icontains=data['nome'])
                )

                q &= Q(q_nome | q_nome_social | q_nome_fantasia)

            filiacao = data['filiacao'][0]

            if filiacao['nome'] is not None and filiacao['nome'] != '':
                nomes = Util.text_to_soundex(filiacao['nome'])
                for nome in nomes:
                    q &= Q(filiacoes__nome_soundex__icontains=nome)

            if data['data_nascimento'] is not None and data['data_nascimento'] != '':
                try:
                    data['data_nascimento'] = datetime.datetime.strptime(data['data_nascimento'], '%Y-%m-%dT%H:%M:%S.000Z')  # noqa: E501
                except Exception:
                    pass
                else:
                    q &= Q(data_nascimento=data['data_nascimento'].date())

            filtro_pessoas_count = PessoaAssistida.objects.filter(q).count()

            # Verifica se o número de registros não ultrapassou o limite configurado
            if config.BUSCAR_ATENDIMENTOS_FILTRO_NOME_MAX_PESSOAS and filtro_pessoas_count > config.BUSCAR_ATENDIMENTOS_FILTRO_NOME_MAX_PESSOAS:  # noqa: E501
                return JsonResponse({
                    'sucesso': False,
                    'mensagem': 'Erro: Seriam retornados mais de {} pessoas. Preencha mais campos e tente novamente.'.format(  # noqa: E501
                        # noqa: E501
                        filtro_pessoas_count
                    )
                })

        filtro_pessoas = PessoaAssistida.objects.filter(q).only(
            'id',
            'cpf',
            'nome',
            'nome_social',
            'apelido',
            'tipo',
            'data_nascimento'
        ).order_by(
            'nome'
        )

        pessoas = []

        for pessoa in filtro_pessoas.all():
            pessoa_dict = {
                'id': pessoa.id,
                'cpf': pessoa.cpf,
                'nome': pessoa.nome,
                'nome_social': pessoa.nome_social,
                'apelido': pessoa.apelido,
                'tipo': pessoa.tipo,
                'data_nascimento': None,
                'filiacao': []
            }

            if pessoa.data_nascimento:
                pessoa_dict['data_nascimento'] = pessoa.data_nascimento.isoformat()

            for filiacao in pessoa.filiacoes.all():
                pessoa_dict['filiacao'].append({'nome': filiacao.nome})

            pessoas.append(pessoa_dict)

        return JsonResponse({'sucesso': True, 'pessoas': pessoas}, safe=False)

    else:

        try:
            ligacao = Atendimento.objects.get(id=request.session.get('ligacao_id'))
        except ObjectDoesNotExist:
            ligacao = Atendimento.objects.create(tipo=Atendimento.TIPO_LIGACAO, cadastrado_por=request.user.servidor)

        request.session['foto'] = None
        request.session['pessoa_id'] = None
        request.session['ligacao_id'] = ligacao.id

        if ligacao.cronometro.expirado():
            return encerrar(request, ligacao.numero, Cronometro.MOTIVO_TEMPO_EXPIRADO)

        if ligacao.requerente is not None:
            return redirect('precadastro_continuar', ligacao.numero)

        deficiencias = Deficiencia.objects.all()

        endereco_form_initial = {
            'estado': Estado.objects.get(uf__iexact=settings.SIGLA_UF)
        }

        # forms
        endereco_form = EnderecoForm(initial=endereco_form_initial)

        relatorios = Relatorio.objects.filter(
            papeis=request.user.servidor.papel,
            locais__pagina=Local.PAG_PRECADASTRO_INDEX
        ).ativos()

        angular = 'BuscarPessoaModel'

        sigla_uf = settings.SIGLA_UF.upper()

        return render(request=request, template_name="atendimento/precadastro/iniciar.html", context=locals())


@never_cache
@login_required
def set_pessoa(request, pessoa_id):
    if request.session.get('ligacao_id'):

        pessoa = PessoaAssistida.objects.get(id=pessoa_id)
        request.session['pessoa_id'] = pessoa_id

        ligacao = Atendimento.objects.get(id=request.session.get('ligacao_id'))
        ligacao.set_requerente(pessoa_id)

        return JsonResponse({'error': False, 'pessoa': pessoa.to_dict()})

    return JsonResponse({'error': True})


class PainelView(ListView):
    queryset = AtendimentoDefensor.objects.annotate(
        tipo_painel=Case(
            When(
                ligacao=None,
                responsavel__isnull=True,
                data_exclusao__isnull=True,
                then=Value(PainelForm.SITUACAO_PENDENTE)
            ),
            When(
                ligacao=None,
                responsavel__isnull=False,
                data_exclusao__isnull=True,
                then=Value(PainelForm.SITUACAO_DISTRIBUIDO)
            ),
            When(
                Q(
                    Q(ligacao__tipo=Procedimento.TIPO_ENCAMINHAMENTO) |
                    Q(data_exclusao__isnull=False)
                ),
                then=Value(PainelForm.SITUACAO_BAIXADO)
            ),
            default=Value(PainelForm.SITUACAO_AGENDADO),
            output_field=IntegerField()
        )
    ).select_related(
        'comarca',
        'qualificacao__area',
        'responsavel__servidor__usuario'
    ).filter(
        defensoria__agendamento_online=True,
        tipo=Atendimento.TIPO_LIGACAO,
        partes__pessoa__desativado_por__isnull=True,
        data_atendimento=None
    ).only(
        'id',
        'numero',
        'inicial',
        'data_cadastro',
        'historico_recepcao',
        'comarca__nome',
        'qualificacao',
        'qualificacao__titulo',
        'qualificacao__area',
        'qualificacao__area__nome',
        'responsavel__servidor__nome',
        'responsavel__servidor__usuario__username',

    )

    paginate_by = 50
    template_name = 'atendimento/precadastro/painel.html'

    def get_context_data(self, **kwargs):

        context = super(PainelView, self).get_context_data(**kwargs)
        situacao = self.request.GET.get('situacao')

        # Obtém total de registros relacionados às lotações do usuário agrupados por situação
        queryset = self.queryset.order_by(
            'tipo_painel'
        ).values(
            'tipo_painel'
        ).annotate(
            total=Count('id')
        )

        # Se não tem permissão, limita a apenas pré-agendamentos das lotações
        if not self.request.user.has_perm(perm='atendimento.view_all_atendimentos'):
            queryset = queryset.filter(
                defensoria__in=self.request.user.servidor.defensor.atuacoes_vigentes().values('defensoria_id')
            )

        # Transforma resultado em formato compatível com painel de totais
        totais = {}
        for total in queryset:
            totais[total['tipo_painel']] = total['total']

        # Dados do painel de totais
        dados_painel_totais = [
            {
                'texto': 'Aguardando distribuição',
                'valor': totais.get(PainelForm.SITUACAO_PENDENTE, 0),
                'icone': 'fas fa-exclamation-circle',
                'cor': 'bg-yellow',
                'url': '{}?situacao={}'.format(reverse('precadastro_painel'), PainelForm.SITUACAO_PENDENTE),
                'selecionado': situacao == str(PainelForm.SITUACAO_PENDENTE),
            },
            {
                'texto': 'Aguardando análise',
                'valor': totais.get(PainelForm.SITUACAO_DISTRIBUIDO, 0),
                'icone': 'fas fa-clock',
                'cor': 'bg-blue',
                'url': '{}?situacao={}'.format(reverse('precadastro_painel'), PainelForm.SITUACAO_DISTRIBUIDO),
                'selecionado': situacao == str(PainelForm.SITUACAO_DISTRIBUIDO),

            },
            {
                'texto': 'Agendados',
                'valor': totais.get(PainelForm.SITUACAO_AGENDADO, 0),
                'icone': 'fas fa-check-circle',
                'cor': 'bg-green',
                'url': '{}?situacao={}'.format(reverse('precadastro_painel'), PainelForm.SITUACAO_AGENDADO),
                'selecionado': situacao == str(PainelForm.SITUACAO_AGENDADO),
            },
            {
                'texto': 'Encaminhados/Excluídos',
                'valor': totais.get(PainelForm.SITUACAO_BAIXADO, 0),
                'icone': 'fas fa-times-circle',
                'cor': 'bg-red',
                'url': '{}?situacao={}'.format(reverse('precadastro_painel'), PainelForm.SITUACAO_BAIXADO),
                'selecionado': situacao == str(PainelForm.SITUACAO_BAIXADO),
            },
        ]

        form = PainelForm(usuario=self.request.user)

        context.update({
            'situacao': situacao,
            'totais': dados_painel_totais,
            'form': PainelForm(self.request.GET, usuario=self.request.user),
            'PainelForm': form,
            'responsaveis': form.fields['responsavel'].queryset.values_list('id', 'servidor__nome'),
            'categorias': form.fields['agenda'].queryset.values_list('id', 'nome'),
            'existe_categoria_crc': Categoria.objects.filter(eh_categoria_crc=True).exists(),
            'angular': 'BuscarCtrl',
        })

        return context

    def get_queryset(self):

        queryset = super(PainelView, self).get_queryset()
        q = Q()

        # Se não tem permissão, limita a apenas pré-agendamentos das lotações
        if not self.request.user.has_perm(perm='atendimento.view_all_atendimentos'):
            q &= Q(defensoria__in=self.request.user.servidor.defensor.atuacoes_vigentes().values('defensoria_id'))

        form = PainelForm(self.request.GET, usuario=self.request.user)

        # Só filtra se valores de busca forem válidos
        if form.is_valid():

            data = form.cleaned_data

            # Filtro por prazo maior ou igual a data inicial
            if data.get('data_inicial'):
                q &= Q(data_cadastro__gte=data.get('data_inicial'))

            # Filtro por prazo menor ou igual a data final
            if data.get('data_final'):
                q &= Q(data_cadastro__lte=datetime.combine(data.get('data_final'), time.max))

            # Filtro por setor responsável (defensoria)
            if data.get('comarca'):
                q &= Q(comarca=data.get('comarca'))

            # Filtro por servidor responsável
            if data.get('responsavel'):
                q &= Q(responsavel=data.get('responsavel'))

            # Define situação padrão caso não tenha sido informada
            # TODO: definir permissão para visualizar pendentes primeiro
            if data.get('situacao') is None:
                data['situacao'] = PainelForm.SITUACAO_PENDENTE

            if data.get('agenda'):
                q &= Q(agenda=data.get('agenda'))

            # Filtro por situação
            if data.get('situacao') == PainelForm.SITUACAO_PENDENTE:
                q &= Q(ligacao=None) & Q(responsavel__isnull=True) & Q(data_exclusao__isnull=True)
            elif data.get('situacao') == PainelForm.SITUACAO_DISTRIBUIDO:
                q &= Q(ligacao=None) & Q(responsavel__isnull=False) & Q(data_exclusao__isnull=True)
            elif data.get('situacao') == PainelForm.SITUACAO_AGENDADO:
                q &= Q(ligacao__tipo__in=[
                    Procedimento.TIPO_AGENDAMENTO_INICIAL,
                    Procedimento.TIPO_AGENDAMENTO_RETORNO,
                    Procedimento.TIPO_REAGENDAMENTO
                ]) & Q(data_exclusao__isnull=True)
            elif data.get('situacao') == PainelForm.SITUACAO_BAIXADO:
                q &= (Q(ligacao__tipo=Procedimento.TIPO_ENCAMINHAMENTO) | Q(data_exclusao__isnull=False))

        return queryset.filter(q).order_by('data_cadastro')

    def post(self, request, *args, **kwargs):

        data = self.request.POST
        atendimentos_ids = data.getlist('atendimentos')

        for atendimento_id in atendimentos_ids:
            responsavel_id = data.get('responsavel-{}'.format(atendimento_id))
            categoria_id = data.get('categoria-{}'.format(atendimento_id))
            if not responsavel_id:
                responsavel_id = AtendimentoDefensor.objects.filter(
                    id=atendimento_id
                ).values_list('responsavel__id', flat=True)[0]

            if not categoria_id:
                if Categoria.objects.filter(eh_categoria_crc=True).exists():
                    categoria_id = Categoria.objects.filter(eh_categoria_crc=True).first()
                else:
                    categoria_id = Categoria.objects.filter().first()

            AtendimentoDefensor.objects.filter(
                id=atendimento_id
            ).update(
                responsavel=responsavel_id,
                agenda=categoria_id
            )

        return redirect('precadastro_painel')


class PainelAlterarComarcaView(UpdateView):
    """
    Altera comarca do pré-agendamento
    """
    model = AtendimentoDefensor
    slug_field = 'numero'
    fields = ['comarca']

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', '/')

    def form_valid(self, form):

        atendimento = form.save(commit=False)

        # TODO: Unificar com mesma validação contida em api.api_v1.utils.criar_agendamento()
        # Obtém defensoria responsável pela comarca
        defensoria = Defensoria.objects.get(
            comarca=atendimento.comarca.diretoria,
            agendamento_online=True
        )

        # Obtém atuação do defensor responsável
        atuacao = defensoria.all_atuacoes.nao_lotacoes().vigentes().order_by('tipo').first()

        # Recupera informações do defensor titular e substituto a partir da atuação identificada
        if atuacao.tipo == Atuacao.TIPO_SUBSTITUICAO:
            atendimento.defensor = atuacao.titular
            atendimento.substituto = atuacao.defensor
        else:
            atendimento.defensor = atuacao.defensor
            atendimento.substituto = None

        # Atualiza dados do atendimento
        atendimento.defensoria = defensoria
        atendimento.responsavel = None
        atendimento.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        for k, v in form.errors.items():
            messages.error(self.request, u'{0}: {1}'.format(k, v))
        return redirect(self.request.META.get('HTTP_REFERER', '/'))


class ReclamacaoPainel(ListView):
    template_name = 'atendimento/precadastro/painel_reclamacao.html'
    context_object_name = 'reclamacao_lst'
    paginate_by = 25

    def get_queryset(self):
        painel = self.kwargs.get('painel')
        print(" ############### ")
        print(painel)

        if painel == 'comercial':
            reclamacao_lst = self.get_reclamacao_comercial_queryset()
        elif painel == 'industrial':
            reclamacao_lst = self.get_reclamacao_industrial_queryset()
        elif painel == 'residencial':
            reclamacao_lst = self.get_reclamacao_residencial_queryset()
        elif painel == 'todos':
            reclamacao_lst = self.get_reclamacao_queryset()

        return reclamacao_lst

    def get(self, request, *args, **kwargs):
        response_original = super(ReclamacaoPainel, self).get(request, *args, **kwargs)

        return response_original

    def get_reclamacao_queryset(self):
        return Reclamacao.objects.prefetch_related('endereco_estabelecimento').filter(
            ativo=True,
            tipo_estabelecimento__in=[
                Reclamacao.ESTABELECIMENTO_COMERCIAL,
                Reclamacao.ESTABELECIMENTO_INDUSTRIAL,
                Reclamacao.ESTABELECIMENTO_RESIDENCIAL,
            ]
        ).order_by('-id')

    def get_reclamacao_comercial_queryset(self):
        return self.get_reclamacao_queryset().filter(
            tipo_estabelecimento=Reclamacao.ESTABELECIMENTO_COMERCIAL
        )

    def get_reclamacao_industrial_queryset(self):
        return self.get_reclamacao_queryset().filter(
            tipo_estabelecimento=Reclamacao.ESTABELECIMENTO_INDUSTRIAL
        )

    def get_reclamacao_residencial_queryset(self):
        return self.get_reclamacao_queryset().filter(
            tipo_estabelecimento=Reclamacao.ESTABELECIMENTO_RESIDENCIAL
        )

    def get_context_data(self, **kwargs):
        contexto = super(ReclamacaoPainel, self).get_context_data(**kwargs)

        painel = self.kwargs.get('painel')
        estabelecimento_comercial_count = self.get_reclamacao_comercial_queryset().count()
        estabelecimento_industrial_count = self.get_reclamacao_industrial_queryset().count()
        estabelecimento_residencial_count = self.get_reclamacao_residencial_queryset().count()
        todos_estabelecimentos_count = self.get_reclamacao_queryset().count()

        dados_painel_totais = [
            {
                'texto': 'Estabelecimentos Comerciais',
                'valor': estabelecimento_comercial_count,
                'icone': 'fa-shopping-cart',
                'cor': 'bg-yellow',
                'url': reverse(
                    'painel_acompanhar_reclamacao', kwargs={'painel': 'comercial'}
                ),
                'selecionado': painel == "comercial",
            },
            {
                'texto': 'Estabelecimentos Industriais',
                'valor': estabelecimento_industrial_count,
                'icone': ' fa-industry',
                'cor': 'bg-green',
                'url': reverse(
                    'painel_acompanhar_reclamacao', kwargs={'painel': 'industrial'}
                ),
                'selecionado': painel == "industrial",
            },
            {
                'texto': 'Estabelecimentos Residenciais',
                'valor': estabelecimento_residencial_count,
                'icone': ' fa-home',
                'cor': 'bg-red',
                'url': reverse(
                    'painel_acompanhar_reclamacao', kwargs={'painel': 'residencial'}
                ),
                'selecionado': painel == "residencial",
            },
            {
                'texto': 'Todos os Estabelecimentos',
                'valor': todos_estabelecimentos_count,
                'icone': ' fa-globe',
                'cor': 'bg-blue',
                'url': reverse(
                    'painel_acompanhar_reclamacao', kwargs={'painel': 'todos'}
                ),
                'selecionado': painel == "todos",
            },
        ]
        contexto['painel'] = painel
        contexto['totais'] = dados_painel_totais
        contexto['bairros'] = Bairro.objects.annotate(
            total_reclamacoes=Count('endereco__reclamacao', distinct=True),
            total_comercial=Count(
                Case(
                    When(Q(endereco__reclamacao__tipo_estabelecimento=1), then=1),
                    output_field=IntegerField()
                ),
            ),
            total_industrial=Count(
                Case(
                    When(Q(endereco__reclamacao__tipo_estabelecimento=2), then=1),
                    output_field=IntegerField()
                ),
            ),
            total_residencial=Count(
                Case(
                    When(Q(endereco__reclamacao__tipo_estabelecimento=3), then=1),
                    output_field=IntegerField()
                ),
            ),
        ).order_by('-total_reclamacoes')[:10]

        return contexto
