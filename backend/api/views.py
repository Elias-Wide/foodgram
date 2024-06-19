from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination 
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView

from api import serializers
from api.constants import ERROR_MESSAGES
from recipes.models import  Ingredient, Recipe, ShopingList, Subscription, Tag
from users.models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.SignUpSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.SignUpSerializer
        if self.request.method == 'GET':
            return serializers.UserProfileSerializer

    @action(
        ['GET'],
        detail=False,
        name='current_user',
        permission_classes=[IsAuthenticated,]
    )
    def me(self, request):
        serializer = serializers.UserProfileSerializer(
            request.user,
            context={'request': request}
        )
        return Response(data=serializer.data)

    @action(
        ['POST', 'DELETE'],
        detail=True,
        name='subscribe',
        permission_classes=[IsAuthenticated,]
    )
    def subscribe(self, request, pk):
        author = get_object_or_404(User, id=self.kwargs.get('pk'))
        user = self.request.user
        if request.method == 'POST':
            serializer = serializers.SubscribeSerializer(
                data=request.data,
                context={"author": author, "user": user,},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, author=author)
            return Response({'Подписка успешно создана': serializer.data},
                status=status.HTTP_201_CREATED
            )
        if Subscription.objects.filter(
            user=user, author=author
        ).exists():
            Subscription.objects.get(user=user, author=author).delete()
            return Response("Успешная отписка",
                            status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"errors": "Вы не подписаны на данного автора"},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        ['GET'],
        detail=False,
        name='Получить собственные подписки',
        permission_classes=[IsAuthenticated,],
    )
    def subscriptions(self, request):
        paginate_subs = self.paginate_queryset(Subscription.objects.filter(user=self.request.user))
        serializer = serializers.SubscribeSerializer(
            paginate_subs,
            many=True,
            context={'request': request}
            )
        return self.get_paginated_response(serializer.data)

    @action(
        ['POST'],
        detail=False,
        permission_classes=[IsAuthenticated,]
    )
    def set_password(self, request):
        serializer = serializers.SetPasswordSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(
            instance=self.request.user,
            validated_data=serializer.validated_data
        )
        return Response(
            'Пароль успешно изменен',
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        ['PUT', 'DELETE'],
        detail=False,
        url_path='me/avatar',
        permission_classes=[IsAuthenticated,]
    )
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = serializers.UserProfileSerializer(
                user,
                data=request.data,
                partial=True,
                context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"avatar": serializer.data['avatar']},
                    status=status.HTTP_200_OK
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        user.avatar = None
        user.save()
        return Response(
            "Аватар успешно удален",
            status=status.HTTP_204_NO_CONTENT
        )


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    http_allowed_methods = ['get',]
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    http_allowed_methods = ['get',]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_allowed_methods = ['get', 'post', 'delete', 'patch']

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return serializers.RecipeGetSerializer
        return serializers.RecipeSerializer

    @action(
        ['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated,],
        serializer_class = serializers.ShopingListSerializer
    )
    def shopping_cart(self, request, pk):
        return add_delete_choosen_recipe(
            request=request,
            recipe=get_object_or_404(Recipe, id=pk),
            serializer_class=self.serializer_class,
            model=self.serializer_class.Meta.model,
            error_key="SHOP_LIST"
        )

    @action(
        ['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated,],
        serializer_class = serializers.FavoriteSerializer
    )
    def favorite(self, request, pk):
        return add_delete_choosen_recipe(
            request=request,
            recipe=get_object_or_404(Recipe, id=pk),
            serializer_class=self.serializer_class,
            model=self.serializer_class.Meta.model,
            error_key="FAVORITE"
        )


def add_delete_choosen_recipe(request, recipe, serializer_class, model, error_key):
    """
    Объединенная функция добавления/удаления рецепта
    Выбранный рецепт может быть удален или добавлен либо в список покупок,
    либо в избранное, в зависимости от используемого представления.
    Выводится соотвествующее запросу и действию сообщение.
    """
    recipe_in_shoping_cart = model.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists()
    if request.method == "POST":
        serializer = serializer_class(
            data=request.data,
            context={'user': request.user, 'recipe': recipe}
        )
        if recipe_in_shoping_cart:
            return Response(
                ERROR_MESSAGES['ALREADY_IN'][error_key],
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, recipe=recipe)
        return Response(
            {ERROR_MESSAGES['SUCCES_ADD'][error_key]: serializer.data},
            status=status.HTTP_201_CREATED
        )
    if not recipe_in_shoping_cart:
        return Response(
            ERROR_MESSAGES['NOT_EXIST'][error_key],
            status=status.HTTP_400_BAD_REQUEST
        )
    model.objects.get(user=request.user,recipe=recipe).delete()
    return Response(
        ERROR_MESSAGES['SUCCES_DELETE'][error_key],
        status=status.HTTP_204_NO_CONTENT
    )