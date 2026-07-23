import uuid

import pytest

from app.database.models import ExportAudit, PipelineStatus, User
from app.services.reporting import ExportFilters, ReportingService, ReportingValidationError


class ReportingRepositoryFake:
    def __init__(self, rows: list[tuple] | None = None, total: int | None = None) -> None:
        self.rows = rows or []
        self.total = len(self.rows) if total is None else total
        self.audit = None
        self.filters = None

    def dashboard(self) -> dict:
        return {"total_active": 2}

    def export_rows(self, *filters: object) -> tuple[list[tuple], int]:
        self.filters = filters
        return self.rows, self.total

    def add_export_audit(self, audit: ExportAudit) -> None:
        self.audit = audit

    def commit(self) -> None:
        pass


def test_export_is_minimized_audited_and_safe_for_spreadsheets() -> None:
    category_id = uuid.uuid4()
    repository = ReportingRepositoryFake(
        [("=Fórmula", "Serviços", "São Paulo", "SP", PipelineStatus.DO_NOT_CONTACT, False, 81)]
    )
    content = ReportingService(repository).export_csv(
        ExportFilters(" Empresa ", category_id, "sp", "DO_NOT_CONTACT"), User(id=uuid.uuid4())
    )

    assert content.startswith("\ufeffempresa,categoria,cidade,uf,pipeline,website_presente,score\n")
    assert "'=Fórmula,Serviços,São Paulo,SP,DO_NOT_CONTACT,não,81" in content
    assert repository.filters == ("empresa", category_id, "SP", "DO_NOT_CONTACT")
    assert repository.audit.row_count == 1
    assert repository.audit.fields == [
        "empresa",
        "categoria",
        "cidade",
        "uf",
        "pipeline",
        "website_presente",
        "score",
    ]


def test_export_requires_refined_filters_above_limit() -> None:
    repository = ReportingRepositoryFake(total=501)
    with pytest.raises(ReportingValidationError, match="refine os filtros"):
        ReportingService(repository).export_csv(ExportFilters(), User(id=uuid.uuid4()))
    assert repository.audit is None


def test_export_rejects_unknown_pipeline_status() -> None:
    with pytest.raises(ReportingValidationError, match="pipeline inválido"):
        ReportingService(ReportingRepositoryFake()).export_csv(
            ExportFilters(pipeline_status="UNKNOWN"), User(id=uuid.uuid4())
        )
