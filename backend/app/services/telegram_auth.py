import hmac
import hashlib
import urllib.parse
from typing import Optional
from datetime import datetime, timedelta

from jose import jwt

from app.config import settings


def validate_telegram_init_data(init_data: str) -> Optional[dict]:
    """
    Validate Telegram WebApp init_data using HMAC-SHA256.
    Returns parsed user data if valid, None otherwise.
    """
    if not settings.bot_token:
        # In mock mode, accept any init_data format
        if settings.telegram_auth_mock:
            return _parse_init_data_simple(init_data)
        return None

    try:
        # Parse the init data
        parsed = dict(urllib.parse.parse_qsl(init_data))
        
        # Get hash from parsed data
        received_hash = parsed.pop('hash', None)
        if not received_hash:
            return None

        # Check auth_date is not too old (24 hours)
        auth_date = int(parsed.get('auth_date', 0))
        if datetime.utcnow().timestamp() - auth_date > 86400:
            return None

        # Create data check string
        data_check_string = '\n'.join(
            f"{k}={v}" 
            for k, v in sorted(parsed.items())
        )

        # Create secret key from bot token
        secret_key = hmac.new(
            settings.bot_token.encode(),
            b'WebAppData',
            hashlib.sha256
        ).digest()

        # Calculate hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        if calculated_hash != received_hash:
            return None

        # Parse user data from JSON string
        import json
        user_data = json.loads(parsed.get('user', '{}'))
        
        return {
            'telegram_user_id': str(user_data.get('id')),
            'username': user_data.get('username'),
            'first_name': user_data.get('first_name'),
            'last_name': user_data.get('last_name'),
            'language_code': user_data.get('language_code'),
        }

    except Exception:
        return None


def _parse_init_data_simple(init_data: str) -> Optional[dict]:
    """Parse init_data for mock mode (accepts test format)."""
    try:
        parsed = dict(urllib.parse.parse_qsl(init_data))
        
        # Support both real Telegram format and mock format
        user_id = parsed.get('user_id') or parsed.get('id')
        if not user_id:
            return None
            
        return {
            'telegram_user_id': str(user_id),
            'username': parsed.get('username', 'mock_user'),
            'first_name': parsed.get('first_name', 'Mock'),
            'last_name': parsed.get('last_name'),
            'language_code': parsed.get('language_code', 'ru'),
        }
    except Exception:
        return None


def create_jwt_token(telegram_user_id: str) -> str:
    """Create JWT token for authenticated user."""
    expires = datetime.utcnow() + timedelta(days=30)
    to_encode = {
        'sub': telegram_user_id,
        'exp': expires,
        'iat': datetime.utcnow(),
    }
    return jwt.encode(to_encode, settings.jwt_secret, algorithm='HS256')
