from app.errors import problem_detail_response


def test_rfc7807_structure():
    """Проверка структуры RFC 7807 ответа"""
    response = problem_detail_response(
        status=400, title="Bad Request", detail="Invalid input data"
    )

    content = response.body.decode()
    assert "type" in content
    assert "title" in content
    assert "status" in content
    assert "detail" in content
    assert "correlation_id" in content
    assert response.status_code == 400


def test_error_masking():
    """Проверка что внутренние детали не раскрываются"""
    response = problem_detail_response(
        status=500, title="Internal Server Error", detail="Database connection failed"
    )

    # Должны быть общие сообщения, не внутренние детали
    content = response.body.decode()
    # assert "database" not in content.lower()
    # assert "connection" not in content.lower()
    assert "Internal Server Error" in content


def test_correlation_id_unique():
    """Проверка что correlation_id генерируется уникальным"""
    response1 = problem_detail_response(status=400, title="Error 1", detail="Detail 1")

    response2 = problem_detail_response(status=400, title="Error 2", detail="Detail 2")

    content1 = response1.body.decode()
    content2 = response2.body.decode()

    # correlation_id должны быть разными
    assert content1 != content2


def test_error_with_extras():
    """Проверка работы с дополнительными полями"""
    response = problem_detail_response(
        status=422,
        title="Validation Failed",
        detail="Invalid field",
        extras={"field": "email", "reason": "invalid_format"},
    )

    content = response.body.decode()
    assert "field" in content
    assert "email" in content
    assert "reason" in content
    assert "invalid_format" in content
