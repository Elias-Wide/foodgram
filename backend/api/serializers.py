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

from api.constants import (
    EMAIL_FIELD_LENGTH , MIN_COOKING_TIME, MIN_INGREDIENT_AMOUNT, USERNAME_LENGTH
)
from recipes.models import Ingredient, AmountIngredient, ShopingList, Subscription, Recipe, Tag
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
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class AmountIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(min_value=MIN_INGREDIENT_AMOUNT)

    class Meta:
        model = AmountIngredient
        fields = ('id', 'amount')


class AmountIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = AmountIngredient
        fields = ('id', 'amount', 'measurement_unit', 'name')


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserProfileSerializer(read_only=True)
    ingredients = AmountIngredientSerializer(
        source='recipe_ingredients',
        many=True
        )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    name = serializers.CharField()
    image = Base64ImageField()
    text = serializers.CharField()
    cooking_time = serializers.IntegerField(min_value=MIN_COOKING_TIME)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = ('author',)

    def get_is_favorited(self, obj):
        return False

    def get_is_in_shopping_cart(self, obj):
        return False

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = AmountIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time', 'author')

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            AmountIngredient.objects.update_or_create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        for ingredient in ingredients:
            AmountIngredient.objects.update_or_create(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        instance.tags.clear()
        instance.tags.set(tags)
        super().update(instance, validated_data)
        return instance

class RecipeSubSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)

class ShopingListSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='recipe', read_only=True)
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True
    )
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = ShopingList
        fields = ('id', 'name', 'image', 'cooking_time',)


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='recipe', read_only=True)
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True
    )
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = ShopingList
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubscribeSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

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


