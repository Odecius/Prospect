import re
import unicodedata
from urllib.parse import urlsplit, urlunsplit


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


def normalize_contact(contact_type: str, value: str) -> str:
    raw = value.strip()
    if not raw or len(raw) > 500:
        raise ValueError("Contato inválido.")
    if contact_type == "PHONE":
        digits = re.sub(r"\D", "", raw)
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError("Telefone inválido.")
        return f"+{digits}"
    if contact_type == "EMAIL":
        normalized = raw.casefold()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized):
            raise ValueError("Email inválido.")
        return normalized
    if contact_type == "WEBSITE":
        parsed = urlsplit(raw if "://" in raw else f"https://{raw}")
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("Website inválido.")
        host = parsed.hostname.casefold().removeprefix("www.")
        return urlunsplit(("https", host, parsed.path.rstrip("/"), "", ""))
    if contact_type == "INSTAGRAM":
        handle = raw.rstrip("/").split("/")[-1].removeprefix("@").casefold()
        if not re.fullmatch(r"[a-z0-9._]{1,30}", handle):
            raise ValueError("Perfil do Instagram inválido.")
        return handle
    raise ValueError("Tipo de contato inválido.")
