# third-party
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# django
from django.contrib.auth.models import User


# classe de serialização para o modelo de usuário padrão do Django
class UsuarioSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'nome']

    def get_nome(self, obj):
        # obtém o nome completo do usuário usando o método get_full_name() do modelo de usuário
        return obj.get_full_name()


# serialização personalizada para autenticação de tokens
class CustomAuthTokenSerializer(AuthTokenSerializer):
    user = UsuarioSerializer(read_only=True)


# serialização personalizada para obtenção de pares de tokens
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    user = UsuarioSerializer(read_only=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UsuarioSerializer(self.user).data

        return data
