import csv
import io
import uuid
from dataclasses import dataclass

from app.database.models import ExportAudit, PipelineStatus, User
from app.domain.normalization import normalize_state_code, normalize_text
from app.repositories.reporting import ReportingRepository

EXPORT_FIELDS = ["empresa", "categoria", "cidade", "uf", "pipeline", "website_presente", "score"]
MAX_EXPORT_ROWS = 500


class ReportingValidationError(Exception):
    pass


@dataclass(frozen=True)
class ExportFilters:
    query: str | None = None
    category_id: uuid.UUID | None = None
    state_code: str | None = None
    pipeline_status: str | None = None


class ReportingService:
    def __init__(self, repository: ReportingRepository) -> None:
        self.repository = repository

    def dashboard(self) -> dict:
        return self.repository.dashboard()

    def export_csv(self, filters: ExportFilters, actor: User) -> str:
        query = normalize_text(filters.query) if filters.query else None
        state_code = normalize_state_code(filters.state_code) if filters.state_code else None
        pipeline_status = None
        if filters.pipeline_status:
            try:
                pipeline_status = PipelineStatus(filters.pipeline_status).value
            except ValueError as error:
                raise ReportingValidationError("Estado do pipeline inválido.") from error
        rows, total = self.repository.export_rows(query, filters.category_id, state_code, pipeline_status)
        if total > MAX_EXPORT_ROWS:
            raise ReportingValidationError(
                f"A exportação possui {total} registros; refine os filtros para no máximo {MAX_EXPORT_ROWS}."
            )
        output = io.StringIO(newline="")
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(EXPORT_FIELDS)
        for name, category, city, uf, status, website_present, score in rows:
            writer.writerow(
                [
                    self._safe_cell(name),
                    self._safe_cell(category),
                    self._safe_cell(city),
                    uf,
                    status.value,
                    "sim" if website_present else "não",
                    "" if score is None else score,
                ]
            )
        filter_snapshot = {
            key: str(value) if value is not None else None
            for key, value in {
                "query": query,
                "category_id": filters.category_id,
                "state_code": state_code,
                "pipeline_status": pipeline_status,
            }.items()
        }
        self.repository.add_export_audit(
            ExportAudit(
                export_type="COMPANY_SEGMENT_CSV",
                filters=filter_snapshot,
                fields=EXPORT_FIELDS,
                row_count=total,
                performed_by_user_id=actor.id,
            )
        )
        self.repository.commit()
        return "\ufeff" + output.getvalue()

    @staticmethod
    def _safe_cell(value: str) -> str:
        normalized = " ".join(value.split())
        return f"'{normalized}" if normalized.lstrip().startswith(("=", "+", "-", "@")) else normalized
