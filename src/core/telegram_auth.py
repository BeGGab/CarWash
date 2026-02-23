import hashlib
import hmac
import urllib.parse
import json
from typing import Dict, Any
from src.core.config import Settings

settings = Settings()

def _hex_to_bytes(hex_string: str) -> bytes:
    """Converts a hexadecimal string to bytes."""
    return bytes.fromhex(hex_string)

def validate_init_data(init_data: str) -> bool:
    """
    Validates Telegram Mini App initData.
    More info: https://core.telegram.org/bots/webapps#checking-authorization
    """
    if not init_data:
        return False

    # Parse the init_data string
    parsed_data = urllib.parse.parse_qs(init_data)
    
    # Extract hash and other parameters
    data_check_string_parts = []
    hash_value = None
    for key, value in sorted(parsed_data.items()):
        key = key[0] # parse_qs returns lists for values
        value = value[0]
        if key == 'hash':
            hash_value = value
        else:
            data_check_string_parts.append(f"{key}={value}")
    
    data_check_string = '\n'.join(data_check_string_parts)

    secret_key = hmac.new(b"WebAppData", settings.bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    return calculated_hash == hash_value

def parse_init_data(init_data: str) -> Dict[str, Any]:
    """Parses Telegram Mini App initData into a dictionary."""
    parsed_data = urllib.parse.parse_qs(init_data)
    result = {k[0]: v[0] for k, v in parsed_data.items()}
    if 'user' in result:
        result['user'] = json.loads(result['user'])
    return result
