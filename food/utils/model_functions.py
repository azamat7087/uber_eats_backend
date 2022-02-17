from food.utils.translator import translate_text
from django.utils.text import slugify
import food.models as azt_models
from django.db import IntegrityError
import transliterate
import random
import json


def get_hex_id():
    obj_id = random.randint(1, 4294967295)
    hex_id = str(hex(obj_id))[2:]
    return hex_id


def set_id():
    while True:
        try:
            obj_id = get_hex_id()
            azt_models.UsedID.objects.create(used=obj_id)
            return obj_id
        except IntegrityError:
            pass


def config_md_text(text):
    return str(text).replace("\n", "<br>")


def gen_slug(s):
    if has_cyr(s):
        s = transliterate.translit(s, reversed=True)
    new_slug = slugify(s, allow_unicode=True)

    return new_slug + "-" + str(random.randint(0, 1000))


def has_cyr(s):
    lower = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
    return lower.intersection(s.lower()) != set()


def set_markdown_fields(new_obj, old_object):
    setattr(new_obj, "content_md", old_object.content_md)
    return new_obj


def set_lang_versions(obj, cls, attrs_list):
    translations = [(obj.locale.code, obj.id), ]
    obj_list = [obj]
    for lang in azt_models.Locale.objects.exclude(code=obj.locale.code):
        new_obj = cls.objects.get(id=obj.id)
        new_obj.id = set_id()
        if hasattr(new_obj, "slug"):
            new_obj.slug = gen_slug(new_obj.title)
        new_obj.locale = lang
        for field in cls._meta.get_fields():
            if (field.name in attrs_list) and (field.name not in cls.SPECIAL_O2M_FIELDS):
                if field.name == "content_md" and lang != obj.locale:
                    new_obj = set_markdown_fields(new_obj, obj)
                else:
                    setattr(new_obj, field.name,
                            translate_text(obj, obj.__getattribute__("locale").code, lang.code, field.name, True))

        translations.append((lang.code, new_obj.id))
        obj_list.append(new_obj)

    for new_obj in obj_list:
        new_obj.translations = json.dumps(translations)
        new_obj.save()


def get_object_locals(obj, cls):
    obj_locals = []
    for code, id in json.loads(obj.translations):
        obj_locals.append(cls.objects.get(id=id))
    return obj_locals


def is_valid_attrs(field):
    return field.name != "locale" and field.name != "slug" and field.name != "id"


def copy_m2m_fields(old_object, cls):  # Вызывается в администраторской панели в методе сохранения полей связи
    for code, id in json.loads(old_object.translations):
        other_obj = cls.objects.get(id=id)
        for field in cls._meta.get_fields():
            if field.many_to_many and field.name not in cls.SPECIAL_M2M_FIELDS:
                m2m = other_obj.__getattribute__(field.name)
                old_m2m = old_object.__getattribute__(field.name)
                m2m.add(*old_m2m.all())

