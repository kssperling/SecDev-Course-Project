# # app/auth.py
# from __future__ import annotations
#
# from fastapi import Depends
# from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
#
#
# class ApiError(Exception):
#     def __init__(self, code: str, message: str, status: int = 400):
#         self.code = code
#         self.message = message
#         self.status = status
#
#
# TOKEN_MAP = {
#     "token-alice": "alice",
#     "token-bob": "bob",
# }
#
# bearer = HTTPBearer(auto_error=False)
#
#
# def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(bearer),
# ) -> str:
#     if not credentials or credentials.scheme.lower() != "bearer":
#         raise ApiError("unauthorized", "missing bearer token", 401)
#     token = credentials.credentials.strip()
#     username = TOKEN_MAP.get(token)
#     if not username:
#         raise ApiError("unauthorized", "invalid token", 401)
#     return username

from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class ApiError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status


TOKEN_MAP = {
    "token-alice": "alice",
    "token-bob": "bob",
}

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> str:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise ApiError("unauthorized", "missing bearer token", 401)
    token = credentials.credentials.strip()
    username = TOKEN_MAP.get(token)
    if not username:
        raise ApiError("unauthorized", "invalid token", 401)
    return username
