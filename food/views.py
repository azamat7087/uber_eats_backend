import json

from rest_framework.parsers import FileUploadParser, JSONParser, MultiPartParser, FormParser
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, generics, status
import food.utils.view_utils as azt_view_utils
import food.serializers as azt_serializers
from rest_framework.response import Response
import food.filters as azt_filters
import food.models as azt_models
from django.conf import settings
# Create your views here.


class RestaurantsView(azt_view_utils.ViewSerializerMixin, azt_view_utils.AztViewMixin,):
    queryset = azt_models.Restaurants.objects.all()
    serializer_class = azt_serializers.RestaurantsSerializer
    list_serializer_class = azt_serializers.RestaurantsListSerializer
    model = 'Restaurants'
    obj = 'restaurant'
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    permission_classes = [permissions.AllowAny, ]
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    lookup_field = "id"
    filter_class = azt_filters.RestaurantsFilterSet
    filter_fields = []
    search_fields = ['name', 'categories__name', 'categories__food__name', "categories__food__description"]
    ordering_fields = ['id', 'date_of_update', "date_of_add"]


class CategoriesView(azt_view_utils.ViewSerializerMixin, azt_view_utils.AztViewMixin,):
    queryset = azt_models.Categories.objects.all()
    serializer_class = azt_serializers.CategoriesSerializer
    list_serializer_class = azt_serializers.CategoriesListSerializer
    model = 'Categories'
    obj = 'category'
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    permission_classes = [permissions.AllowAny, ]
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    lookup_field = "id"
    filter_class = azt_filters.CategoriesFilterSet
    filter_fields = []
    search_fields = ['name', 'restaurant__name', 'food__name', 'food__description']
    ordering_fields = ['id', 'date_of_update', "date_of_add"]


class ProductsView(azt_view_utils.ViewSerializerMixin, azt_view_utils.AztViewMixin,):
    queryset = azt_models.Categories.objects.all()
    serializer_class = azt_serializers.CategoriesSerializer
    list_serializer_class = azt_serializers.CategoriesListSerializer
    model = 'Categories'
    obj = 'category'
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    permission_classes = [permissions.AllowAny, ]
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    lookup_field = "id"
    filter_class = azt_filters.CategoriesFilterSet
    filter_fields = []
    search_fields = ['name', 'restaurant__name', 'food__name', 'food__description']
    ordering_fields = ['id', 'date_of_update', "date_of_add"]
