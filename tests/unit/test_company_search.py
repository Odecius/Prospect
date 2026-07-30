import uuid

import pytest

from app.services.companies import CompanyService, CompanyValidationError


class SearchRepository:
    def search_companies(self, *values: object) -> tuple[list[object], int]:
        self.values = values
        return [], 0


def test_search_normalizes_query_state_and_preserves_pagination() -> None:
    repository = SearchRepository()
    result = CompanyService(repository).search_companies(" Café Azul ", uuid.uuid4(), "sp", "NEW", False, "name", 2, 25)

    assert result == ([], 0)
    assert repository.values[0] == "cafe azul"
    assert repository.values[2] == "SP"
    assert repository.values[3] == "NEW"
    assert repository.values[-2:] == (2, 25)


def test_search_rejects_unknown_pipeline_status() -> None:
    with pytest.raises(CompanyValidationError, match="pipeline inválido"):
        CompanyService(SearchRepository()).search_companies(None, None, None, "UNKNOWN", False, "name", 1, 25)
