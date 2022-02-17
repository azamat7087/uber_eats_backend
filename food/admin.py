from django.contrib.auth.admin import UserAdmin
import food.utils.admin_utils as azt_admin_utils
import food.models as azt_models
import food.utils.model_functions as azt_functions
import food.utils.model_utils as azt_model_utils
from django.contrib import admin


class LocaleAdmin(azt_admin_utils.LocaleBaseAdmin):
    list_display = ('id', 'name', 'code', 'iso', 'date_of_update', 'date_of_add')
    search_fields = ('id', 'name', 'code', 'iso')
    readonly_fields = ('id', 'date_of_update', 'date_of_add',)
    ordering = ('-date_of_update',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(azt_models.Locale, LocaleAdmin)


class TimeRangesAdmin(azt_admin_utils.MultiLangAdmin):

    list_display = ('id', 'min_time', 'max_time', 'time_unit', 'locale', 'date_of_update', 'date_of_add')
    search_fields = ('id', 'time_unit', 'min_time', 'max_time')
    readonly_fields = ('id', 'date_of_update', 'date_of_add', 'translations')
    ordering = ('-date_of_update',)
    filter_horizontal = ()
    autocomplete_fields = ()
    list_filter = ('locale', )
    fieldsets = ()


admin.site.register(azt_models.TimeRanges, TimeRangesAdmin)


class RestaurantsAdmin(azt_admin_utils.MultiLangAdmin):

    list_display = ('id', 'name', 'index', 'locale', 'date_of_update', 'date_of_add')
    search_fields = ('id', 'name',)
    readonly_fields = ('id', 'date_of_update', 'date_of_add', 'translations')
    ordering = ('-date_of_update',)
    filter_horizontal = ()
    autocomplete_fields = ()
    list_filter = ('locale', )
    fieldsets = ()

    def save_related(self, request, form, formsets, change):
        super(RestaurantsAdmin, self).save_related(request, form, formsets, change)
        cls = azt_models.Restaurants
        old_object = cls.objects.get(id=form.instance.id)
        azt_functions.copy_m2m_fields(old_object, cls)
        old_object.get_other_lang_of_time_ranges()


admin.site.register(azt_models.Restaurants, RestaurantsAdmin)


class CategoriesAdmin(azt_admin_utils.MultiLangAdmin):

    list_display = ('id', 'name', 'restaurant', 'index', 'locale', 'date_of_update', 'date_of_add')
    search_fields = ('id', 'name',)
    readonly_fields = ('id', 'date_of_update', 'date_of_add', 'translations')
    ordering = ('-date_of_update',)
    filter_horizontal = ()
    autocomplete_fields = ('restaurant',)
    list_filter = ('locale', 'restaurant')
    fieldsets = ()

    def save_related(self, request, form, formsets, change):
        super(CategoriesAdmin, self).save_related(request, form, formsets, change)
        cls = azt_models.Categories
        old_object = cls.objects.get(id=form.instance.id)
        azt_functions.copy_m2m_fields(old_object, cls)
        old_object.get_other_lang_of_restaurants()


admin.site.register(azt_models.Categories, CategoriesAdmin)


class FoodAdmin(azt_admin_utils.MultiLangAdmin):

    list_display = ('id', 'name', 'description', 'price', 'category', 'index', 'locale', 'date_of_update', 'date_of_add')
    search_fields = ('id', 'name',)
    readonly_fields = ('id', 'date_of_update', 'date_of_add', 'translations')
    ordering = ('-date_of_update',)
    filter_horizontal = ()
    autocomplete_fields = ('category', )
    list_filter = ('locale', 'category', 'category__restaurant')
    fieldsets = ()

    def save_related(self, request, form, formsets, change):
        super(FoodAdmin, self).save_related(request, form, formsets, change)
        cls = azt_models.Food
        old_object = cls.objects.get(id=form.instance.id)
        azt_functions.copy_m2m_fields(old_object, cls)
        old_object.get_other_lang_of_categories()

admin.site.register(azt_models.Food, FoodAdmin)



