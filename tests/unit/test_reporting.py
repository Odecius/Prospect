import uuid
from datetime import UTC, datetime, timedelta

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

    def validation_counts(self, _started_at: datetime, _ended_at: datetime) -> dict[str, int]:
        return {
            "companies_created": 24,
            "companies_scored": 20,
            "companies_with_activity": 18,
            "companies_contacted": 10,
            "companies_replied": 4,
            "companies_with_meeting": 2,
            "companies_progressed": 8,
            "companies_won": 1,
            "companies_marked_do_not_contact": 2,
            "scored_with_positive_progression": 6,
        }

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


def test_validation_snapshot_calculates_only_reproducible_rates() -> None:
    started_at = datetime(2026, 7, 1, tzinfo=UTC)
    snapshot = ReportingService(ReportingRepositoryFake()).validation_snapshot(
        started_at, started_at + timedelta(days=14)
    )

    assert snapshot["companies_created"] == 24
    assert snapshot["contact_response_rate"] == 0.4
    assert snapshot["score_progression_rate"] == 0.3


@pytest.mark.parametrize(
    ("started_at", "ended_at", "message"),
    [
        (datetime(2026, 7, 1), datetime(2026, 7, 2), "fuso horário"),
        (datetime(2026, 7, 2, tzinfo=UTC), datetime(2026, 7, 1, tzinfo=UTC), "posterior"),
        (datetime(2026, 1, 1, tzinfo=UTC), datetime(2026, 7, 1, tzinfo=UTC), "90 dias"),
    ],
)
def test_validation_snapshot_rejects_ambiguous_periods(started_at: datetime, ended_at: datetime, message: str) -> None:
    with pytest.raises(ReportingValidationError, match=message):
        ReportingService(ReportingRepositoryFake()).validation_snapshot(started_at, ended_at)
