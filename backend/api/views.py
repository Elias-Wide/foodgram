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
from recipes.models import  Ingredient, Recipe, Subscription, Tag
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
        name='Получить данные авторизованного пользователя',
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
        name='Создание/удаление подписки',
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
            serializer = serializers.UserProfileSerializer(user, data=request.data, partial=True, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return Response({"avatar": serializer.data['avatar']}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user.avatar = None
        user.save()
        return Response("Аватар успешно удален")
        

        

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
    pass