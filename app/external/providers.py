from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ExternalPlace:
    external_id: str
    name: str | None
    formatted_address: str | None
    city: str | None
    state_code: str | None
    latitude: float | None
    longitude: float | None
    primary_type: str | None
    types: list[str]
    business_status: str | None
    rating: float | None
    user_rating_count: int | None
    website_uri: str | None
    google_maps_uri: str | None
    attributions: list[str]


@dataclass(frozen=True)
class ExternalSearchPage:
    places: list[ExternalPlace]
    next_page_token: str | None


class BusinessSearchProvider(Protocol):
    def search(
        self,
        query: str,
        page_size: int,
        page_token: str | None = None,
        location_restriction: dict | None = None,
    ) -> ExternalSearchPage: ...
