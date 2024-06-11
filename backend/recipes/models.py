from django.db import models

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.constants import MIN_COOKING_TIME, TEXT_FIELD_LENGTH
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=TEXT_FIELD_LENGTH,
        verbose_name='Tag'
    )
    slug = models.SlugField(unique=True, verbose_name='Slug')

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'tags'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=TEXT_FIELD_LENGTH,
        verbose_name='Ingredient'
    )
    measurement_unit = models.CharField


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Author'
    )
    name = models.CharField(
        max_length=TEXT_FIELD_LENGTH,
        verbose_name='Title'
    )
    text = models.TextField(verbose_name='Recipes description')
    image = models.ImageField(null=False, blank=False, upload_to="images/")
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ingredients'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Tags'
    )
    cooking_time = models.IntegerField(
        validators=(MinValueValidator(MIN_COOKING_TIME)),
        verbose_name='Review rating'
    )

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ('name',)
        default_related_name = 'recipes'

    def str(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='featured_recipe',
        on_delete=models.CASCADE
    )
