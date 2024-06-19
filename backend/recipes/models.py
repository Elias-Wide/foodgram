from django.db import models

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.constants import MEASUREMENT_UNIT_LENTH, TEXT_FIELD_LENGTH
from recipes.constants import MIN_COOKING_TIME, MIN_INGREDIENT_AMOUNT
from users.models import User, User

class Tag(models.Model):
    name = models.CharField(
        max_length=TEXT_FIELD_LENGTH,
        verbose_name='Название тэга'
    )
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'тэги'
        ordering = ('name',)
        default_related_name = 'tag'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=TEXT_FIELD_LENGTH,
        verbose_name='Ингредиент'
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_LENTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'ингредиенты'
        ordering = ('name',)
        default_related_name = 'ingredient'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        max_length=TEXT_FIELD_LENGTH,
        verbose_name='Название рецепта'
    )
    text = models.TextField(verbose_name='Recipes description')
    image = models.ImageField(blank=False, upload_to="recipe_images/")
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги  '
    )
    cooking_time = models.IntegerField(
        validators=(MinValueValidator(MIN_COOKING_TIME),),
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ('pub_date',)
        default_related_name = 'recipe'

    def str(self):
        return self.text

class AmountIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        verbose_name='Название рецепта',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(MIN_INGREDIENT_AMOUNT),),
        verbose_name='Количество ингредиента',
    )

    class Meta:
        verbose_name = 'Cостав рецепта'
        verbose_name_plural = 'Состав рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='Количество ингредиента')]


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        related_name='subscriber',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
    )
    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='уникальные подписки')]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='user',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe',
        on_delete=models.CASCADE
    )
    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'
            ),
        ]


class ShopingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'списки покупок'
        default_related_name = 'shoping_list'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shoping_list'
            )
        ]

    def __str__(self):
        return f'{self.recipe}'
