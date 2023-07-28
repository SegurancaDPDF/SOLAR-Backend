# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.http.response import Http404
from django.utils.translation import ugettext as _

from .models import Defensor


class SingleAtendimentoDefensorObjectMixin(object):
    """
    Provides the ability to retrieve a single 'Defensor' object for further manipulation.
    """
    atendimentodefensor_object = None
    atendimentodefensor_model = Defensor
    atendimentodefensor_queryset = None
    atendimentodefensor_slug_field = 'numero'
    atendimentodefensor_context_object_name = 'atendimentodefensor_object'
    atendimentodefensor_slug_url_kwarg = 'atendimento_numero'
    atendimentodefensor_pk_url_kwarg = 'atendimentodefensor_pk'
    atendimentodefensor_query_pk_and_slug = False
    atendimentodefensor_disable_if_url_kwarg_not_is_available = False

    def get(self, request, *args, **kwargs):
        if not self.atendimentodefensor_disable_if_url_kwarg_not_is_available or (
            self.kwargs.get(self.atendimentodefensor_pk_url_kwarg, None) or self.kwargs.get(
                self.atendimentodefensor_slug_url_kwarg, None)):
            self.atendimentodefensor_object = self.get_atendimentodefensor_object()
        return super(SingleAtendimentoDefensorObjectMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.atendimentodefensor_disable_if_url_kwarg_not_is_available or (
            self.kwargs.get(self.atendimentodefensor_pk_url_kwarg, None) or self.kwargs.get(
                self.atendimentodefensor_slug_url_kwarg, None)):
            self.atendimentodefensor_object = self.get_atendimentodefensor_object()
        return super(SingleAtendimentoDefensorObjectMixin, self).post(request, *args, **kwargs)

    def get_atendimentodefensor_object(self, queryset=None):
        """
        Returns the object the view is displaying.

        By default this requires `self.atendimentodefensor_queryset` and a `pk` or `slug` argument
        in the URLconf, but subclasses can override this to return any object.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_atendimentodefensor_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.atendimentodefensor_pk_url_kwarg, None)
        slug = self.kwargs.get(self.atendimentodefensor_slug_url_kwarg, None)
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        if slug is not None and (pk is None or self.atendimentodefensor_query_pk_and_slug):
            slug_field = self.get_atendimentodefensor_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        # If none of those are defined, it's an error.
        if pk is None and slug is None:
            raise AttributeError("Generic detail view %s must be called with "
                                 "either an object pk or a slug."
                                 % self.__class__.__name__)

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj

    def get_atendimentodefensor_queryset(self):
        """
        Return the `QuerySet` that will be used to look up the object.

        Note that this method is called by the default implementation of
        `get_atendimentodefensor_object` and may not be called if `get_atendimentodefensor_object` is overridden.
        """
        if self.atendimentodefensor_queryset is None:
            if self.atendimentodefensor_model:
                return self.atendimentodefensor_model.objects.select_related('atendimento_ptr')
            else:
                raise ImproperlyConfigured(
                    "%(cls)s is missing a QuerySet. Define "
                    "%(cls)s.atendimentodefensor_model, %(cls)s.atendimentodefensor_queryset, or override "
                    "%(cls)s.get_atendimentodefensor_queryset()." % {
                        'cls': self.__class__.__name__
                    }
                )
        return self.atendimentodefensor_queryset.all()

    def get_atendimentodefensor_slug_field(self):
        """
        Get the name of a slug field to be used to look up by slug.
        """
        return self.atendimentodefensor_slug_field

    def get_atendimentodefensor_context_object_name(self, obj):
        """
        Get the name to use for the object.
        """
        if self.atendimentodefensor_context_object_name:
            return self.atendimentodefensor_context_object_name
        elif isinstance(obj, models.Model):
            return obj._meta.model_name
        else:
            return None

    def get_context_data(self, **kwargs):
        """
        Insert the single object into the context dict.
        """
        context = super(SingleAtendimentoDefensorObjectMixin, self).get_context_data(**kwargs)
        if self.atendimentodefensor_object:
            context['atendimentodefensor_object'] = self.atendimentodefensor_object
            context_object_name = self.get_atendimentodefensor_context_object_name(self.atendimentodefensor_object)
            if context_object_name:
                context[context_object_name] = self.atendimentodefensor_object
        context.update(kwargs)
        return context
