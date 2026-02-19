import re
from typing import Annotated

from pydantic import AfterValidator, PlainValidator


def validate_not_empty(value: str) -> str:
    if not value or not value.strip():
        raise ValueError("Поле не может быть пустым")
    return value


def validate_phone_number(value: str) -> str:
    if not re.match(r"^\+7\d{10}$", value):
        raise ValueError('Номер телефона должен начинаться с "+7" и содержать 10 цифр.')
    return value


def validate_working_hours(value: dict) -> dict:
    if not isinstance(value, dict):
        raise ValueError("Рабочие часы должны быть словарем")
    if "start" not in value or "end" not in value:
        raise ValueError("Рабочие часы должны содержать 'start' и 'end'")
    try:
        start_hour, start_minute = map(int, value["start"].split(":"))
        end_hour, end_minute = map(int, value["end"].split(":"))

        if not (0 <= start_hour <= 23 and 0 <= start_minute <= 59):
            raise ValueError("Неверный формат времени начала работы")
        if not (0 <= end_hour <= 23 and 0 <= end_minute <= 59):
            raise ValueError("Неверный формат времени окончания работы")

        if (start_hour, start_minute) >= (end_hour, end_minute):
            raise ValueError("Время начала работы должно быть раньше времени окончания")
    except (ValueError, TypeError):
        raise ValueError("Неверный формат времени в рабочих часах. Используйте 'HH:MM'")
    return value


NotEmptyString = Annotated[str, AfterValidator(validate_not_empty)]
PhoneNumber = Annotated[str, PlainValidator(validate_phone_number)]
WorkingHours = Annotated[dict, PlainValidator(validate_working_hours)]
