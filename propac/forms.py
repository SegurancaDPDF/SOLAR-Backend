# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Bibliotecas de terceiros
import django
from django import forms
from django.urls import reverse_lazy

# Solar
from django_addanother.widgets import AddAnotherWidgetWrapper

# Modulos locais
from djdocuments.models import Documento
from .models import Movimento, MovimentoTipo, Procedimento, DocumentoPropac
from contrib.models import Area


class MovimentoForm(forms.ModelForm):  # formulario que define campos, widgets e textos
    class Meta:
        model = Movimento
        fields = ('tipo', 'data_movimento', 'procedimento', 'historico')
        widgets = {
            'data_movimento': forms.DateInput(
                attrs={
                    'placeholder': 'Data Inicial',
                    'data-date-format': 'dd/mm/yyyy',
                    'class': 'datepicker',
                    'autocomplete': 'off'
                }),
            'procedimento': forms.HiddenInput()
        }
        help_texts = {
            'data_movimento': 'Data que foi realizado do movimento',
            'tipo': 'Tipo do movimento',
        }

    # construtor do formulario Verifica o tipo de procedimento e ajusta as opções do campo 'tipo' de acordo
    def __init__(self, *args, **kwargs):

        super(MovimentoForm, self).__init__(*args, **kwargs)

        if 'initial' in kwargs:
            if 'procedimento' in kwargs['initial'] and kwargs['initial']['procedimento'].tipo == Procedimento.TIPO_PROPAC:  # noqa 
                if kwargs['initial']['procedimento'].movimentos_ativos_nao_removidos().filter(
                        tipo__instauracao=True).exists():
                    self.fields['tipo'].queryset = MovimentoTipo.objects.filter(ativo=True, instauracao=False)
                else:
                    self.fields['tipo'].queryset = MovimentoTipo.objects.filter(ativo=True, instauracao=True)


# adiciona validação para garantir que um movimento tenha pelo menos um documento ou anexo associado
class EditarMovimentoForm(MovimentoForm):
    def clean(self):  # verifica se existem documentos associados ao movimento
        cleaned_data = super(EditarMovimentoForm, self).clean()
        if not self.instance.documentos.exists():
            self.add_error(None, 'Movimento deve possuir no mínimo um documento ou anexo. Clique no botão Novo, abaixo')
        return cleaned_data


class CadastraProcedimentoForm(forms.ModelForm):  # permite cadastrar novos procedimentos com campos específicos
    class Meta:
        model = Procedimento
        fields = ('tipo', 'defensoria_responsavel', 'defensor_responsavel', 'assunto', 'area')
        widgets = {
            'assunto': forms.Textarea(attrs={'cols': 40, 'rows': 4, 'maxlength': 255}),
        }

    def __init__(self, *args, **kwargs):  # permite filtrar as opções de defensorias e áreas para selecao
        defensorias_responsavel_queryset = kwargs.pop('defensorias_responsavel_queryset', None)
        defensores_responsavel_queryset = kwargs.pop('defensores_responsavel_queryset', None)

        super(CadastraProcedimentoForm, self).__init__(*args, **kwargs)

        if defensorias_responsavel_queryset:
            self.fields['defensoria_responsavel'].queryset = defensorias_responsavel_queryset
            self.fields['defensoria_responsavel'].widget.attrs.update({
                'ng-model': 'defensoria_responsavel',
                'ng-change': 'listar_defensores(defensoria_responsavel)'
            })

            self.fields['defensor_responsavel'].queryset = defensores_responsavel_queryset
            self.fields['area'].queryset = Area.objects.filter(ativo=True)


class AlteraProcedimentoForm(forms.ModelForm):  # formulario de editar procedimento organizado com plugin de widgets
    class Meta:
        model = Procedimento
        fields = (
            'assunto',
            'defensoria_responsavel',
            'defensor_responsavel',
            'representante',
            'representado',
            'acesso',
            'defensorias_acesso',
            'area'
        )
        widgets = {
            'assunto': forms.Textarea(),
            'representante': forms.Textarea(),
            'representado': forms.Textarea(),
        }

    def __init__(self, *args, **kwargs):
        defensorias_responsavel_queryset = kwargs.pop('defensorias_responsavel_queryset', None)
        defensores_responsavel_queryset = kwargs.pop('defensores_responsavel_queryset', None)

        super(AlteraProcedimentoForm, self).__init__(*args, **kwargs)

        if defensorias_responsavel_queryset:
            self.fields['defensoria_responsavel'].queryset = defensorias_responsavel_queryset
            self.fields['defensoria_responsavel'].required = True
            self.fields['defensoria_responsavel'].widget.attrs.update({
                'ng-model': 'defensoria_responsavel',
                'ng-change': 'listar_defensores(defensoria_responsavel)'
            })

            self.fields['defensor_responsavel'].queryset = defensores_responsavel_queryset
            self.fields['defensor_responsavel'].required = True
            self.fields['defensor_responsavel'].widget.attrs.update({
                'ng-model': 'defensor_responsavel'
            })

            self.fields['defensorias_acesso'].widget.attrs.update({
                'ng-model': 'defensorias_acesso'
            })

            self.fields['area'].queryset = Area.objects.filter(ativo=True)


class RemocaoMovimentoForm(forms.ModelForm):
    class Meta:
        model = Movimento
        fields = ('motivo_remocao',)


class AddAnotherWidgetWrapper2(AddAnotherWidgetWrapper):
    class Media:
        extend = False
        css = {
            'all': ('django_addanother/addanother.css',)
        }
        js = (
            'django_addanother/django_jquery.js',
            'luzfcb_djdocuments/js/RelatedObjectLookups.js',
        )
        if django.VERSION < (1, 9):
            # This is part of "RelatedObjectLookups.js" in Django 1.9
            js += ('admin/js/related-widget-wrapper.js',)


class DocumentoModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        label = '{}'.format(obj.identificador_versao)
        return label


class CriarDocumentoPropacForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CriarDocumentoPropacForm, self).__init__(*args, **kwargs)

        css_classes = self.fields['anexo'].widget.attrs.get('class', '')
        css_classes = '{} {}'.format(css_classes, 'inputfile')

        self.fields['anexo'].widget.attrs.update({
            'class': css_classes,
            'file-model': 'documento.anexo',
        })
        self.fields['tipo_anexo'].widget.attrs.update({
            'ng-model': 'documento.tipo_anexo',
            # 'ng-show': 'mostrar'
        })
        self.fields['tipo_anexo'].queryset = self.fields['tipo_anexo'].queryset.filter(ativo=True)
        self.fields['documento'].widget.attrs.update({
            # 'ng-hide': 'mostrar'
        })

    documento = DocumentoModelChoiceField(
        required=False,
        # empty_label=None,
        queryset=Documento.objects.all(),
        widget=AddAnotherWidgetWrapper2(
            forms.Select(attrs={
                'ng-model': 'documento.documento',
            }),
            reverse_lazy('documentos:create'),

        )
    )

    class Meta:
        model = DocumentoPropac
        fields = ('anexo', 'tipo_anexo', 'documento')

    def clean(self):
        cleaned_data = super(CriarDocumentoPropacForm, self).clean()
        anexo = cleaned_data.get("anexo")
        documento = cleaned_data.get("documento")

        if not anexo and not documento:
            self.add_error(None, 'Anexo ou Documento deve ser enviado')


class NovoMovimentoForm(forms.ModelForm):
    class Meta:
        model = Movimento
        fields = ('tipo', 'data_movimento', 'historico')
        widgets = {
            'data_movimento': forms.DateInput(
                attrs={
                    'placeholder': 'Data Inicial',
                    'data-date-format': 'dd/mm/yyyy',
                    # 'bs-datepicker': True
                    'class': 'datepicker'
                }),
        }
