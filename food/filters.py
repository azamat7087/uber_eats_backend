from django_filters import CharFilter
from django_filters.rest_framework import FilterSet


class LanguageFilterSet(FilterSet):
    lang = CharFilter(field_name="locale__code")

    class Meta:
        fields = ['lang']


class RestaurantsFilterSet(LanguageFilterSet):
    tag = CharFilter(field_name="tags__id")

    class Meta:
        fields = ['tag']


class CategoriesFilterSet(LanguageFilterSet):
    restaurant = CharFilter(field_name="restaurant__id")

    class Meta:
        fields = ['restaurant']


class ProductsFilterSet(LanguageFilterSet):
    category = CharFilter(field_name="category__id")
    restaurant = CharFilter(field_name="category__restaurant__id")

    class Meta:
        fields = ['category', 'restaurant']
