# app/auth_routes.py
from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.token_security import token_manager

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/tokens", summary="Create new token")
def create_token(username: str = Depends(get_current_user)):
    """Создание нового токена для пользователя"""
    new_token = token_manager.create_token(username)
    return {"token": new_token, "message": "Store this token securely"}


@router.delete("/tokens", summary="Revoke current token")
def revoke_token(username: str = Depends(get_current_user)):
    """Отзыв текущего токена"""
    # Для полноценной реализации нужно отслеживать текущий токен
    return {"message": "Token revocation requires tracking current token session"}


@router.get("/token-stats", summary="Get token statistics")
def get_token_stats(_: str = Depends(get_current_user)):
    """Получение статистики токенов (только для отладки)"""
    return token_manager.get_token_stats()
