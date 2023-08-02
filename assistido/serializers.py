# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

from django.db import transaction
from rest_framework import serializers

from contrib.models import GeneroPessoa, Endereco, Telefone
from assistido import models


class FiliacaoSerializer(serializers.ModelSerializer):
    tipo_str = serializers.SerializerMethodField()

    class Meta:
        model = models.Filiacao
        exclude = ('pessoa_assistida', 'nome_soundex', 'nome_norm')

    def get_tipo_str(self, obj):
        a = obj.LISTA_TIPO[obj.tipo][1]
        return a


class PessoaAderiuLunaChatbotSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    nome = serializers.CharField(read_only=True)
    aderiu_luna_chatbot = serializers.BooleanField(read_only=True)

    def update(self, instance, validated_data):
        instance.aderiu_luna_chatbot = validated_data.get('aderiu_luna_chatbot', instance.aderiu_luna_chatbot)
        instance.save()
        return instance


class RendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Renda
        exclude = ('pessoa',)


class MoradiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Moradia
        fields = '__all__'


class PessoaPatrimonialSerializer(serializers.ModelSerializer):
    tipo_str = serializers.SerializerMethodField()
    grupo_str = serializers.SerializerMethodField()

    class Meta:
        model = models.Patrimonial
        exclude = (
            'pessoa',
            'cadastrado_em',
            'modificado_em',
            'desativado_em',
            'cadastrado_por',
            'modificado_por',
            'desativado_por',
        )

    def get_tipo_str(self, obj):
        a = obj.tipo.nome
        return a

    def get_grupo_str(self, obj):
        a = dict(obj.tipo.LISTA_GRUPO)[obj.tipo.grupo]
        return a


class PessoaDependenteSerializer(serializers.ModelSerializer):
    situacao_str = serializers.SerializerMethodField()
    parentesco_str = serializers.SerializerMethodField()

    class Meta:
        model = models.Dependente
        exclude = (
            'pessoa',
            'cadastrado_em',
            'modificado_em',
            'desativado_em',
            'cadastrado_por',
            'modificado_por',
            'desativado_por',
        )

    def get_situacao_str(self, obj):
        a = dict(obj.situacao.LISTA_SITUACAO)[obj.situacao]
        return a

    def get_parentesco_str(self, obj):
        a = dict(obj.parentesco.GRAU_PARENTESCO)[obj.parentesco]
        return a


class PessoaAssistidaSerializer(serializers.ModelSerializer):
    from api.api_v1.serializers import EnderecoSerializer, TelefoneSerializer
    filiacoes = FiliacaoSerializer(many=True)
    telefones = TelefoneSerializer(many=True)
    enderecos = EnderecoSerializer(many=True)
    patrimonios = PessoaPatrimonialSerializer(many=True, required=False)
    dependentes = PessoaDependenteSerializer(many=True, required=False)
    renda = RendaSerializer()
    moradia = MoradiaSerializer()
    hipossuficiente = serializers.SerializerMethodField()

    class Meta:
        model = models.PessoaAssistida
        exclude = (
            'automatico',
            'nome_norm',
            'nome_soundex',
            'tipo_cadastro',
        )
        read_only_fields = [
            'cadastrado_em',
            'modificado_em',
            'desativado_em',
            'cadastrado_por',
            'modificado_por',
            'desativado_por',
        ]

    def get_hipossuficiente(self, obj):
        return obj.avaliar()

    @transaction.atomic
    def create(self, validated_data):

        if ('cpf' in validated_data and validated_data['cpf'] and
                models.PessoaAssistida.objects.filter(cpf=validated_data['cpf']).exists()):
            raise serializers.ValidationError({'cpf': ['CPF/CNPJ já cadastrado']})

        # Converte sexo em gênero
        if 'sexo' in validated_data and 'genero' not in validated_data:
            sexo = validated_data.pop('sexo')
            validated_data['genero'] = GeneroPessoa.objects.filter(id=sexo).first()

        # Extrai dados das tabelas auxiliares
        telefones = validated_data.pop('telefones')
        filiacoes = validated_data.pop('filiacoes')
        enderecos = validated_data.pop('enderecos')
        patrimonios = validated_data.pop('patrimonios', [])
        dependentes = validated_data.pop('dependentes', [])
        renda = validated_data.pop('renda')
        moradia = validated_data.pop('moradia')

        # Grava dados da moradia
        if moradia != dict():
            estrutura = moradia.pop('estrutura', [])
            moradia = models.Moradia.objects.create(**moradia)
            moradia.estrutura.set(estrutura)
            validated_data['moradia'] = moradia

        # Grava dados do assistido
        pessoa = super(PessoaAssistidaSerializer, self).create(validated_data)

        # Grava dados dos endereços e vincula ao assistido
        for endereco in enderecos:
            endereco_salvo = Endereco.objects.create(**endereco)
            pessoa.enderecos.add(endereco_salvo)

        # Grava dados dos telefones e vincula ao assistido
        for telefone in telefones:
            telefone_salvo = Telefone.objects.create(**telefone)
            pessoa.telefones.add(telefone_salvo)

        # Grava dados das filiações
        for filiacao in filiacoes:
            filiacao['pessoa_assistida'] = pessoa
            models.Filiacao.objects.create(**filiacao)

        # Grava dados dos patrimônios
        for patrimonio in patrimonios:
            patrimonio['pessoa'] = pessoa
            models.Patrimonial.objects.create(**patrimonio)

        # Grava dados dos dependentes
        for dependente in dependentes:
            dependente['pessoa'] = pessoa
            models.Dependente.objects.create(**dependente)

        # Grava dados da renda
        renda['pessoa'] = pessoa
        models.Renda.objects.create(**renda)

        return pessoa

    @transaction.atomic
    def update(self, instance, validated_data):

        if ('cpf' in validated_data and validated_data['cpf'] != instance.cpf and
                models.PessoaAssistida.objects.filter(cpf=validated_data['cpf']).exists()):
            raise serializers.ValidationError({'cpf': ['CPF/CNPJ já cadastrado']})

        # Converte sexo em gênero
        if 'sexo' in validated_data and 'genero' not in validated_data:
            sexo = validated_data.pop('sexo')
            validated_data['genero'] = GeneroPessoa.objects.filter(id=sexo).first()

        # Extrai dados das tabelas auxiliares
        telefones = validated_data.pop('telefones', [])
        filiacoes = validated_data.pop('filiacoes', [])
        enderecos = validated_data.pop('enderecos', [])
        patrimonios = validated_data.pop('patrimonios', [])
        dependentes = validated_data.pop('dependentes', [])
        renda = validated_data.pop('renda', {})
        moradia = validated_data.pop('moradia', {})

        # Grava dados da renda
        if renda != dict():
            renda['id'] = instance.renda.id
            renda['pessoa_id'] = instance.id
            renda = models.Renda(**renda)
            renda.save()
            validated_data['renda'] = renda

        # Grava dados da moradia
        if moradia != dict():
            estrutura = moradia.pop('estrutura', [])
            moradia['id'] = self.initial_data['moradia'].get('id')
            moradia = models.Moradia(**moradia)
            moradia.save()
            moradia.estrutura.set(estrutura)
            validated_data['moradia'] = moradia

        # Grava dados do assistido
        instance.modificado_por = self.context['request'].user
        pessoa = super(PessoaAssistidaSerializer, self).update(instance, validated_data)

        # Grava dados dos endereços e vincula ao assistido
        for index, endereco in enumerate(enderecos):
            endereco['id'] = self.initial_data['enderecos'][index].get('id')
            endereco_salvo = Endereco(**endereco)
            endereco_salvo.save()
            pessoa.enderecos.add(endereco_salvo)

        # Grava dados dos telefones e vincula ao assistido
        for index, telefone in enumerate(telefones):
            telefone['id'] = self.initial_data['telefones'][index].get('id')
            telefone_salvo = Telefone(**telefone)
            telefone_salvo.save()
            pessoa.telefones.add(telefone_salvo)

        # Grava dados das filiações
        for index, filiacao in enumerate(filiacoes):
            models.Filiacao.objects.update_or_create(
                id=self.initial_data['filiacoes'][index].get('id'),
                pessoa_assistida=pessoa,
                defaults=filiacao
            )

        # Grava dados dos patrimônios
        for index, patrimonio in enumerate(patrimonios):
            models.Patrimonial.objects.update_or_create(
                id=self.initial_data['patrimonios'][index].get('id'),
                pessoa=pessoa,
                defaults=patrimonio
            )

        # Grava dados dos dependentes
        for index, dependente in enumerate(dependentes):
            models.Dependente.objects.update_or_create(
                id=self.initial_data['dependentes'][index].get('id'),
                pessoa=pessoa,
                defaults=dependente
            )

        return pessoa


class PatrimonialTipoSerializer(serializers.ModelSerializer):
    grupo_nome = serializers.SerializerMethodField()

    class Meta:
        model = models.PatrimonialTipo
        fields = '__all__'

    def get_grupo_nome(self, obj):
        return obj.get_grupo_display()


class PatrimonialSerializer(serializers.ModelSerializer):
    tipo = PatrimonialTipoSerializer()

    class Meta:
        model = models.Patrimonial
        fields = ('id', 'eh_bem_familia', 'pessoa', 'tipo', 'descricao', 'valor')


class SituacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Situacao
        fields = '__all__'


class TipoRendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TipoRenda

        exclude = (
            'cadastrado_em',
            'modificado_em',
            'desativado_em',
            'cadastrado_por',
            'modificado_por',
            'desativado_por',
        )


class DependenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Dependente
        fields = '__all__'


class DocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Documento
        fields = '__all__'
        ref_name = 'DefensorDocumento'


class EstruturaMoradiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EstruturaMoradia
        fields = '__all__'


class ImovelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Imovel
        fields = '__all__'


class MovelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Movel
        fields = '__all__'


class PatrimonioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Patrimonio
        fields = '__all__'


class PerfilCamposObrigatoriosSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PerfilCamposObrigatorios
        fields = '__all__'


class ProfissaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profissao
        fields = '__all__'


class SemoventeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Semovente
        fields = '__all__'
