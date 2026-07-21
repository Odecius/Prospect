import uuid

import pytest

from app.database.models import Company, PipelineStatus, User
from app.services.pipeline import PipelineService, PipelineValidationError


class PipelineRepositoryFake:
    def __init__(self, status: PipelineStatus) -> None:
        self.company = Company(id=uuid.uuid4(), pipeline_status=status, merged_into_company_id=None)
        self.saved = None

    def get_company(self, _company_id: uuid.UUID) -> Company:
        return self.company

    def add(self, activity: object) -> None:
        self.saved = activity

    def commit(self) -> None:
        pass


def test_pipeline_allows_next_step_and_records_transition() -> None:
    repository = PipelineRepositoryFake(PipelineStatus.NEW)
    activity = PipelineService(repository).transition(
        repository.company.id, PipelineStatus.QUALIFIED, "Critérios mínimos verificados.", User(id=uuid.uuid4())
    )

    assert repository.company.pipeline_status is PipelineStatus.QUALIFIED
    assert activity.previous_status == "NEW"
    assert activity.new_status == "QUALIFIED"


def test_pipeline_rejects_skipping_steps() -> None:
    repository = PipelineRepositoryFake(PipelineStatus.NEW)
    with pytest.raises(PipelineValidationError, match="não permitida"):
        PipelineService(repository).transition(
            repository.company.id, PipelineStatus.WON, "Não pode saltar etapas.", User(id=uuid.uuid4())
        )


def test_do_not_contact_blocks_contact_activity() -> None:
    repository = PipelineRepositoryFake(PipelineStatus.DO_NOT_CONTACT)
    with pytest.raises(PipelineValidationError, match="impede"):
        PipelineService(repository).add_activity(
            repository.company.id, "CONTACT", "Tentativa proibida.", User(id=uuid.uuid4())
        )
