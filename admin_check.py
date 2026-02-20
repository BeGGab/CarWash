import os
from typing import Any, Set

def _parse_admin_ids(env_value: str | None) -> Set[int]:
    if not env_value:
        return set()
    ids: Set[int] = set()
    for part in env_value.split(','):
        part = part.strip()
        if not part:
            continue
        try:
            ids.add(int(part))
        except ValueError:
            continue
    return ids

_CONFIGURED_ADMINS: Set[int] = set()
_CONFIGURED_ADMINS |= _parse_admin_ids(os.getenv('ADMIN_IDS'))
_single_admin = os.getenv('ADMIN_ID')
if _single_admin:
    try:
        _CONFIGURED_ADMINS.add(int(_single_admin))
    except ValueError:
        pass


def is_admin(user_id: int | str) -> bool:
    if isinstance(user_id, str):
        try:
            user_id = int(user_id)
        except ValueError:
            return False
    if not isinstance(user_id, int):
        return False

    return user_id in _CONFIGURED_ADMINS


def _extract_user_id(obj: Any) -> int | None:
    # Direct int or str input
    if isinstance(obj, (int, str)):
        try:
            return int(obj)
        except (TypeError, ValueError):
            return None

    # Aiogram Message or CallbackQuery: obj.from_user.id
    from_user = getattr(obj, "from_user", None)
    if from_user is not None:
        uid = getattr(from_user, "id", None)
        try:
            return int(uid) if uid is not None else None
        except (TypeError, ValueError):
            return None

    # Aiogram CallbackQuery can also have 'message' with 'from_user'
    message = getattr(obj, "message", None)
    if message is not None:
        from_user = getattr(message, "from_user", None)
        if from_user is not None:
            uid = getattr(from_user, "id", None)
            try:
                return int(uid) if uid is not None else None
            except (TypeError, ValueError):
                return None

    # Dict-like Telegram update structures
    if isinstance(obj, dict):
        try:
            uid = (
                obj.get("from", {}).get("id")
                or obj.get("message", {}).get("from", {}).get("id")
                or obj.get("callback_query", {}).get("from", {}).get("id")
            )
            return int(uid) if uid is not None else None
        except (AttributeError, ValueError, TypeError):
            return None

    return None


def is_admin_from(obj: Any) -> bool:
    """
    Universal admin check helper for bot updates.

    Accepts one of:
      - int or str user_id
      - aiogram.types.Message (e.g., /start message)
      - aiogram.types.CallbackQuery
      - dict-like Telegram update

    Returns True if the resolved user_id is configured as admin.
    """
    uid = _extract_user_id(obj)
    if uid is None:
        return False
    return is_admin(uid)


__all__ = ["is_admin", "is_admin_from"]
