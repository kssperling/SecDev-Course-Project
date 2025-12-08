from urllib import request

from fastapi import HTTPException, Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded errors"""
    raise HTTPException(
        status_code=429,
        detail={
            "error": {
                "code": "rate_limit_exceeded",
                "message": "Too many requests. Please try again later.",
            }
        },
    )


def get_rate_limit_key(user_role: str = "anonymous") -> str:
    """Ключ для rate limiting с учетом роли"""
    base_key = get_remote_address(request)
    return f"{base_key}:{user_role}"


# Конфигурируемые лимиты
RATE_LIMITS = {"anonymous": "10/minute", "user": "100/minute", "admin": "1000/minute"}

limiter = Limiter(key_func=get_remote_address)
