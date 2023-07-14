from django.db.models import QuerySet
from rest_framework.serializers import Serializer


class QueryParameterSerializerMixin:
    """
    Mixin usado para escolher de forma dinâmica, baseado no query parameter 'serializer',
    o serializer que será utilizado para retornar os dados. O objetivo principal é limitar a quantidade
    de campos retornados e evitar joins desnecessários que muitas vezes acabam comprometendo a performance
    do endpoint.

    Attributes
    ----------
    serializer_classes : dict = None

    Methods
    -------
    get_serializer_class(self) -> Serializer
    """

    serializer_classes = None

    def get_serializer_class(self) -> Serializer:
        try:
            serializer = self.request.query_params.get("serializer")
            if serializer:
                return self.serializer_classes[serializer]
            return super().get_serializer_class()
        except (AttributeError, KeyError):
            return super().get_serializer_class()


class QuerysetSerializerMixin:
    """
    Mixin usado para escolher de forma dinâmica, baseado no query parameter 'serializer',
    o queryset que será utilizado para retornar os dados. O objetivo principal é limitar a quantidade
    de campos retornados e evitar joins desnecessários que muitas vezes acabam comprometendo a performance.
    como usar:
    - Definir na viewset o atributo 'queryset_serializer' com um dicionário contendo a chave para o queryset desejado.
    - O nome da chave definida deve casar com a chave definida no 'serializer_classes', caso contrário o efeito desejado
      poderá não ser atingido.

    Attributes
    ----------
    queryset_serializer : dict = None

    Methods
    -------
    get_queryset(self, *args, **kwargs) -> QuerySet
    """

    queryset_serializer = None

    def get_queryset(self, *args, **kwargs) -> QuerySet:
        try:
            queryset = self.request.query_params.get("serializer")
            if queryset:
                return self.queryset_serializer.get(queryset)
            return super().get_queryset(*args, **kwargs)
        except (AttributeError, KeyError):
            return super().get_queryset(*args, **kwargs)
