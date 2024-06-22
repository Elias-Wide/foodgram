EMAIL_FIELD_LENGTH: int = 254
MEASUREMENT_UNIT_LENTH: int = 10
MIN_COOKING_TIME: int = 1
MIN_INGREDIENT_AMOUNT: int = 1
MAX_LENTH_IN_ADMIN: int = 20
TEXT_FIELD_LENGTH: int = 255
USERNAME_LENGTH: int = 150

ERROR_MESSAGES: dict[dict[str]] = {
    'ALREADY_IN': {
        "FAVORITE": 'Рецепт уже добавлен в избранное!',
        'SHOP_LIST': 'Рецепт уже добавлен в список покупок!'
    },
    "SUCCES_ADD": {
        'FAVORITE': 'Рецепт успешно добавлен в избранное.',
        'SHOP_LIST': 'Рецепт успешно добавлен в список покупок.'
    },
    "NOT_EXIST": {
        'FAVORITE': {'errors': 'Рецепт не добавлен в избранное!'},
        'SHOP_LIST': {'errors': 'Рецепт не добавлен в список покупок!'}
    },
    "SUCCES_DELETE": {
        'FAVORITE': 'Рецепт успешно удален из избранного.',
        'SHOP_LIST': 'Рецепт успешно удален из списка покупок.'
    },
}
RECIPE_VALIDATION_MESSAGES: dict[dict[str]] = {
    'EMPTY': {
        'ingredients': 'Необходимо добавить ингредиенты',
        'tags': 'Необходимо указать тэги'
    },
    'NOT_UNIQUE': {
        'ingredients': 'Ингредиенты повторяются!',
        'tags': 'Укажите только уникальные тэги!'
    },
}
