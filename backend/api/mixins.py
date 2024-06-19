from typing import Any
from django_filters.rest_framework import DjangoFilterBackend

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status, viewsets
from rest_framework.exceptions import ValidationError

from users.models import User

class ChosenRecipeMixin(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='recipe', read_only=True)
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True
    )
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')


class IngridientTagMixin(viewsets.ModelViewSet):
    http_allowed_methods = ['get',]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
