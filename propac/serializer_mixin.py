class SerializerMixin:

    def get_serializer_class(self):
        try:
            return self.serializer_classes[self.action]
        except (AttributeError, KeyError):
            return super().get_serializer_class()
