from rest_framework import serializers
import food.models as azt_models
import json


class LocaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = azt_models.Locale
        exclude = ("date_of_add", "date_of_update")


class SlugMixin:
    pass
    # @staticmethod
    # def get_translations(obj):
    #
    #     try:
    #         translations = json.loads(obj.translations)
    #     except AttributeError:
    #         translations = obj['translations']
    #
    #     for lang in translations:
    #         lang[1] = __class__.Meta.model.objects.get(id=lang[1]).slug
    #
    #     return translations


class AztLocaleSerializerMixin(serializers.ModelSerializer):
    locale = LocaleSerializer(many=False)
    translations = serializers.SerializerMethodField()

    @staticmethod
    def get_translations(obj):
        try:
            return json.loads(obj.translations)
        except AttributeError:
            return obj['translations']


class TimeRangeSerializer(AztLocaleSerializerMixin):
    locale = None
    translations = None

    class Meta:
        model = azt_models.TimeRanges
        exclude = ("date_of_add", "date_of_update", "locale", "translations", "id")


class ProductsListSerializer(AztLocaleSerializerMixin):
    class Meta:
        model = azt_models.Products
        fields = ("id", "image", "name", "description", "slug", "index", "locale")


class ProductsSerializer(AztLocaleSerializerMixin, SlugMixin):
    class Meta:
        model = azt_models.Products
        exclude = ("id", "date_of_add", "date_of_update", )


class CategoriesListSerializer(AztLocaleSerializerMixin):
    class Meta:
        model = azt_models.Categories
        fields = ("id", "name", "slug", "index", "locale")


class CategoriesSerializer(AztLocaleSerializerMixin, SlugMixin):
    products = ProductsListSerializer(many=True)

    class Meta:
        model = azt_models.Categories
        exclude = ("date_of_add", "date_of_update", )


class TagsSerializer(AztLocaleSerializerMixin):
    locale = None
    translations = None

    class Meta:
        model = azt_models.Tags
        exclude = ("locale", "translations", "date_of_add", "date_of_update",)


class RestaurantsSerializer(AztLocaleSerializerMixin, SlugMixin):
    time_range = TimeRangeSerializer(many=False)
    categories = CategoriesListSerializer(many=True)
    tags = TagsSerializer(many=True)

    class Meta:
        model = azt_models.Restaurants
        exclude = ("date_of_add", "date_of_update", "card_image")


class RestaurantsListSerializer(AztLocaleSerializerMixin):
    time_range = TimeRangeSerializer(many=False)
    tags = TagsSerializer(many=True)

    class Meta:
        model = azt_models.Restaurants
        fields = ("id", "name", "slug", "tags", "time_range", "card_image", "index", "locale", "translations")


