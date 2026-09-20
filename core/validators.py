from django.core.exceptions import ValidationError

def validate_uzb_numbers(value):
        if len(value) != 13:
            raise ValidationError("Telefon raqamingizni to'liq kiriting:(masalan:+998911234567)")
        if not value.startswith('+998'):
            raise ValidationError("Telefon raqamingizni to'liq kiriting:(masalan:+998911234567)")
        if not value[1:].isdigit():
            raise ValidationError("Telefon raqami raqamlardan iborat bo'lishi shart.")

        return value