import httpx
import pytest

from app.external.google_places import (
    FIELD_MASK,
    GOOGLE_PLACES_URL,
    GooglePlacesAuthenticationError,
    GooglePlacesClient,
    GooglePlacesConfigurationError,
    GooglePlacesError,
    GooglePlacesTemporaryError,
)


def transport(status: int = 200, payload: dict | None = None) -> httpx.MockTransport:
    return httpx.MockTransport(lambda request: httpx.Response(status, json=payload or {}, request=request))


def sample_place() -> dict:
    return {
        "id": "place-123",
        "displayName": {"text": "Empresa Fictícia"},
        "formattedAddress": "Rua Teste, São Paulo - SP",
        "addressComponents": [
            {"longText": "São Paulo", "shortText": "São Paulo", "types": ["locality"]},
            {"longText": "São Paulo", "shortText": "SP", "types": ["administrative_area_level_1"]},
        ],
        "location": {"latitude": -23.5, "longitude": -46.6},
        "primaryType": "store",
        "types": ["store"],
        "businessStatus": "OPERATIONAL",
        "rating": 4.7,
        "userRatingCount": 120,
        "websiteUri": "https://example.test",
        "googleMapsUri": "https://maps.google.test/place-123",
    }


def test_successful_search_maps_fields_and_uses_explicit_mask() -> None:
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["mask"] = request.headers["X-Goog-FieldMask"]
        seen["key"] = request.headers["X-Goog-Api-Key"]
        return httpx.Response(200, json={"places": [sample_place()]}, request=request)

    result = GooglePlacesClient("fake-key", 2, 0, httpx.MockTransport(handler)).search("lojas", 10)

    assert seen == {"mask": FIELD_MASK, "key": "fake-key"}
    assert "*" not in FIELD_MASK
    assert result.places[0].city == "São Paulo"
    assert result.places[0].state_code == "SP"
    assert result.places[0].website_uri == "https://example.test"


def test_empty_and_paginated_responses() -> None:
    empty = GooglePlacesClient("fake", 2, 0, transport()).search("lojas", 5)
    page = GooglePlacesClient("fake", 2, 0, transport(payload={"nextPageToken": "next"})).search("lojas", 5)
    assert empty.places == []
    assert page.next_page_token == "next"


def test_missing_key_and_invalid_key_are_distinct() -> None:
    with pytest.raises(GooglePlacesConfigurationError):
        GooglePlacesClient(None, 2, 0).search("lojas", 5)
    with pytest.raises(GooglePlacesAuthenticationError):
        GooglePlacesClient("invalid", 2, 0, transport(403)).search("lojas", 5)


def test_timeout_retries_are_limited() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ReadTimeout("timeout", request=request)

    with pytest.raises(GooglePlacesTemporaryError, match="Tempo limite"):
        GooglePlacesClient("fake", 1, 2, httpx.MockTransport(handler), sleeper=lambda _value: None).search("lojas", 5)
    assert calls == 3


@pytest.mark.parametrize("status", [400, 404])
def test_non_retryable_4xx(status: int) -> None:
    with pytest.raises(GooglePlacesError):
        GooglePlacesClient("fake", 2, 2, transport(status)).search("lojas", 5)


def test_5xx_retries_then_fails() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(503, json={}, request=request)

    with pytest.raises(GooglePlacesTemporaryError):
        GooglePlacesClient("fake", 2, 1, httpx.MockTransport(handler), sleeper=lambda _value: None).search("lojas", 5)
    assert calls == 2


def test_incomplete_response_and_missing_optional_fields_are_safe() -> None:
    result = GooglePlacesClient(
        "fake", 2, 0, transport(payload={"places": [{"id": "only-id"}, {"displayName": {"text": "ignored"}}]})
    ).search("lojas", 5)
    assert len(result.places) == 1
    assert result.places[0].name is None
    assert result.places[0].rating is None
    assert result.places[0].user_rating_count is None
    assert result.places[0].website_uri is None


def test_request_targets_only_official_endpoint_and_limits_page_size() -> None:
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["body"] = request.read().decode()
        return httpx.Response(200, json={}, request=request)

    GooglePlacesClient("fake", 2, 0, httpx.MockTransport(handler)).search("lojas", 999)
    assert seen["url"] == GOOGLE_PLACES_URL
    assert '"pageSize":20' in seen["body"]
