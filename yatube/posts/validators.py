from django.forms import ValidationError


def validate_not_empty(text):
    if text == '':
        raise ValidationError(
            'Пожалуйста, введите текст поста в форму.',
            params={'text': text},
        )
