import uuid

from app.database.models import Company, User
from app.services.scores import FORMULA_VERSION, ScoreInput, ScoreService


class ScoreRepositoryFake:
    def __init__(self) -> None:
        self.company = Company(id=uuid.uuid4(), archived_at=None, merged_into_company_id=None)
        self.saved = None

    def get_company(self, _company_id: uuid.UUID) -> Company:
        return self.company

    def add(self, score: object) -> None:
        self.saved = score

    def commit(self) -> None:
        pass


def test_complete_score_is_weighted_and_versioned() -> None:
    repository = ScoreRepositoryFake()
    actor = User(id=uuid.uuid4())
    score = ScoreService(repository).calculate(
        repository.company.id, ScoreInput(fit=80, reputation=70, digital_gap=90, rationale="Avaliação fictícia."), actor
    )

    assert score.total == 80
    assert score.formula_version == FORMULA_VERSION
    assert score.components["fit"] == {"value": 80, "weight": 0.4, "missing": False}


def test_incomplete_score_records_missing_data_without_total() -> None:
    repository = ScoreRepositoryFake()
    score = ScoreService(repository).calculate(
        repository.company.id,
        ScoreInput(fit=80, reputation=None, digital_gap=90, rationale="Reputação ainda não avaliada."),
        User(id=uuid.uuid4()),
    )

    assert score.total is None
    assert score.components["reputation"]["missing"] is True
    assert "reputation" in score.explanation
