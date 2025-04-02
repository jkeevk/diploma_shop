from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class PhoneValidator:
    def __call__(self, value):
        if value is None:
            raise ValidationError(_("Номер телефона не может быть пустым"))

        if not isinstance(value, str):
            raise ValidationError(_("Номер телефона должен быть строкой"))

        if not value.startswith("+"):
            raise ValidationError(_("Номер должен начинаться с '+'"))

        if len(value) < 10:
            raise ValidationError(_("Слишком короткий номер"))

        if not value[1:].isdigit():
            raise ValidationError(_("Номер должен содержать только цифры после '+'"))
