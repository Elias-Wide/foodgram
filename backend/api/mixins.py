from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, viewsets


class IngridientTagMixin(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    permission_classes = (permissions.AllowAny, )
