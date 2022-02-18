import json
import random

from django.db import models
from django.core.validators import MinValueValidator
from food.utils import model_functions as azt_functions
from food.utils import model_utils as azt_models
# Create your models here.


class UsedID(models.Model):
    used = models.CharField(max_length=8, unique=True)

    def __str__(self):
        return self.used


class Locale(models.Model):
    id = models.CharField(max_length=8, primary_key=True, unique=True, null=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=2, unique=True)
    iso = models.CharField(max_length=15, unique=True)
    date_of_update = models.DateTimeField(auto_now=True)
    date_of_add = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}, code:{}'.format(self.name, self.code)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = azt_functions.set_id()
        super(Locale, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Locale"
        ordering = ['-date_of_update']


class TimeRanges(azt_models.AztLocaleModel, models.Model):
    TRANSLATED_FIELDS = ['time_unit']
    id = models.CharField(max_length=8, primary_key=True, unique=True, null=False)
    min_time = models.IntegerField(validators=[MinValueValidator(0)])
    max_time = models.IntegerField(validators=[MinValueValidator(0)])
    time_unit = models.CharField(max_length=30, default="min")
    locale = models.ForeignKey('Locale', on_delete=models.CASCADE, related_name="time_range", null=True)
    translations = models.CharField(max_length=1000, blank=True)
    date_of_update = models.DateTimeField(auto_now=True)
    date_of_add = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.min_time}-{self.max_time} {self.time_unit}"

    def save(self, *args, **kwargs):

        if not self.id:
            self.id = azt_functions.set_id()
        super(TimeRanges, self).save(*args, **kwargs)

        self.set_translations()

    class Meta:
        verbose_name_plural = "TimeRanges"
        ordering = ['-date_of_update']


class Tags(azt_models.AztLocaleModel, models.Model):
    SPECIAL_M2M_FIELDS = []
    SPECIAL_O2M_FIELDS = []
    TRANSLATED_FIELDS = ['name']
    GENERAL_FIELDS = ['translations']

    id = models.CharField(max_length=8, primary_key=True, unique=True, null=False)
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    locale = models.ForeignKey('Locale', on_delete=models.CASCADE, related_name="tags", )
    translations = models.CharField(max_length=1000, blank=True)
    date_of_update = models.DateTimeField(auto_now=True)
    date_of_add = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        self.set_index()

        if not self.id:
            self.id = azt_functions.set_id()
        super(Tags, self).save(*args, **kwargs)

        self.set_translations()

    class Meta:
        verbose_name_plural = "Tags"
        ordering = ['-date_of_update']


class Restaurants(azt_models.AztLocaleModel, models.Model):
    SPECIAL_M2M_FIELDS = ['tags']
    SPECIAL_O2M_FIELDS = ['time_range']
    TRANSLATED_FIELDS = ['name']
    GENERAL_FIELDS = ['main_image', 'index', 'card_image', 'translations']

    id = models.CharField(max_length=8, primary_key=True, unique=True, null=False)
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    slug = models.CharField(max_length=100, null=False, unique=True, blank=True)
    tags = models.ManyToManyField(Tags, blank=True, related_name="restaurants")
    main_image = models.ImageField(upload_to="images/restaurants/main/", null=True)
    card_image = models.ImageField(upload_to="images/restaurants/card/", null=True)
    time_range = models.ForeignKey('TimeRanges', on_delete=models.CASCADE, related_name='restaurants', null=False)
    index = models.PositiveIntegerField(blank=True, validators=[MinValueValidator(1)], )
    locale = models.ForeignKey('Locale', on_delete=models.CASCADE, related_name="restaurants", )
    translations = models.CharField(max_length=1000, blank=True)
    date_of_update = models.DateTimeField(auto_now=True)
    date_of_add = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_other_lang_of_time_ranges(self):
        restaurants = dict(json.loads(self.translations))
        for code, id in json.loads(self.time_range.translations):
            restaurant = Restaurants.objects.get(id=restaurants[code])
            restaurant.time_range = TimeRanges.objects.get(id=id)
            restaurant.save()

    def get_other_lang_of_tags(self):
        restaurants = dict(json.loads(self.translations))
        for tag in self.tags.all():
            for code, id in json.loads(tag.translations):
                restaurant = Restaurants.objects.get(id=restaurants[code])
                restaurant.tags.add(Tags.objects.get(id=id))
                restaurant.save()

    def save(self, *args, **kwargs):

        self.set_index()

        if not self.id:
            self.id = azt_functions.set_id()
            self.slug = azt_functions.gen_slug(self.name)[0:100]
        super(Restaurants, self).save(*args, **kwargs)

        self.set_translations()

    def set_index(self):
        if not self.index and self.__class__.objects.last():
            self.index = self.__class__.objects.last().index + 1
        elif not self.__class__.objects.last():
            self.index = 1

    class Meta:
        verbose_name_plural = "Restaurants"
        ordering = ['date_of_update']


class Categories(azt_models.AztLocaleModel, models.Model):
    SPECIAL_O2M_FIELDS = ['restaurant']
    TRANSLATED_FIELDS = ['name']
    GENERAL_FIELDS = ['index', 'translations', ]

    id = models.CharField(max_length=8, primary_key=True, unique=True, null=False)
    name = models.CharField(max_length=100, null=False, blank=False, )
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE, related_name="categories")
    slug = models.CharField(max_length=100, null=False, unique=True, blank=True)
    index = models.PositiveIntegerField(blank=True, validators=[MinValueValidator(1)], )
    locale = models.ForeignKey('Locale', on_delete=models.CASCADE, related_name="categories", )
    translations = models.CharField(max_length=1000, blank=True)
    date_of_update = models.DateTimeField(auto_now=True)
    date_of_add = models.DateTimeField(auto_now_add=True)

    def get_other_lang_of_restaurants(self):
        categories = dict(json.loads(self.translations))
        for code, id in json.loads(self.restaurant.translations):
            category = Categories.objects.get(id=categories[code])
            category.restaurant = Restaurants.objects.get(id=id)
            category.save()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        self.set_index()

        if not self.id:
            self.id = azt_functions.set_id()
            self.slug = azt_functions.gen_slug(self.name)[0:100]

        super(Categories, self).save(*args, **kwargs)

        self.set_translations()

    def set_index(self):
        if not self.index and self.__class__.objects.last():
            self.index = self.__class__.objects.last().index + 1
        elif not self.__class__.objects.last():
            self.index = 1

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['date_of_update']


class Products(azt_models.AztLocaleModel, models.Model):
    SPECIAL_O2M_FIELDS = ['category']
    TRANSLATED_FIELDS = ['name', 'description']
    GENERAL_FIELDS = ['price', 'index', 'image', 'translations']

    id = models.CharField(max_length=8, primary_key=True, unique=True, null=False)
    name = models.CharField(max_length=100, null=False, blank=False,)
    description = models.TextField(null=False)
    image = models.ImageField(upload_to="images/food/")
    slug = models.CharField(max_length=100, null=False, unique=True, blank=True)
    price = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True,
                                validators=[MinValueValidator(0)], default=0)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name="products")
    index = models.PositiveIntegerField(blank=True, validators=[MinValueValidator(1)], )
    locale = models.ForeignKey('Locale', on_delete=models.CASCADE, related_name="products", )
    translations = models.CharField(max_length=1000, blank=True)
    date_of_update = models.DateTimeField(auto_now=True)
    date_of_add = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        self.set_index()

        if not self.id:
            self.id = azt_functions.set_id()
            self.slug = azt_functions.gen_slug(self.name)[0:100]

        super(Products, self).save(*args, **kwargs)

        self.set_translations()

    def get_other_lang_of_categories(self):
        product = dict(json.loads(self.translations))
        for code, id in json.loads(self.category.translations):
            pr = Products.objects.get(id=product[code])
            pr.category = Categories.objects.get(id=id)
            pr.save()

    def set_index(self):
        if not self.index and self.__class__.objects.last():
            self.index = self.__class__.objects.last().index + 1
        elif not self.__class__.objects.last():
            self.index = 1

    class Meta:
        verbose_name_plural = "Products"
        ordering = ['date_of_update']


"""
    Добавить SLUG 
    Добавить Категории ресторанов
    
    Посмотреть как будут выводиться продукты
"""
