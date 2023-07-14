# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import TypedChoiceField
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from constance import config

from atividade_extraordinaria.models import AtividadeExtraordinariaTipo
from defensor.models import Defensor
from .form_fields import (
    FixAtribsFormMixin,
    PapelModelChoiceField,
    DefensorSupervisorChoiceField,
    ComarcaChoiceField,
)
from .models import Comarca, Bairro, Defensoria, DefensoriaTipoEvento, Endereco, Estado, Municipio, Papel, Servidor, Telefone
import contrib.services
from .validators import validate_CPF
from random import randint
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

# Modulos locais


# Solar


class BootstrapForm(forms.ModelForm):
    def as_bs(self):
        return render_to_string('_bootstrap_form.html', {'form': self})

    def __init__(self, *args, **kwargs):
        super(BootstrapForm, self).__init__(*args, **kwargs)


class AngularFormMixin(object):
    angular_prefix = None

    def __init__(self, *args, **kwargs):
        self.angular_prefix = kwargs.pop('angular_prefix', None)
        super(AngularFormMixin, self).__init__(*args, **kwargs)

        if self.angular_prefix:
            for field_name in self.fields:
                self.fields[field_name].widget.attrs['ng-model'] = '{}.{}'.format(self.angular_prefix, field_name)


class BuscarDefensoriaForm(forms.Form):
    filtro = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'off',
                'class': 'span3',
                'placeholder': 'Buscar pelo nome da defensoria...'
            }
        )
    )
    comarca = forms.ModelChoiceField(
        queryset=Comarca.objects.ativos(),
        empty_label="Selecione uma comarca...",
        required=False,
        widget=forms.Select(attrs={'class': 'span3 ativar-select2'})
    )


class EditarDefensoriaForm(BootstrapForm):
    class Meta:
        model = Defensoria
        fields = ['atuacao', 'telefone', 'email', 'cabecalho_documento', 'rodape_documento']
        widgets = {
            'atuacao': forms.TextInput(attrs={'class': 'span12'}),
            'telefone': forms.TextInput(attrs={
                'class': 'span4',
                'ng-model': 'telefone',
                'ui-mask': '[[ telefone.length == 11 ? "(99) 99999-9999" : "(99) 9999-9999?9" ]]'}),
            'email': forms.EmailInput(attrs={'class': 'span4', 'placeholder': 'Digite o E-mail'})
        }

    def clean_telefone(self):
        if self.cleaned_data['telefone']:
            return self.cleaned_data['telefone'].replace('_', '')


class EditarDefensoriaTiposEventosForm(BootstrapForm):
    class Meta:
        model = Defensoria
        fields = ['tipos_eventos']
        widgets = {
            'tipos_eventos': forms.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostra apenas tipos de ativos ativos e relacionados às atividades extraordinárias
        self.fields['tipos_eventos'].queryset = AtividadeExtraordinariaTipo.objects.ativos().order_by('nome')

    def save(self, commit=True):

        # Intercepta 'tipo_eventos' uma vez que é um m2m com through
        tipos_eventos = self.cleaned_data.pop('tipos_eventos')

        # Salva dados da defensoria
        defensoria = super().save(commit=False)

        # Habilita recurso de at. extraordinária se forem selecionados eventos
        defensoria.pode_cadastrar_atividade_extraordinaria = True if len(tipos_eventos) > 0 else False
        defensoria.save()

        # TODO: Ver se há necessidade de incluir campos de auditoria
        # Remove vínculos com os tipos de eventos
        defensoria.defensoriatipoevento_set.exclude(tipo_evento__in=tipos_eventos).delete()

        # Adiciona vínculos com os tipos de eventos
        for tipo_evento in tipos_eventos:
            DefensoriaTipoEvento.objects.update_or_create(
                defensoria=defensoria,
                tipo_evento=tipo_evento,
                defaults={
                    'conta_estatistica': True
                }
            )

        return defensoria


class RequiredFiedlsMixin(object):
    required_fields = []

    def __init__(self, *args, **kwargs):

        super(RequiredFiedlsMixin, self).__init__(*args, **kwargs)

        for field in self.required_fields:
            self.fields[field].required = True

        for field in self.fields:
            if self.fields[field].required:
                self.fields[field].widget.attrs['required'] = True


class EnderecoForm(BootstrapForm):
    estado = forms.ModelChoiceField(queryset=Estado.objects.order_by('nome'), empty_label=None)
    bairro_nome = forms.CharField(label='Bairro', required=False)

    class Meta:
        model = Endereco
        fields = (
            'cep', 'estado', 'municipio', 'bairro', 'bairro_nome', 'logradouro', 'numero', 'complemento', 'tipo_area')

    def __init__(self, *args, **kwargs):

        self.base_fields['logradouro'].widget = forms.TextInput(attrs={'class': 'span6'})
        self.base_fields['numero'].widget = forms.TextInput(attrs={'class': 'span3'})
        self.base_fields['complemento'].widget = forms.TextInput(attrs={'class': 'span6'})
        self.base_fields['cep'].widget = forms.TextInput(attrs={'class': 'span3', 'data-mask': '99.999-999'})
        self.base_fields['bairro'].widget = forms.HiddenInput()
        self.base_fields['municipio'].widget = forms.Select(attrs={'class': 'span6'})
        self.base_fields['tipo_area'].widget = forms.RadioSelect(choices=Endereco.LISTA_AREA)

        super(EnderecoForm, self).__init__(*args, **kwargs)

        self.fields['estado'].widget.attrs = {'class': 'span3'}
        self.fields['bairro_nome'].widget.attrs = {'class': 'span6'}

        # recupera nome do bairro a partir do id
        if 'instance' in kwargs and kwargs['instance']:
            if kwargs['instance'].bairro is not None:
                bairro = Bairro.objects.get(id=kwargs['instance'].bairro.id)
                self.fields['bairro_nome'].initial = bairro.nome

        # carrega lista de municipios do estado selecionado
        try:
            self.fields['municipio'].queryset = Municipio.objects.filter(estado_id=kwargs['initial']['estado'])
        except Exception:
            self.fields['municipio'].queryset = Municipio.objects.none()


class TelefoneForm(BootstrapForm):
    """ Formulario de cadastro de telefone (generico) """

    class Meta:
        model = Telefone
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.base_fields['tipo'].widget = forms.Select(choices=Telefone.LISTA_TIPO, attrs={'class': 'span2'})
        self.base_fields['ddd'].widget = forms.TextInput(attrs={'class': 'span2', 'placeholder': 'DDD'})
        self.base_fields['numero'].widget = forms.TextInput(
            attrs={'class': 'span4', 'placeholder': 'Digite o Telefone', 'data-mask': '9999-9999'})

        super(TelefoneForm, self).__init__(*args, **kwargs)


class BuscarServidorForm(forms.Form):
    comarca = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'span3 ativar-select2',
        }),
        empty_label='< TODAS COMARCAS >',
        queryset=Comarca.objects.ativos()
    )

    papel = forms.ModelChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'span3 ativar-select2',
        }),
        empty_label='< TODOS PAPÉIS >',
        queryset=Papel.objects.all()
    )

    nome = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'span4',
                'placeholder': 'Pesquisar por nome ou matrícula'}))

    def is_valid(self):
        valid = super().is_valid()

        if valid and not self.cleaned_data['comarca'] and not self.cleaned_data['papel'] and not self.cleaned_data['nome']:
            valid = False

        return valid


class ServidorForm(forms.ModelForm):
    papel = PapelModelChoiceField(required=False)

    class Meta:
        model = Servidor
        fields = ('cpf', 'matricula', 'comarca', 'sexo', 'papel', 'ativo')


class ServidorFotoForm(forms.ModelForm):
    class Meta:
        model = Servidor
        fields = ('foto',)


class NomeCompletoCPFForm(FixAtribsFormMixin, forms.Form):
    def __init__(self, *args, **kwargs):
        self.dados_servidor_no_athenas = None
        self.dados_servidor_ldap = None
        self.foi_consulta_matricula = False
        super(NomeCompletoCPFForm, self).__init__(*args, **kwargs)

    nome_completo = forms.CharField(
        max_length=300,
        help_text='Digite o Nome Completo sem acentuação',
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                'required': True,
                'placeholder': 'Digite o Nome completo sem acentuação',
                'class': 'span4',
                'ng-model': 'pesquisa.nome_completo'
            }

        )
    )

    cpf_matricula = forms.CharField(
        label='Pesquisar',
        max_length=14,
        help_text='Digite o CPF ou matricula para verificar se o servidor já possui cadastro',
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                'required': True,
                'class': 'somente_numeros',
                'placeholder': 'CPF ou Matrícula',
                'ng-paste': "removerNaoNumericos($event, pesquisa, 'cpf_matricula')",
                'ng-model': 'pesquisa.cpf_matricula'

            }
        )
    )
    error_messages = {
        'cpf_matricula': '"{}" já possui cadastro no sistema',
    }

    def clean_nome_completo(self):
        nome_completo = self.cleaned_data['nome_completo']

        return nome_completo

    def clean_cpf(self):
        cpf = self.cleaned_data["cpf_matricula"]
        cpf = contrib.services.CARACTERES_NUMERICOS.sub('', cpf)

        try:
            validate_CPF(cpf)
        except ValidationError:
            raise forms.ValidationError(
                'CPF Inválido. Digite o CPF com 11 digitos, sem pontuacao e traço',
                code='cpf_matricula',
            )

        return cpf


class SolarUserCreationForm(FixAtribsFormMixin, forms.ModelForm):
    nome = forms.CharField(label="Nome Completo", max_length=300, widget=forms.TextInput(
        attrs={
            # "autocomplete": "off",
            "class": "span4"
        }
    )
                           )
    cpf = forms.CharField(label='CPF', max_length=11, widget=forms.TextInput(
        attrs={
            'ng-paste': "removerNaoNumericos($event, servidor, 'cpf')",
        }
    )
                          )
    papel = PapelModelChoiceField()
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'matricula': "Matricula é obrigatório para o papel selecionado",
        'defensor_supervisor': "Supervisor é obrigatório para o papel selecionado",
    }
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above, for verification."))

    sexo = TypedChoiceField(choices=Servidor.LISTA_SEXO, coerce=int, widget=forms.RadioSelect)
    matricula = forms.CharField(max_length=200, required=False)
    email = forms.EmailField(
        max_length=128,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                'required': True,
            }

        )
    )
    defensor_supervisor = DefensorSupervisorChoiceField(required=False)
    comarca = ComarcaChoiceField()
    username = forms.CharField(max_length=254, widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        self.papel = None
        if kwargs and 'papel' in kwargs:
            self.papel = kwargs.pop('papel')

        super(SolarUserCreationForm, self).__init__(*args, **kwargs)

        if config.USAR_API_EGIDE_AUTH or config.ENVIAR_EMAIL_AO_CADASTRAR_SERVIDOR:
            self.fields['password1'].required = False
            self.fields['password2'].required = False
            self.fields['password1'].widget = forms.HiddenInput(attrs={'required': False})
            self.fields['password2'].widget = forms.HiddenInput(attrs={'required': False})

        # coloca o atributo 'ng-model' em todos campos
        for field_name in self.fields:
            field = self.fields.get(field_name)
            ng_model_value = 'servidor.{}'.format(field_name)
            ng_disabled = '!editaveis.{}'.format(field_name)
            self.fields[field_name].widget.attrs['ng-model'] = ng_model_value
            self.fields[field_name].widget.attrs['ng-disabled'] = ng_disabled
            self.fields[field_name].widget.attrs['keep-current-value'] = True
            self.fields[field_name].widget.attrs['autocomplete'] = "off"
            if (isinstance(self.fields[field_name].widget, forms.DateInput) and
                    not isinstance(self.fields[field_name].widget, forms.HiddenInput)):
                new_attrs = {
                }
                field.widget.attrs.update(new_attrs)

    def clean_defensor_supervisor(self):
        defensor_supervisor = self.cleaned_data['defensor_supervisor']

        return defensor_supervisor

    def clean_username(self):
        username = self.cleaned_data['username']
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if config.ENVIAR_EMAIL_AO_CADASTRAR_SERVIDOR:
            # gera uma senha aleatória para salvar temporariamente como senha do usuário
            lower_char = "qwertyuiopasdfghjklzxcvbnm"
            upper_char = lower_char.upper()[::-1]  # -1 inverte a ordem
            numbers = "1234567890"
            _schar = "!@#$%&*"
            types = [lower_char, upper_char, numbers, _schar]
            password2 = ""
            password_length = 12

            for i in range(0, password_length):
                char_exists_in_password = False
                while not char_exists_in_password:
                    type_char = randint(0, (len(types) - 1))
                    position = randint(0, (len(types[type_char]) - 1))
                    char = types[type_char][position]
                    if char not in password2:
                        password2 += char
                        char_exists_in_password = True
        else:
            if password1 and password2 and password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def clean(self):
        cleaned_data = super(SolarUserCreationForm, self).clean()
        cpf = cleaned_data.get('cpf')
        nome = cleaned_data.get('nome')
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        papel = cleaned_data.get('papel')
        matricula = cleaned_data.get('matricula')
        defensor_supervisor = cleaned_data.get('defensor_supervisor')
        dados = contrib.services.buscar_servidor_api_athenas_e_ldap(cpf, nome)
        if dados and dados.get('dados_servidor'):
            username = dados['dados_servidor']['username']
        erros = dados.get('errors')

        if User.objects.filter(username=username).exists():
            msg = 'Cadastro duplicado: O usuário "{username}" já está atribuido para outra pessoa. Por favor, entre em\
                 contato com o suporte técnico do sistema e informe o nome completo, CPF, matricula, comarca\
                     e defensor supervisor'  # noqa: E501
            self.add_error(None, msg.format(username=username))

        if User.objects.filter(email=email).exists():
            msg = 'Cadastro duplicado: O email "{email}" já está atribuido para outra pessoa. Por favor, entre em\
                 contato com o suporte técnico do sistema'  # noqa: E501
            self.add_error(None, msg.format(email=email))

        if erros and '__all__' in erros:
            for erro in erros['__all__']:
                self.add_error(None, erro)

        # validacoes
        if papel and papel.requer_matricula and not matricula:
            self.add_error('matricula', self.error_messages['matricula'])

        if papel and papel.requer_supervisor and not defensor_supervisor:
            self.add_error('defensor_supervisor', self.error_messages['defensor_supervisor'])

        if papel and not papel.requer_matricula and not matricula:
            matricula = papel.nome[:256]

        cleaned_data['matricula'] = matricula
        cleaned_data['username'] = username
        cleaned_data['email'] = email
        return cleaned_data

    def save(self, commit=True):
        nome_completo = self.cleaned_data.get('nome')
        papel = self.cleaned_data.get('papel')
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        matricula = self.cleaned_data.get('matricula')
        defensor_supervisor = self.cleaned_data.get('defensor_supervisor')
        # cpf = self.cleaned_data.get('cpf')

        # enquanto last_name for maior que "tamanho_maximo_last_name",
        # mudar o proximo nome para first_name
        first_last_name_idx = 1
        tamanho_maximo_first_name = 30
        tamanho_maximo_last_name = 30
        nome_completo_partes = nome_completo.split()
        first_name = nome_completo_partes[0]
        last_name = " ".join(nome_completo_partes[first_last_name_idx:])
        while len(last_name) > tamanho_maximo_last_name and len(first_name) < tamanho_maximo_first_name:
            first_last_name_idx += 1
            first_name = " ".join(nome_completo_partes[0:first_last_name_idx])
            last_name = " ".join(nome_completo_partes[first_last_name_idx:])

        # dados_api = buscar_servidor_api_athenas_e_ldap(cpf, nome_completo)

        dados_usuario = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'username': username,
        }

        usuario = User(**dados_usuario)
        usuario.set_password(self.cleaned_data.get('password1'))
        usuario.save()

        if papel:
            grupos_list = list(papel.grupos.all())
            usuario.groups.add(*grupos_list)
            usuario.save()

        self.instance.usuario = usuario

        if papel and papel.requer_matricula and not matricula:
            self.instance.matricula = papel.nome[:256]

        saved_instance = super(SolarUserCreationForm, self).save(commit=commit)
        if papel and defensor_supervisor and papel.requer_supervisor:
            try:
                assessor = Defensor.objects.get(servidor=saved_instance)
            except Defensor.DoesNotExist:
                assessor, foi_criado_agora = Defensor.objects.get_or_create(
                    servidor=saved_instance,
                    supervisor=defensor_supervisor,
                )
                if not assessor.ativo:
                    assessor.ativo = True
                    assessor.save()
            else:
                assessor.supervisor = defensor_supervisor
                assessor.ativo = True
                assessor.save()

        return saved_instance

    class Meta:
        model = Servidor
        fields = [
            'nome',
            'cpf',
            'email',
            'papel',
            'password1',
            'password2',
            'matricula',
            'defensor_supervisor',
            'comarca',
            'sexo',
        ]


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label=_("Email"), max_length=254)

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        body = loader.render_to_string(email_template_name, context)

        #  Enviar email aqui
        fromaddr = settings.EMAIL_HOST_USER
        toaddr = to_email
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)

        if settings.EMAIL_USE_TLS:
            server.starttls()

        server.login(fromaddr, settings.EMAIL_HOST_PASSWORD)
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.

        """
        active_users = get_user_model().objects.filter(
            email__iexact=email, is_active=True)
        return (u for u in active_users if u.has_usable_password())

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        email = self.cleaned_data["email"]
        for user in self.get_users(email):
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            context = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',   
            }

            self.send_mail(subject_template_name, email_template_name,
                           context, from_email, user.email,
                           html_email_template_name=html_email_template_name)
