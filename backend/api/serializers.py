import base64
import re

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.mixins import AmountMixin, ChosenMixin
from foodgramm_backend.constants import (
    EMAIL_FIELD_LENGTH,
    MAX_COOKING_TIME,
    MAX_INGREDIENT_AMOUNT,
    MIN_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT,
    RECIPE_VALIDATION_MESSAGES,
    USERNAME_LENGTH
)
from recipes.models import (
    AmountIngredient, Favorite, Ingredient,
    ShopingList, Subscription, Recipe, Tag
)
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
    username = serializers.CharField(
        max_length=USERNAME_LENGTH,
        required=True
    )
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )

    def validate_email(self, value):
        existing_user = User.objects.filter(email=value).first()
        if existing_user and existing_user.email == self.initial_data.get(
            'email'
        ):
            raise serializers.ValidationError(
                'Почтовый адрес уже зарегистрирован!'
            )
        return value

    def validate_username(self, value):
        existing_user = User.objects.filter(username=value).first()
        if existing_user and existing_user.username == self.initial_data.get(
            'username'
        ):
            raise serializers.ValidationError('Логин уже занят!')
        if not re.match(r'^[\w.@+-]+$', value) or value == 'me':
            raise serializers.ValidationError('Невалидный логин')
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор данных модели User.

    Используется при get-запросах.
    """

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if not user or user.is_anonymous:
            return False
        if user == obj:
            return False
        return user.subscriptions.filter(author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class AmountIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для промежуточной модели между Recipe и Ingredient."""

    id = serializers.IntegerField(source='ingredient.id',)
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = AmountIngredient
        fields = ('id', 'amount', 'measurement_unit', 'name')


class AddIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор данных для добавления ингредиентов в рецепт."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        min_value=MIN_INGREDIENT_AMOUNT,
        max_value=MAX_INGREDIENT_AMOUNT
    )

    class Meta:
        model = AmountIngredient
        fields = ('id', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer, ChosenMixin):
    """Сериализатор данных модели Recipe для GET-запросов."""

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
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME,
        max_value=MAX_COOKING_TIME
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = ('author',)

    def get_is_favorited(self, obj):
        return self.get_chosen_recipe(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.get_chosen_recipe(obj, ShopingList)


class RecipeSerializer(serializers.ModelSerializer, AmountMixin, ChosenMixin):
    """Сериализатор данных для создания рецепта."""

    ingredients = AddIngredientSerializer(
        required=True,
        many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time',
            'author', 'is_favorited', 'is_in_shopping_cart'
        )

    def validate(self, data):
        unique_data: set[int] = set()
        for model in ('ingredients', 'tags'):
            if not data.get(model):
                raise ValidationError(
                    RECIPE_VALIDATION_MESSAGES['EMPTY'][model]
                )
            for obj in data.get(model):
                if isinstance(obj, dict):
                    obj = obj.get('id')
                if obj.id in unique_data:
                    raise ValidationError(
                        RECIPE_VALIDATION_MESSAGES['NOT_UNIQUE'][model]
                    )
                unique_data.add(obj.id)
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.update_or_create_ingredient(
            recipe=recipe, ingredients=ingredients
        )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        self.update_or_create_ingredient(
            recipe=instance, ingredients=ingredients
        )
        instance.tags.clear()
        instance.tags.set(tags)
        super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        return RecipeGetSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data

    def get_is_favorited(self, obj):
        return self.get_chosen_recipe(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.get_chosen_recipe(obj, ShopingList)


class RecipeMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Subscriber."""

    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeMiniSerializer(
        read_only=True,
        many=True,
        source='author.recipe'
    )
    recipes_count = serializers.SerializerMethodField()
    avatar = Base64ImageField(
        source='author.avatar',
        required=False,
        allow_null=True
    )

    class Meta:
        model = Subscription
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def validate(self, data):
        if self.context['user'] == self.context['author']:
            raise ValidationError('Нельзя подписаться на самого себя!')
        if self.context['is_subscription_exist']:
            raise ValidationError('Вы уже подписаны на данного автора')
        return data

    def get_is_subscribed(self, obj):
        if not obj.user:
            return False
        return obj.user.subscriptions.filter(author=obj.author).exists()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        recipes_limit = self.context['request'].GET.get('recipes_limit')
        if recipes_limit:
            representation['recipes'] = representation[
                'recipes'
            ][:int(recipes_limit)]
        return representation

    def get_recipes_count(self, obj):
        return obj.author.recipe.count()


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор модели User для смены пароля."""

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
                {'current_password': 'Неправильный пароль'}
            )
        if data.get('current_password') == data.get('new_password'):
            raise ValidationError(
                {'new_password': 'Новый пароль совпадает с предыдущим!'}
            )
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance
