from django.http import HttpResponse

from recipes.models import AmountIngredient


def shopping_list_txt(user):
    text_shop_list = 'Список покупок \n\n'
    measurement_unit = {}
    ingridient_amount = {}
    ingridients = AmountIngredient.objects.filter(
        recipe__shoping_list__user=user
    ).values(
        'ingredient__name', 'ingredient__measurement_unit', 'amount')
    for ingredient in ingridients:
        if ingredient['ingredient__name'] in ingridient_amount:
            ingridient_amount[
                ingredient['ingredient__name']
            ] += ingredient['amount']
        else:
            measurement_unit[
                ingredient['ingredient__name']
            ] = ingredient['ingredient__measurement_unit']
            ingridient_amount[
                ingredient['ingredient__name']
            ] = ingredient['amount']
    for ingredient, amount in ingridient_amount .items():
        text_shop_list += (
            f'{ingredient} - {amount}'
            f'{measurement_unit[ingredient]}\n'
        )
    response = HttpResponse(text_shop_list, content_type='text/plain')
    response[
        'Content-Disposition'
    ] = 'attachment; filename="shopping_list.txt"'
    return response
