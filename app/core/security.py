import hmac
import re
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

_password_hasher = PasswordHasher()
_email_pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_email(email: str) -> str:
    normalized = email.strip().casefold()
    if len(normalized) > 320 or not _email_pattern.fullmatch(normalized):
        raise ValueError("Email inválido.")
    return normalized


def hash_password(password: str) -> str:
    if len(password) < 12:
        raise ValueError("A senha deve ter pelo menos 12 caracteres.")
    return _password_hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _password_hasher.verify(password_hash, password)
    except (InvalidHashError, VerifyMismatchError):
        return False


def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def csrf_tokens_match(expected: str | None, supplied: str | None) -> bool:
    return bool(expected and supplied and hmac.compare_digest(expected, supplied))
