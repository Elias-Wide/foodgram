import base64
import re
import secrets
import string

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from api.constants import EMAIL_FIELD_LENGTH ,USERNAME_LENGTH
from recipes.models import Subscription, Recipe, Tag
from users.models import User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=EMAIL_FIELD_LENGTH,
        required=True
    )
    username = serializers.CharField(max_length=USERNAME_LENGTH, required=True)
    password = serializers.CharField(write_only=True, required=True,
    )


    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')

    def validate_email(self, value):
        existing_user = User.objects.filter(email=value).first()
        if existing_user and existing_user.email == self.initial_data.get(
            'email'
        ):
            raise serializers.ValidationError('Почтовый адрес уже зарегистрирован!')
        return value

    def validate_username(self, value):
        existing_user = User.objects.filter(username=value).first()
        if existing_user and existing_user.email == self.initial_data.get(
            'email'
        ):
            raise serializers.ValidationError('Логин занят!')
        if not re.match(r'^[\w.@+-]+$', value) or value == 'me':
            raise serializers.ValidationError('Невалидный логин')
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        if self.context.get('request').user.is_anonymous:
            return False
        user = self.context.get('request').user
        if user == obj:
            return False
        return Subscription.objects.filter(
            user=user,
            author=obj
        ).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    author = UserProfileSerializer(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    name = serializers.CharField()
    text = serializers.CharField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author')
        read_only_fields = ('author',)


class RecipeSubSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image',)


class SubscribeSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    # avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def validate(self, data):
        user = self.context.get('user')
        author = self.context.get('author')
        if user == author:
            raise ValidationError(
                "Нельзя подписаться на самого себя!",
                code=status.HTTP_400_BAD_REQUEST)
        if Subscription.objects.filter(
            author=author,
            user=user
        ).exists():
            raise ValidationError(
                "Вы уже подписаны на данного автора!",
                code=status.HTTP_400_BAD_REQUEST
            )
        return data


    def get_is_subscribed(self, obj):
        if not obj.user:
            return False
        return Subscription.objects.filter(
                user=obj.user,
                author=obj.author).exists()


    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.author)
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        return RecipeSubSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    class Meta:
        model = User
        write_only = ('new_password', 'current_password')

    def validate(self, data):
        if not self.context['request'].user.check_password(
            data.get('current_password')
        ):
            raise ValidationError(
                {"current_password": "Неправильный пароль"}
            )
        if data.get('current_password') == data.get('new_password'):
            raise ValidationError(
                {"new_password": "Новый пароль совпадает с предыдущим!"}
            )
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance


class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar')
