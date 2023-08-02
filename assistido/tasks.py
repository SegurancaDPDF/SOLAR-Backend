from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail

from defensor.models import Atuacao
from .models import PessoaAssistida, Acesso


# definindo uma tarefa assíncrona usando o Celery para notificar sobre uma solicitação de acesso
@shared_task
def notificar_solicitacao_acesso(pessoa_id, user_id, url_solar):

    pessoa = PessoaAssistida.objects.get(id=pessoa_id)
    acessos = Acesso.objects.filter(assistido_id=pessoa.id, nivel=Acesso.NIVEL_ADMINISTRACAO)
    servidor = User.objects.get(id=user_id).servidor

    # criando uma lista de destinatários para o e-mail
    destinatarios = []
    for acesso in acessos:
        # recuperando os e-mails dos defensores atuantes na mesma defensoria do acesso
        destinatarios += Atuacao.objects.vigentes().filter(
            defensoria=acesso.defensoria,
        ).exclude(
            defensor__servidor__usuario__email=''
        ).values_list(
            'defensor__servidor__usuario__email',
            flat=True
        )
    # montando a URL para editar o cadastro do assistido
    url_assistido = url_solar + '/assistido/editar/' + str(pessoa.id) + '/?tab=3'

    # montando a mensagem de notificação a ser enviada por e-mail
    mensagem = 'Olá, este é um email automático para lhe avisar que ' + servidor.nome + ' solicitou acesso '
    mensagem += 'a dados sigilosos do cadastro do assistido ' + pessoa.nome + ', com CPF nº '
    mensagem += str(pessoa.cpf) if pessoa.cpf is not None else "(Não informado)"
    mensagem += '.<br> Para conceder ou negar o acesso clique no link abaixo, vá na aba Adicional e clique no ícone da chave no campo Situação. <br><br>'
    mensagem += '<a href="' + url_assistido + '">' + url_assistido + '</a><br><br>'
    mensagem += 'Obs: A notificação foi enviada a todos lotados nos ofícios criadores do cadastro.'

    # enviando o e-mail de notificação com os detalhes e a URL para os destinatários
    send_mail(
        '[SOLAR] Solicitação de acesso a dados sigilosos - ' + pessoa.nome,
        '',
        settings.DEFAULT_FROM_EMAIL,
        set(destinatarios),
        html_message=mensagem,
        fail_silently=False,
    )
    # retornando um dicionário com informações sobre o resultado da tarefa
    return {
        'sucesso': True,
        'mensagem': 'E-mail enviado com sucesso!'
    }
