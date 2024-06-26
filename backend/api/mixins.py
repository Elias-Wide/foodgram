from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, viewsets

from recipes.models import AmountIngredient


class IngridientTagMixin(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    permission_classes = (permissions.AllowAny, )


class AmountMixin():
    def update_or_create_ingredient(self, recipe, ingredients) -> None:
        recipe.ingredients.clear()
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_list.append(
                AmountIngredient(
                    recipe=recipe,
                    ingredient=ingredient['id'],
                    amount=ingredient['amount']
                )
            )
        AmountIngredient.objects.bulk_create(ingredient_list)


class ChosenMixin():

    def get_chosen_recipe(self, obj, model) -> bool:
        """
        Метод получения статуса выбранного рецепта.

        Используется для избранного и списка покупок.
        """
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return model.objects.filter(
            user=user,
            recipe=obj
        ).exists()
