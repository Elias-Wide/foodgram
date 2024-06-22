from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


from users.constants import (
    EMAIL_FIELD_LENGTH,
    FIRST_LAST_NAME_LENGTH,
    ROLE_FIELD_LENGTH,
    USER_ROLE_CHOICES,
    USERNAME_LENGTH,
    USER_ROLE_NAME,
    ADMIN_ROLE_NAME
)


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        max_length=EMAIL_FIELD_LENGTH,
        verbose_name='Электронная почта'
    )
    username = models.CharField(
        verbose_name='Логин', max_length=USERNAME_LENGTH, unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя', max_length=FIRST_LAST_NAME_LENGTH
    )
    last_name = models.CharField(
        verbose_name='Фамилия', max_length=FIRST_LAST_NAME_LENGTH
    )
    role = models.CharField(
        max_length=ROLE_FIELD_LENGTH,
        choices=USER_ROLE_CHOICES,
        default=USER_ROLE_NAME,
        verbose_name='Роль'
    )
    avatar = models.ImageField(
        upload_to='users_avatar/',
        null=True,
        verbose_name='Аватар',
        default=None
    )
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']
    USERNAME_FIELD = 'email'

    class Meta:
        default_related_name = 'user'
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'профили пользователей'

    def __str__(self) -> str:
        return self.username

    @property
    def is_admin(self):
        return self.role == ADMIN_ROLE_NAME

    @receiver(post_save, sender='users.User')
    def set_admin_role_for_superuser(sender, instance, created, **kwargs):
        if created:
            if instance.is_superuser:
                instance.role = ADMIN_ROLE_NAME
                instance.save()
