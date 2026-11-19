
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from pwdlib import PasswordHash

from config import settings


password_hash = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def create_token(
    user_id: int,
    token_version: int,
    token_type: str,
    expires_delta: timedelta,
) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "type": token_type,
        "ver": token_version,
        "iat": now,
        "nbf": now,
        "exp": now + expires_delta,
        "jti": str(uuid4()),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm="HS256",
    )


def create_access_token(
    user_id: int,
    token_version: int,
) -> str:
    return create_token(
        user_id,
        token_version,
        "access",
        timedelta(
            minutes=settings.access_token_expire_minutes
        ),
    )


def create_refresh_token(
    user_id: int,
    token_version: int,
) -> str:
    return create_token(
        user_id,
        token_version,
        "refresh",
        timedelta(days=7),
    )


def decode_token(token: str, expected_type: str) -> dict:
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=["HS256"],
        options={
            "require": [
                "sub", "type", "ver",
                "iat", "nbf", "exp", "jti",
            ]
        },
    )

    user_id = payload.get("sub")

    if (
        payload.get("type") != expected_type
        or not isinstance(user_id, str)
        or not user_id.isdecimal()
        or int(user_id) <= 0
        or type(payload.get("ver")) is not int
        or payload["ver"] < 0
        or not isinstance(payload.get("jti"), str)
        or not payload["jti"]
    ):
        raise jwt.InvalidTokenError("Invalid token")

    return payload
