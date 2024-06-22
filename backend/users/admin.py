from django.contrib import admin

from recipes.models import Recipe
from users.models import User


class RecipeInline(admin.StackedInline):
    model = Recipe
    extra = 0


@admin.register(User)
class User(admin.ModelAdmin):
    inlines = (RecipeInline,)
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'role',
        'email',
        'avatar'
    )
    search_fields = ('user', 'email',)
    list_filter = ('role',)
    list_editable = (
        'role',
    )
