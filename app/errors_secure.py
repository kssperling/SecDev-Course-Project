# app/errors_secure.py
from app.problem_details import problem_details


async def secure_validation_exception_handler(request, exc):
    """Безопасный обработчик ошибок валидации"""
    return problem_details.create_problem_response(
        status=422,
        title="Validation Failed",
        detail="The request contains invalid parameters",
        error_type="https://api.example.com/errors/validation-failed",
        instance=str(request.url),
    )


async def secure_http_exception_handler(request, exc):
    """Безопасный обработчик HTTP исключений"""
    # Маскируем детали ошибок для клиента
    if exc.status_code == 404:
        detail = "The requested resource was not found"
    elif exc.status_code == 403:
        detail = "Access to the resource is forbidden"
    elif exc.status_code == 401:
        detail = "Authentication required"
    else:
        detail = "An error occurred while processing your request"

    return problem_details.create_problem_response(
        status=exc.status_code,
        title=exc.detail if hasattr(exc, "detail") else "HTTP Error",
        detail=detail,
        instance=str(request.url),
    )
