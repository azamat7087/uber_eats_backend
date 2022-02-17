from django_filters import CharFilter
from django_filters.rest_framework import FilterSet


class LanguageFilterSet(FilterSet):
    lang = CharFilter(field_name="locale__code")

    class Meta:
        fields = ['lang']


class RestaurantsFilterSet(LanguageFilterSet):
    pass


class CategoriesFilterSet(LanguageFilterSet):
    restaurant = CharFilter(field_name="restaurant__id")

    class Meta:
        fields = ['restaurant']

