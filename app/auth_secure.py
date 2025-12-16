# app/auth_secure.py
from app.problem_details import problem_details
from app.security_enhanced import enhanced_limiter
from app.token_security import token_manager


def secure_auth_with_bruteforce_protection(credentials):
    """Аутентификация с защитой от брутфорса"""
    client_ip = "unknown"  # В реальности получаем из request

    # Проверяем блокировку IP
    if enhanced_limiter.is_ip_locked(client_ip):
        return problem_details.create_problem_response(
            status=429,
            title="Too Many Requests",
            detail="Your IP has been temporarily locked due to too many failed attempts",
            error_type="https://api.example.com/errors/ip-locked",
        )

    # Проверяем токен
    if not credentials or credentials.scheme.lower() != "bearer":
        enhanced_limiter.record_failed_attempt(client_ip)
        return problem_details.create_problem_response(
            status=401,
            title="Unauthorized",
            detail="Missing or invalid authentication",
            error_type="https://api.example.com/errors/unauthorized",
        )

    token = credentials.credentials.strip()
    username = token_manager.validate_token(token)

    if not username:
        enhanced_limiter.record_failed_attempt(client_ip)
        return problem_details.create_problem_response(
            status=401,
            title="Unauthorized",
            detail="Invalid token",
            error_type="https://api.example.com/errors/unauthorized",
        )

    # Сбрасываем счетчик при успешной аутентификации
    enhanced_limiter.reset_failed_attempts(client_ip)
    return username
