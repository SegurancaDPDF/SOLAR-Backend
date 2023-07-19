# third-party
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

# django
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from django.db import transaction

# project
from core.serializers import GenericSerializer
from defensor.models import Atuacao
from defensor.serializers import AtuacaoDocumentoSerializer
# application
from . import models
from . import validators
from nucleo.nucleo.serializers import NucleoSerializer
from comarca.serializers import PredioSerializer
from core.models import TipoEvento
from processo.processo.models import ProcessoPoloDestinatario
from procapi_client.models import Competencia


class AreaSerializer(serializers.ModelSerializer):  # serializa o modelo Area em formato JSON
    class Meta:
        model = models.Area
        fields = '__all__'


class BairroSerializer(serializers.ModelSerializer):  # serializa o modelo Bairro em formato JSON
    class Meta:
        model = models.Bairro
        fields = (
            'id',
            'nome',
            'municipio'
        )


class CartorioSerializer(serializers.ModelSerializer):  # serializa o modelo Cartorio em formato JSON.
    class Meta:
        model = models.Cartorio
        fields = '__all__'


class ComarcaSerializer(serializers.ModelSerializer):  # serializa o modelo Comarca em formato JSON
    filhos = serializers.SerializerMethodField()

    class Meta:
        model = models.Comarca
        fields = '__all__'

    @swagger_serializer_method(serializer_or_field=GenericSerializer(many=True))
    def get_filhos(self, obj):
        incluir_filhos = self.context['request'].query_params.get('incluir_filhos')

        if incluir_filhos == 'true':
            filhos = obj.comarca_set.all()
            return GenericSerializer(instance=filhos, many=True).data
        else:
            return list()


class ComarcaBasicSerializer(serializers.ModelSerializer):  # serializa o modelo Comarca em formato JSON
    class Meta:
        model = models.Comarca
        fields = ('id', 'nome', 'coordenadoria')


class DefensoriaAtuacaoSerializer(serializers.ModelSerializer):  # serializa o modelo Atuacao em formato JSON
    defensor = GenericSerializer()
    documento = AtuacaoDocumentoSerializer()

    class Meta:
        model = Atuacao
        fields = ('id', 'tipo', 'data_inicial', 'data_final', 'defensor', 'titular', 'documento')


class DefensoriaSerializer(serializers.ModelSerializer):  # serializa o modelo Defensoria em formato JSON.
    comarca = ComarcaBasicSerializer()
    categorias_de_agendas = serializers.SerializerMethodField()
    atuacoes = serializers.SerializerMethodField()
    nucleo = NucleoSerializer()
    predio = PredioSerializer()
    tipos_eventos = serializers.PrimaryKeyRelatedField(
        queryset=TipoEvento.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = models.Defensoria
        fields = ('id', 'codigo', 'nome', 'comarca', 'grau',
                  'pode_vincular_processo_judicial', 'atuacao', 'atuacoes',
                  'categorias_de_agendas', 'nucleo', 'tipos_eventos',
                  'telefone',
                  'email', 'cabecalho_documento',
                  'rodape_documento', 'predio'
                  )
    # verificam os parâmetros de consulta incluir_categorias e incluir_atuacoes e retornam os dados correspondentes
    #  se os parâmetros forem 'true', caso contrário, retornam listas vazias

    @swagger_serializer_method(serializer_or_field=DefensoriaAtuacaoSerializer(many=True))
    def get_atuacoes(self, obj):
        incluir_atuacoes = self.context['request'].query_params.get('incluir_atuacoes')

        if incluir_atuacoes == 'true':
            atuacoes = obj.all_atuacoes.all()  # DefensorViewSet.Prefetch
            return DefensoriaAtuacaoSerializer(instance=atuacoes, many=True).data
        else:
            return list()

    @swagger_serializer_method(serializer_or_field=GenericSerializer(many=True))
    def get_categorias_de_agendas(self, obj):
        incluir_categorias = self.context['request'].query_params.get('incluir_categorias')

        if incluir_categorias == 'true':
            atuacoes = obj.categorias_de_agendas.all()
            return GenericSerializer(instance=atuacoes, many=True).data
        else:
            return list()


class DefensoriaBasicoSerializer(serializers.ModelSerializer):  # serializa o modelo Defensoria em formato JSON

    class Meta:
        model = models.Defensoria
        fields = ('id', 'codigo', 'nome', 'atuacao', 'pode_vincular_processo_judicial')


class DefensoriaDetailSerializer(DefensoriaSerializer):  # serializa o modelo DefensoriaEtiqueta em formato JSON
    nucleo = GenericSerializer()
    predio = GenericSerializer()
    areas = GenericSerializer(many=True)
    categorias_de_agendas = GenericSerializer(many=True)

    class Meta:
        model = models.Defensoria
        fields = '__all__'


class DefensoriaEtiquetaSerializer(serializers.ModelSerializer):  # serializa o model DefensoriaEtiqueta em formato JSON
    nome = serializers.CharField(source='__str__')

    class Meta:
        model = models.DefensoriaEtiqueta
        fields = '__all__'


class DocumentoSerializer(serializers.ModelSerializer):  # serializa o modelo Documento em formato JSON
    class Meta:
        model = models.Documento
        fields = '__all__'
        ref_name = 'ContribDocumento'


class MunicipioSerializer(serializers.ModelSerializer):  # serializa o modelo Municipio em formato JSON
    class Meta:
        model = models.Municipio
        fields = '__all__'


class EtiquetaSerializer(serializers.ModelSerializer):  # serializa o modelo Etiqueta em formato JSON
    defensoria = serializers.IntegerField(write_only=True, required=False)
    defensorias = serializers.SerializerMethodField()

    class Meta:
        model = models.Etiqueta
        fields = '__all__'

    def create(self, validated_data):
        # cria a etiqueta e, se houver uma defensoria associada, também cria ou atualiza a relação entre a etiqueta e
        # a defensoria na tabela DefensoriaEtiqueta.
        defensoria = validated_data.pop('defensoria', None)

        etiqueta = super().create(validated_data)

        if defensoria:
            models.DefensoriaEtiqueta.objects.update_or_create(
                etiqueta=etiqueta,
                defensoria_id=defensoria,
                defaults={
                    'desativado_por': None,
                    'desativado_em': None,
                }
            )

        return etiqueta

    def get_defensorias(self, obj):
        return obj.defensoriaetiqueta_set.ativos().values_list('defensoria', flat=True)


class AtualizacaoSerializer(serializers.ModelSerializer):  # serializa o modelo Atualizacao em formato JSON
    class Meta:
        model = models.Atualizacao
        fields = '__all__'


class CEPSerializer(serializers.ModelSerializer):  # serializa o modelo CEP em formato JSON
    class Meta:
        model = models.CEP
        fields = '__all__'


class UsuarioSerializer(serializers.ModelSerializer):  # serializa o modelo User (usuário) em formato JSON

    class Meta:
        ref_name = "contrib.User"
        model = User
        fields = ('id', 'username', 'email', 'is_superuser')

    def get_nome(self, obj):  # retorna o nome completo do usuario
        return obj.get_full_name()


class CargoSerializer(serializers.ModelSerializer):  # serializa o modelo Cargo em formato JSON
    class Meta:
        model = models.Cargo
        fields = '__all__'


class DefensoriaTipoEventoSerializer(serializers.ModelSerializer):  # serializa o model defensoriatipoevento em JSON
    class Meta:
        model = models.DefensoriaTipoEvento
        fields = '__all__'


class VaraSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Vara
        fields = '__all__'


class DefensoriaVaraSerializer(serializers.ModelSerializer):
    defensoria = GenericSerializer()
    vara = GenericSerializer()
    cadastrado_por = UsuarioSerializer()

    class Meta:
        model = models.DefensoriaVara
        fields = '__all__'


class DefensoriaVaraCreateSerializer(serializers.ModelSerializer):
    distribuir_por_polo = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=False,
        required=False,
        queryset=ProcessoPoloDestinatario.objects.all()
    )
    distribuir_por_competencia = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=False,
        required=False,
        queryset=Competencia.objects.all()
    )

    class Meta:
        model = models.DefensoriaVara
        fields = '__all__'

    def create(self, validated_data):

        polos = validated_data.pop('distribuir_por_polo', None)
        competencias = validated_data.pop('distribuir_por_competencia', None)

        instance = super().create(validated_data)

        if polos:
            instance.distribuir_por_polo.set(polos)

        if competencias:
            instance.distribuir_por_competencia.set(competencias)

        return instance

    def update(self, instance, validated_data):

        polos = validated_data.pop('distribuir_por_polo', None)
        competencias = validated_data.pop('distribuir_por_competencia', None)

        instance = super().update(instance, validated_data)

        if polos:
            instance.distribuir_por_polo.set(polos)

        if competencias:
            instance.distribuir_por_competencia.set(competencias)

        return instance


class DeficienciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Deficiencia
        fields = '__all__'


class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Endereco
        fields = '__all__'
        ref_name = 'ContribEndereco'


class EnderecoHistoricoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EnderecoHistorico
        fields = '__all__'


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Estado
        fields = '__all__'


class HistoricoLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.HistoricoLogin
        fields = '__all__'


class IdentidadeGeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IdentidadeGenero
        fields = '__all__'


class MenuExtraSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MenuExtra
        fields = '__all__'


class OrientacaoSexualSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrientacaoSexual
        fields = '__all__'


class PapelSerializer(serializers.ModelSerializer):
    grupos = GenericSerializer(read_only=True, many=True)

    class Meta:
        model = models.Papel
        fields = '__all__'


class PaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pais
        fields = '__all__'


class SalarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Salario
        fields = '__all__'


class ServidorSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source='usuario.username',
        required=True,
    )
    password = serializers.CharField(
        source='usuario.password',
        write_only=True,
        required=False,
        validators=[validate_password])
    email = serializers.EmailField(
        source='usuario.email',
        required=True,
        )
    nome = serializers.CharField(required=True)
    cpf = serializers.CharField(
        validators=[
            validators.validate_CPF,
            RegexValidator(r'^[0-9]*$'),
            ])
    ativo = serializers.BooleanField()
    uso_interno = serializers.BooleanField(required=False)

    comarca = GenericSerializer()
    papel = GenericSerializer()
    usuario = UsuarioSerializer(required=False)

    class Meta:
        ref_name = "Servidor_v2"
        model = models.Servidor
        exclude = ['data_nascimento', 'data_atualizacao', 'telefones']

    def validate(self, data):

        user = data.get('usuario')
        if user:
            email = user['email']
            username = user['username']
            if self.context['request'].method == 'PATCH':
                usuario_id = models.Servidor.objects.get(cpf=data.get('cpf')).usuario_id
                if email and username:

                    existe_email = User.objects.filter(pk=usuario_id, email=email)
                    if not existe_email:
                        existe_email_outro_usuario = User.objects.filter(email=email).exists()
                        if existe_email_outro_usuario:
                            raise serializers.ValidationError({'email': [f"o email {email} está sendo usado"]})
                if username:
                    existe_username = User.objects.filter(pk=usuario_id, username=username)
                    if not existe_username:
                        existe_username_outro_servidor = User.objects.filter(username=username).exists()
                        if existe_username_outro_servidor:
                            raise serializers.ValidationError({'username': ["username ou nome de usuário ja existe"]})

                existe_cpf = models.Servidor.objects.filter(pk=self.instance.id, cpf=data.get('cpf')).exists()

                if not existe_cpf:
                    existe_cpf_outro_servidor = models.Servidor.objects.filter(cpf=data.get('cpf')).exists()
                    if existe_cpf_outro_servidor:
                        raise serializers.ValidationError({'cpf': ["cpf já existe no cadastro"]})

            elif self.context['request'].method == 'POST':
                existe_email = User.objects.filter(email=email).exists()
                if existe_email:
                    raise serializers.ValidationError({'email': ["Já existe este email"]})
                existe_username = User.objects.filter(username=username).exists()
                if existe_username:
                    raise serializers.ValidationError({'username': ["Já existe este username"]})

                existe_cpf = models.Servidor.objects.filter(cpf=data.get('cpf')).exists()
                if existe_cpf:
                    raise serializers.ValidationError({'cpf': ["cpf já existe no cadastro"]})

        return data

    @transaction.atomic
    def create(self, validated_data):

        nomes = validated_data['nome'].split()

        data_usuario = validated_data.pop('usuario')
        data_usuario['first_name'] = nomes[0]
        data_usuario['last_name'] = ' '.join(nomes[1:])

        usuario = User.objects.create(**data_usuario)
        usuario.set_password(data_usuario['password'])
        validated_data['usuario'] = usuario
        papel = models.Papel.objects.get(pk=validated_data['papel']['id'])
        validated_data['papel'] = papel
        comarca = models.Comarca.objects.get(pk=validated_data['comarca']['id'])
        validated_data['comarca'] = comarca
        return self.Meta.model.objects.create(**validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        from cacheops import invalidate_model

        instance = models.Servidor.objects.get(pk=instance.id)
        # instance.cpf = validated_data['cpf']
        instance = models.Servidor.objects.get(pk=instance.id)
        if validated_data.get('usuario'):
            if validated_data['usuario']['email']:
                usuario = User.objects.get(pk=instance.usuario.id)
                usuario.email = validated_data['usuario']['email']
                validated_data['usuario'] = usuario
        instance.nome = validated_data['nome']
        instance.matricula = validated_data['matricula']
        instance.ativo = validated_data['ativo']
        papel = models.Papel.objects.get(pk=validated_data['papel']['id'])
        validated_data['papel'] = papel
        instance.papel = papel
        instance.sexo = validated_data['sexo']
        comarca = models.Comarca.objects.get(pk=validated_data['comarca']['id'])
        validated_data['comarca'] = comarca
        instance.comarca = comarca
        models.Servidor.objects.filter(pk=instance.id).update(**validated_data)
        invalidate_model(models.Servidor)
        return instance


class TelefoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Telefone
        fields = '__all__'
        ref_name = 'ContribTelefone'
