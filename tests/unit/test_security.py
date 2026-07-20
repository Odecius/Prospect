import pytest

from app.core.security import csrf_tokens_match, hash_password, normalize_email, verify_password


def test_password_is_hashed_with_argon2_and_verified() -> None:
    password_hash = hash_password("a-secure-test-password")

    assert password_hash.startswith("$argon2")
    assert "a-secure-test-password" not in password_hash
    assert verify_password(password_hash, "a-secure-test-password") is True
    assert verify_password(password_hash, "wrong-password") is False


def test_short_password_is_rejected() -> None:
    with pytest.raises(ValueError, match="12 caracteres"):
        hash_password("too-short")


def test_email_is_normalized_and_validated() -> None:
    assert normalize_email(" Admin@Example.COM ") == "admin@example.com"
    with pytest.raises(ValueError, match="Email inválido"):
        normalize_email("not-an-email")


def test_csrf_comparison_requires_matching_non_empty_tokens() -> None:
    assert csrf_tokens_match("token", "token") is True
    assert csrf_tokens_match("token", "different") is False
    assert csrf_tokens_match(None, None) is False
