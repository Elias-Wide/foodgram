API_VERSION: str = 'v1/'
EMAIL_FIELD_LENGTH: int = 254
TEXT_FIELD_LENGTH: int = 255
USERNAME_LENGTH: int = 150
MEASUREMENT_UNIT_LENTH: int = 10
MIN_COOKING_TIME: int = 1
MIN_INGREDIENT_AMOUNT: int = 1
ERROR_MESSAGES: dict = {
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
