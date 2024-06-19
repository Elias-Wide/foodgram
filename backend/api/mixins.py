import base64
import re
import secrets
import string

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from api.constants import (
    EMAIL_FIELD_LENGTH , MIN_COOKING_TIME, MIN_INGREDIENT_AMOUNT, USERNAME_LENGTH, ERROR_MESSAGES
)
from recipes.models import AmountIngredient, Favorite, Ingredient, ShopingList, Subscription, Recipe, Tag
from users.models import User

class ChosenRecipeMixin(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='recipe', read_only=True)
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True
    )
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

