from django.contrib.auth import admin
from django.contrib import admin, auth

from recipes.models import  Ingredient, Recipe, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('slug', )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('measurement_unit',)
    list_filter = ('measurement_unit',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'text',
        'cooking_time'
    )
    search_fields = ('ingredients', 'tags', 'name')
    list_filter = ('ingredients', 'cooking_time', 'tags',)
    list_editable = ('cooking_time',)


admin.site.empty_value_display = 'Не задано'
admin.site.unregister(auth.models.Group)
