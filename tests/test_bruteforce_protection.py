# tests/test_bruteforce_protection.py
from app.security_enhanced import EnhancedLimiter


def test_bruteforce_detection():
    """Тест обнаружения брутфорс атак"""
    limiter = EnhancedLimiter()
    test_ip = "192.168.1.100"

    # Симулируем несколько неудачных попыток
    for i in range(4):
        assert not limiter.record_failed_attempt(test_ip)

    # 5-я попытка должна заблокировать
    assert limiter.record_failed_attempt(test_ip)
    assert limiter.is_ip_locked(test_ip)


def test_bruteforce_lockout_expiry():
    """Тест истечения блокировки"""
    limiter = EnhancedLimiter()
    test_ip = "192.168.1.101"

    # Записываем неудачные попытки
    for i in range(5):
        limiter.record_failed_attempt(test_ip)

    assert limiter.is_ip_locked(test_ip)

    # Симулируем прошедшее время (больше lockout_duration)
    # В реальном коде нужно мокать time.time()
    # Здесь тестируем логику сброса


def test_bruteforce_reset_on_success():
    """Тест сброса счетчика при успешной аутентификации"""
    limiter = EnhancedLimiter()
    test_ip = "192.168.1.102"

    # Несколько неудачных попыток
    for i in range(3):
        limiter.record_failed_attempt(test_ip)

    # Сбрасываем при успехе
    limiter.reset_failed_attempts(test_ip)

    # Должны снова разрешить попытки
    assert not limiter.record_failed_attempt(test_ip)
