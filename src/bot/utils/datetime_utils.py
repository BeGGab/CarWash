"""
Утилиты для работы с датой и временем.
"""

import locale
from datetime import datetime

# Устанавливаем русскую локаль для корректного отображения названий месяцев.
# Пробуем сначала стандарт для Linux, потом для Windows.
try:
    locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, "Russian_Russia.1251")
    except locale.Error:
        # Если локали не найдены, будет использована системная.
        # В лог можно добавить предупреждение, если это критично.
        pass


def format_date_for_display(iso_date_str: str) -> str:
    """
    Форматирует дату из ISO-строки в 'dd Month'.
    Пример: '2023-10-27' -> '27 октября'
    """
    if not iso_date_str:
        return ""
    date_obj = datetime.fromisoformat(iso_date_str.split("T")[0])
    return date_obj.strftime("%d %B")


def format_time_for_display(iso_time_str: str) -> str:
    """
    Форматирует время из ISO-стро-ки в 'HH:MM'.
    Пример: '14:30:00' -> '14:30'
    """
    if not iso_time_str:
        return ""
    time_obj = datetime.fromisoformat(f"1970-01-01T{iso_time_str}")
    return time_obj.strftime("%H:%M")
