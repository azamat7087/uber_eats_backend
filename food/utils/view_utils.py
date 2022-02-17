import json

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import generics, status
import food.models as azt_models
import os
import inspect
from django.conf import settings


def configure_languages(request):
    for lang in settings.AZT_LANGUAGES:
        azt_models.Locale.objects.create(name=lang[2], code=lang[0], iso=lang[1])


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def str_to_class(classname):
    return getattr(azt_models, classname)


class ViewSerializerMixin:
    list_serializer_class = None

    @staticmethod
    def get_caller_name():
        current_frame = inspect.currentframe()
        call_frame = inspect.getouterframes(current_frame, 2)
        return call_frame[2][3]

    def get_serializer(self, *args, **kwargs):
        caller = self.get_caller_name()
        serializer_class = self.get_serializer_class()

        if caller == 'list':
            serializer_class = self.list_serializer_class
        elif caller == 'retrieve':
            serializer_class = self.serializer_class

        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)


class ListObjectsMixin(generics.ListAPIView):

    serializer_class = None
    filter_backends = (DjangoFilterBackend,)
    permission_classes = []
    model = None
    user_private = None
    filter_fields = []
    search_fields = []

    def list(self, request, *args, **kwargs):
        try:
            class_name = str_to_class(self.model)
            lang_code = request.GET.get('lang', 'en')
            objects = class_name.objects.all()

            objects = self.filter_queryset(objects)

            objects = objects.filter(locale__code=lang_code)

            page = self.paginate_queryset(objects)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(objects, many=True)

            return Response(serializer.data, status.HTTP_200_OK)
        except Exception as e:
            return Response(f"Error, wrong data: {str(e)}",  status.HTTP_400_BAD_REQUEST)


class RetrieveObjectsMixin(generics.RetrieveAPIView):
    serializer_class = None
    filter_backends = (DjangoFilterBackend,)
    permission_classes = []
    obj = None
    model = None
    user_private = None
    lookup_field = 'id'

    def get_lang_object(self, lang, obj):
        translations = json.loads(obj.translations)

        for code, obj_id in translations:
            if lang == code:
                return str_to_class(self.model).objects.get(id=obj_id)
        raise Exception(f"{lang} language not supported")

    def retrieve(self, request, *args, **kwargs):
        class_name = str_to_class(self.model)
        try:
            lang = request.GET.get('lang', "")
            obj = class_name.objects.get(id=kwargs['id'])

            if lang:
                obj = self.get_lang_object(lang, obj)

            serializer = self.serializer_class(obj)
            return Response(serializer.data, status.HTTP_200_OK)
        except class_name.DoesNotExist:
            return Response(f'DoesNotExist. {self.obj} does not exist in {self.model}', status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(f"Error, wrong data: {str(e)}",  status.HTTP_400_BAD_REQUEST)


class AztViewMixin(ListObjectsMixin, RetrieveObjectsMixin, GenericViewSet):
    pass
