import uuid
from dataclasses import dataclass

from app.database.models import OpportunityScore, User
from app.repositories.scores import ScoreRepository

FORMULA_VERSION = "v1-human-40-30-30"
WEIGHTS = {"fit": 0.4, "reputation": 0.3, "digital_gap": 0.3}


class ScoreValidationError(Exception):
    pass


@dataclass(frozen=True)
class ScoreInput:
    fit: int | None
    reputation: int | None
    digital_gap: int | None
    rationale: str


class ScoreService:
    def __init__(self, repository: ScoreRepository) -> None:
        self.repository = repository

    def list_scores(self, company_id: uuid.UUID) -> list[OpportunityScore]:
        return self.repository.list_scores(company_id)

    def calculate(self, company_id: uuid.UUID, data: ScoreInput, actor: User) -> OpportunityScore:
        company = self.repository.get_company(company_id)
        if company is None or company.archived_at or company.merged_into_company_id:
            raise ScoreValidationError("Empresa ativa não encontrada.")
        rationale = data.rationale.strip()
        if not rationale or len(rationale) > 1000:
            raise ScoreValidationError("Justificativa obrigatória com até 1000 caracteres.")
        values = {key: getattr(data, key) for key in WEIGHTS}
        if any(value is not None and not 0 <= value <= 100 for value in values.values()):
            raise ScoreValidationError("Componentes devem estar entre 0 e 100.")
        missing = [key for key, value in values.items() if value is None]
        total = None if missing else round(sum(values[key] * WEIGHTS[key] for key in WEIGHTS))
        components = {
            key: {"value": values[key], "weight": WEIGHTS[key], "missing": values[key] is None} for key in WEIGHTS
        }
        explanation = f"{rationale} Dados ausentes: {', '.join(missing) if missing else 'nenhum'}."
        score = OpportunityScore(
            company_id=company_id,
            total=total,
            formula_version=FORMULA_VERSION,
            components=components,
            explanation=explanation,
            calculated_by_user_id=actor.id,
        )
        self.repository.add(score)
        self.repository.commit()
        return score
