# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from django import forms
import six

from contrib.models import Comarca, Papel
from defensor.models import Defensor


class UserModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name()


# filtra os defensores com base em determinados critérios e os ordena pelo nome do servidor
class DefensorSupervisorChoiceField(forms.ModelChoiceField):  
    def __init__(self, empty_label="---------", required=True, widget=None, label=None,
                 initial=None, help_text='', to_field_name=None, limit_choices_to=None, *args, **kwargs):
        queryset = Defensor.objects.filter(supervisor=None, eh_defensor=True, ativo=True).order_by('servidor__nome')
        super(DefensorSupervisorChoiceField, self).__init__(queryset=queryset, empty_label=empty_label,
                                                            required=required, widget=widget,
                                                            label=label, initial=initial, help_text=help_text,
                                                            to_field_name=to_field_name,
                                                            limit_choices_to=limit_choices_to,
                                                            *args, **kwargs)
        current_class_attr = self.widget.attrs.get('class', None)
        new_class_to_append = 'noupper ativar-select2'
        if current_class_attr:
            self.widget.attrs.update({
                'class': '{} {}'.format(current_class_attr, new_class_to_append)
            })
        else:
            self.widget.attrs.update({
                'class': '{}'.format(new_class_to_append)
            })


# obtém todas as comarcas do modelo Comarca e atualiza o atributo class do widget
class ComarcaChoiceField(forms.ModelChoiceField):
    def __init__(self, empty_label="---------", required=True, widget=None, label=None,
                 initial=None, help_text='', to_field_name=None, limit_choices_to=None, *args, **kwargs):
        queryset = Comarca.objects.all()
        super(ComarcaChoiceField, self).__init__(queryset=queryset, empty_label=empty_label,
                                                 required=required, widget=widget,
                                                 label=label, initial=initial,
                                                 help_text=help_text, to_field_name=to_field_name,
                                                 limit_choices_to=limit_choices_to, *args, **kwargs)

        current_class_attr = self.widget.attrs.get('class', None)
        new_class_to_append = 'noupper ativar-select2'
        if current_class_attr:
            self.widget.attrs.update({
                'class': '{} {}'.format(current_class_attr, new_class_to_append)
            })
        else:
            self.widget.attrs.update({
                'class': '{}'.format(new_class_to_append)
            })


# adiciona funcionalidades de ajuste de atributos a todos os campos do formulário
class FixAtribsFormMixin(object):
    def __init__(self, *args, **kwargs):
        super(FixAtribsFormMixin, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            current_class_attr = field.widget.attrs.get('class', None)
            new_class_to_append = 'noupper'
            if current_class_attr:
                field.widget.attrs.update({
                    'class': '{} {}'.format(current_class_attr, new_class_to_append)
                })
            else:
                field.widget.attrs.update({
                    'class': '{}'.format(new_class_to_append)
                })
            if isinstance(field, forms.DateField) and not isinstance(field.widget, forms.HiddenInput):
                new_attrs = {"placeholder": field.label,
                             "bs-datepicker": "",
                             # "data-provide": "datepicker",
                             "data-date-format": "dd/mm/yyyy",
                             "data-mask": "99/99/9999",
                             # "data-toggle": "datepicker",
                             # 'class': '{} {}'.format(field.widget.attrs.get('class', ''), 'ativar-datepicker')
                             }
                field.widget.attrs.update(new_attrs)


# filtra os papéis com base em determinados critérios e atualiza o atributo class do widget
class PapelModelChoiceField(forms.ModelChoiceField):
    def __init__(self, empty_label="---------", required=True, widget=None, label=None,
                 initial=None, help_text='', to_field_name=None, limit_choices_to=None, *args, **kwargs):
        queryset = Papel.objects.filter(requer_superusuario=False, ativo=True)
        super(PapelModelChoiceField, self).__init__(queryset=queryset, empty_label=empty_label,
                                                    required=required, widget=widget, label=label, initial=initial,
                                                    help_text=help_text, to_field_name=to_field_name,
                                                    limit_choices_to=limit_choices_to,
                                                    *args, **kwargs)
        current_class_attr = self.widget.attrs.get('class', None)
        new_class_to_append = 'noupper ativar-select2'
        if current_class_attr:
            self.widget.attrs.update({
                'class': '{} {}'.format(current_class_attr, new_class_to_append)
            })
        else:
            self.widget.attrs.update({
                'class': '{}'.format(new_class_to_append)
            })

    def label_from_instance(self, obj):
        return obj.nome


class PapelForm(forms.Form):
    papel = PapelModelChoiceField()


class EmptyChoiceFieldMixin(object):
    def __init__(self, choices=(), empty_label=None, required=True, widget=None, label=None,
                 initial=None, help_text=None, *args, **kwargs):
        # prepend an empty label if it exists
        if empty_label is not None:
            choices = tuple([(six.text_type(''), empty_label)] + list(choices))

        super(EmptyChoiceFieldMixin, self).__init__(choices=choices, required=required, widget=widget, label=label,
                                                    initial=initial, help_text=help_text, *args, **kwargs)


class EmptyTypedChoiceField(EmptyChoiceFieldMixin, forms.TypedChoiceField):
    pass
