FIRST_LAST_NAME_LENGTH: int = 150
USERNAME_LENGTH: int = 150
EMAIL_FIELD_LENGTH: int = 254
ROLE_FIELD_LENGTH: int = 20

USER_ROLE_NAME: str = 'user'
ADMIN_ROLE_NAME: str = 'admin'
USER_ROLE_CHOICES = tuple(
    (user_role, user_role.capitalize()) for user_role in (
        USER_ROLE_NAME,
        ADMIN_ROLE_NAME,
    )
)