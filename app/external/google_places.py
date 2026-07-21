import logging
import time
from collections.abc import Callable

import httpx

from app.external.providers import ExternalPlace, ExternalSearchPage

logger = logging.getLogger(__name__)

GOOGLE_PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
FIELD_MASK = ",".join(
    [
        "places.id",
        "places.displayName",
        "places.formattedAddress",
        "places.addressComponents",
        "places.location",
        "places.primaryType",
        "places.types",
        "places.businessStatus",
        "places.rating",
        "places.userRatingCount",
        "places.websiteUri",
        "places.googleMapsUri",
        "places.attributions",
        "nextPageToken",
    ]
)


class GooglePlacesError(Exception):
    pass


class GooglePlacesConfigurationError(GooglePlacesError):
    pass


class GooglePlacesAuthenticationError(GooglePlacesError):
    pass


class GooglePlacesTemporaryError(GooglePlacesError):
    pass


class GooglePlacesClient:
    def __init__(
        self,
        api_key: str | None,
        timeout_seconds: float,
        max_retries: int,
        transport: httpx.BaseTransport | None = None,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.api_key = api_key.strip() if api_key else None
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.transport = transport
        self.sleeper = sleeper

    def search(
        self,
        query: str,
        page_size: int,
        page_token: str | None = None,
        location_restriction: dict | None = None,
    ) -> ExternalSearchPage:
        if not self.api_key:
            raise GooglePlacesConfigurationError("Google Places API não configurada.")
        body: dict[str, object] = {
            "textQuery": query,
            "languageCode": "pt-BR",
            "regionCode": "BR",
            "pageSize": min(page_size, 20),
        }
        if page_token:
            body["pageToken"] = page_token
        if location_restriction:
            body["locationRestriction"] = location_restriction
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": FIELD_MASK,
        }
        for attempt in range(self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout_seconds, transport=self.transport) as client:
                    response = client.post(GOOGLE_PLACES_URL, headers=headers, json=body)
                logger.info("google_places_request completed status=%s attempt=%s", response.status_code, attempt + 1)
                if response.status_code in {401, 403}:
                    raise GooglePlacesAuthenticationError("Credencial da Google Places rejeitada.")
                if response.status_code in {408, 429} or response.status_code >= 500:
                    if attempt < self.max_retries:
                        self.sleeper(0.25 * (2**attempt))
                        continue
                    raise GooglePlacesTemporaryError("Google Places temporariamente indisponível.")
                if response.status_code >= 400:
                    raise GooglePlacesError("Google Places recusou a pesquisa.")
                return self._map_response(response.json())
            except httpx.TimeoutException as error:
                if attempt < self.max_retries:
                    self.sleeper(0.25 * (2**attempt))
                    continue
                raise GooglePlacesTemporaryError("Tempo limite da Google Places excedido.") from error
        raise GooglePlacesTemporaryError("Google Places temporariamente indisponível.")

    @staticmethod
    def _map_response(payload: dict) -> ExternalSearchPage:
        places = [GooglePlacesClient._map_place(item) for item in payload.get("places", []) if item.get("id")]
        return ExternalSearchPage(places=places, next_page_token=payload.get("nextPageToken"))

    @staticmethod
    def _map_place(item: dict) -> ExternalPlace:
        components = item.get("addressComponents") or []
        city = GooglePlacesClient._component(components, {"locality", "administrative_area_level_2"}, "longText")
        state = GooglePlacesClient._component(components, {"administrative_area_level_1"}, "shortText")
        location = item.get("location") or {}
        return ExternalPlace(
            external_id=item["id"],
            name=(item.get("displayName") or {}).get("text"),
            formatted_address=item.get("formattedAddress"),
            city=city,
            state_code=state,
            latitude=location.get("latitude"),
            longitude=location.get("longitude"),
            primary_type=item.get("primaryType"),
            types=item.get("types") or [],
            business_status=item.get("businessStatus"),
            rating=item.get("rating"),
            user_rating_count=item.get("userRatingCount"),
            website_uri=item.get("websiteUri"),
            google_maps_uri=item.get("googleMapsUri"),
            attributions=[str(value) for value in item.get("attributions") or []],
        )

    @staticmethod
    def _component(components: list[dict], accepted_types: set[str], field: str) -> str | None:
        for component in components:
            if accepted_types.intersection(component.get("types") or []):
                return component.get(field)
        return None
