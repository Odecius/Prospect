import pytest

from app.domain.normalization import normalize_cnpj, normalize_state_code, normalize_text


def test_text_normalization_is_stable_for_duplicate_comparison() -> None:
    assert normalize_text("  Café & Pão LTDA. ") == "cafe pao ltda"


def test_state_code_accepts_brazilian_codes_only() -> None:
    assert normalize_state_code(" sp ") == "SP"
    with pytest.raises(ValueError, match="UF inválida"):
        normalize_state_code("XX")


def test_cnpj_normalization_validates_check_digits() -> None:
    assert normalize_cnpj("11.222.333/0001-81") == "11222333000181"
    assert normalize_cnpj("") is None
    with pytest.raises(ValueError, match="CNPJ inválido"):
        normalize_cnpj("11.111.111/1111-11")
