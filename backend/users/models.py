from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CheckConstraint, Q

from users.constants import (
    EMAIL_FIELD_LENGTH,
    ROLE_FIELD_LENGTH,
    USER_ROLE_CHOICES,
    USER_ROLE_NAME,
    ADMIN_ROLE_NAME
)


class User(AbstractUser):
    email = models.EmailField(
        max_length=EMAIL_FIELD_LENGTH,
        unique=True,
        null=False,
        blank=False,
        verbose_name='Email addres'
    )
    role = models.CharField(
        max_length=ROLE_FIELD_LENGTH,
        choices=USER_ROLE_CHOICES,
        default=USER_ROLE_NAME,
        verbose_name='Role'
    )
    bio = models.TextField(
        null=True,
        blank=True,
        verbose_name='User biography'
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        constraints = [
            CheckConstraint(
                check=~Q(username='me'), name='username_me_banned_word'
            )
        ]
        ordering = ('email',)

    def __str__(self) -> str:
        return self.username

    @property
    def is_admin(self):
        return self.role == ADMIN_ROLE_NAME
