import food.models as azt_models
from django.contrib import admin
from functools import partial
import django.apps
import json


class LocaleBaseAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        obj.save()

        for model in django.apps.apps.get_models():
            if "food.models" in str(model):
                try:
                    if model.has_lang_object():
                        model.add_new_lang(model, obj)
                except AttributeError:
                    pass

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self.delete_model(request, obj)

    def delete_model(self, request, obj):
        for model in django.apps.apps.get_models():
            if "food.models" in str(model):
                try:
                    if model.has_lang_object():
                        model.delete_lang(model, obj)
                except AttributeError:
                    pass
        obj.delete()


class MultiLangAdmin(admin.ModelAdmin):

    @staticmethod
    def field_is_valid(obj, field):
        return field.name not in obj.SPECIAL_O2M_FIELDS and field.name not in obj.SPECIAL_M2M_FIELDS \
               and field.name not in obj.TRANSLATED_FIELDS and field.uniq

    def delete_queryset(self, request, queryset):
        index = 0
        while len(queryset):
            if hasattr(queryset[index], 'locale'):
                objs = [queryset[index].__class__.objects.get(id=obj_id) for code, obj_id
                        in dict(json.loads(queryset[index].translations)).items()]
                for d_obj in objs:
                    queryset = queryset.exclude(id=d_obj.id)
                    d_obj.delete()

    def delete_model(self, request, obj):
        objs = dict(json.loads(obj.translations))
        for code, obj_id in objs.items():
            (getattr(azt_models, f"{obj.__class__.__name__}").objects.get(id=obj_id)).delete()

    def get_form(self, request, obj=None, **kwargs):
        kwargs['formfield_callback'] = partial(self.formfield_for_dbfield, request=request, obj=obj)
        return super().get_form(request, obj, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if kwargs['obj']:
            if db_field.name not in kwargs['obj'].SPECIAL_M2M_FIELDS:
                kwargs.pop('obj', None)
        else:
            kwargs.pop('obj', None)
        return super().formfield_for_dbfield(db_field, **kwargs)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        obj = kwargs.pop('obj', None)

        if obj:
            if obj.locale:
                if db_field.name in obj.SPECIAL_M2M_FIELDS:
                    qs = kwargs.get('queryset', db_field.remote_field.model.objects)
                    kwargs['queryset'] = qs.select_related().filter(locale=obj.locale)

        return super().formfield_for_manytomany(db_field, request=request, **kwargs)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.translations:
            for another_obj in [obj.__class__.objects.get(id=obj_id) for name, obj_id in json.loads(obj.translations)]:
                if not obj.id == another_obj.id:
                    for general_field in obj.GENERAL_FIELDS:

                        try:
                            setattr(another_obj, general_field, getattr(obj, general_field))
                        except TypeError:
                            m2m = another_obj.__getattribute__(general_field)
                            old_m2m = obj.__getattribute__(general_field)
                            m2m.add(*old_m2m.all())
                    another_obj.save()
