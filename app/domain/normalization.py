import re
import unicodedata


def normalize_text(value: str) -> str:
    compact = " ".join(value.strip().split()).casefold()
    ascii_value = unicodedata.normalize("NFKD", compact).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", ascii_value).split())


def normalize_state_code(value: str) -> str:
    normalized = value.strip().upper()
    valid_codes = {
        "AC",
        "AL",
        "AP",
        "AM",
        "BA",
        "CE",
        "DF",
        "ES",
        "GO",
        "MA",
        "MT",
        "MS",
        "MG",
        "PA",
        "PB",
        "PR",
        "PE",
        "PI",
        "RJ",
        "RN",
        "RS",
        "RO",
        "RR",
        "SC",
        "SP",
        "SE",
        "TO",
    }
    if normalized not in valid_codes:
        raise ValueError("UF inválida.")
    return normalized


def normalize_cnpj(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None
    digits = re.sub(r"\D", "", value)
    if len(digits) != 14 or len(set(digits)) == 1:
        raise ValueError("CNPJ inválido.")
    for length in (12, 13):
        numbers = [int(digit) for digit in digits[:length]]
        weights = list(range(length - 7, 1, -1)) + list(range(9, 1, -1))
        remainder = sum(number * weight for number, weight in zip(numbers, weights, strict=True)) % 11
        check_digit = 0 if remainder < 2 else 11 - remainder
        if check_digit != int(digits[length]):
            raise ValueError("CNPJ inválido.")
    return digits
