import json

from django.db import models
import food.models as azt_models
import food.utils.model_functions as azt_functions
import food.utils.translator as azt_translator


class AztBaseModel(models.Model):
    id = models.CharField(max_length=8, primary_key=True, unique=True, null=False)
    date_of_update = models.DateTimeField(auto_now=True)
    date_of_add = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = azt_functions.set_id()
        super().save(*args, **kwargs)

    def set_index(self):
        if not self.index and self.__class__.objects.last():
            self.index = self.__class__.objects.last().index + 1
        elif not self.__class__.objects.last():
            self.index = 1


class AztLocaleModel:
    translations = None
    locale = None
    SPECIAL_M2M_FIELDS = []
    SPECIAL_O2M_FIELDS = []
    TRANSLATED_FIELDS = []
    GENERAL_FIELDS = []

    @classmethod
    def has_lang_object(cls):
        if cls.objects.last().translations:
            return True

    @staticmethod
    def delete_lang(cls, new_obj):
        locale_code = new_obj.code
        locale = azt_models.Locale.objects.get(code=locale_code)
        for obj in cls.objects.exclude(locale=locale):
            translations = json.loads(obj.translations)
            for i in translations:
                if i[0] == locale_code:
                    translations.remove(i)
            obj.translations = json.dumps(translations)
            obj.save()

    @staticmethod
    def add_new_lang(model, new_obj):
        locale_code = new_obj.code
        locale = azt_models.Locale.objects.get(code=locale_code)
        objects = model.objects.filter(locale=azt_models.Locale.objects.get(code="en"))

        for obj in objects:
            new_obj = model.objects.get(id=obj.id)
            new_obj.id = azt_functions.set_id()
            new_obj.locale = locale
            translations = json.loads(obj.translations)
            translations.append([f'{locale_code}', f'{new_obj.id}'])
            new_obj.translations = json.dumps(translations)

            for field in obj._meta.get_fields():
                if field.name in obj.TRANSLATED_FIELDS:
                    setattr(new_obj, field.name,
                            azt_translator.translate_text(obj, "en", locale_code, field.name, True))

            for code, id in json.loads(obj.translations):
                another_obj = model.objects.get(id=id)
                another_obj.translations = new_obj.translations
                another_obj.save()

        if hasattr(new_obj, "slug"):
            new_obj.slug = azt_functions.gen_slug(new_obj.title)

        new_obj.save()

    def set_translations(self):
        if not self.translations:
            azt_functions.set_lang_versions(self.__class__.objects.get(id=self.id), self.__class__,
                                            self.TRANSLATED_FIELDS)

    def set_index(self):
        if not self.index and self.__class__.objects.filter(locale=self.locale).last():
            self.index = self.__class__.objects.filter(locale=self.locale).order_by('-index').first().index + 1
        elif not self.__class__.objects.last():
            self.index = 1
