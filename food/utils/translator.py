from django.http import HttpResponse
from googletrans import Translator
translator = Translator()


def capitalize_text(text):
    text_arr = list(text)
    for index in range(len(text_arr)):
        if text_arr[index] in ['.', ';', '?', '!']:
            for next_index in range(index, len(text_arr)):
                if text_arr[next_index] not in ['.', ';', '?', '!', ' ', '\n', '\r']:
                    text_arr[next_index] = str(text_arr[next_index]).upper()
                    break
    return f''.join(text_arr)


def translate_text(obj, fr, to,  field_name, capitalize):
    try:
        text = str(translator.translate(getattr(obj, f'{field_name}'), src=f'{fr}', dest=f'{to}').text).capitalize()
        if capitalize:
            text = capitalize_text(text)
        return text
    except ValueError:
        return getattr(obj, f'{field_name}')


def translate_client_email(text, lang):
    return str(translator.translate(text, src='en', dest=lang)).capitalize()