from django.contrib import admin

from users.models import User


@admin.register(User)
class User(admin.ModelAdmin):
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