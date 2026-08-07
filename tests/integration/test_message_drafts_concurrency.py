import os
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.ai.openai_responses import OpenAIResponseError
from app.ai.providers import DraftGeneration
from app.database.models import Category, Company, GeneratedMessage, MessageDraftStatus, User
from app.database.session import create_database_engine
from app.repositories.message_drafts import MessageDraftRepository
from app.services.external_search import RequestLimiter
from app.services.message_drafts import (
    AIDailyLimitExceededError,
    DiagnosticLimitExceededError,
    MessageDraftService,
)

pytestmark = pytest.mark.skipif(os.getenv("RUN_DATABASE_TESTS") != "true", reason="requer PostgreSQL descartável")


class CountingProvider:
    model = "gpt-5.6-luna"

    def __init__(self, fail: bool = False) -> None:
        self.calls = 0
        self.fail = fail
        self._lock = threading.Lock()

    def generate(self, _context: dict) -> DraftGeneration:
        with self._lock:
            self.calls += 1
        time.sleep(0.1)
        if self.fail:
            raise OpenAIResponseError("falha simulada")
        return DraftGeneration("Assunto", "Corpo", [], "openai", self.model, {})


def _seed(engine, existing_drafts: int = 0):
    suffix = uuid.uuid4().hex
    with Session(engine) as session:
        user = User(
            email_normalized=f"ai-concurrency-{suffix}@example.invalid",
            display_name="Teste concorrente",
            password_hash="test-only-hash",
        )
        category = Category(name=f"Categoria {suffix}", name_normalized=f"categoria {suffix}", slug=f"cat-{suffix}")
        session.add_all([user, category])
        session.flush()
        company = Company(
            legal_or_trade_name="Empresa concorrente",
            name_normalized=f"empresa concorrente {suffix}",
            category_id=category.id,
            city="Recife",
            state_code="PE",
            created_by_user_id=user.id,
            updated_by_user_id=user.id,
        )
        session.add(company)
        session.flush()
        for index in range(existing_drafts):
            session.add(
                GeneratedMessage(
                    company_id=company.id,
                    status=MessageDraftStatus.DRAFT,
                    draft_type="COMMERCIAL_INTRODUCTION",
                    provider="openai",
                    model="gpt-5.6-luna",
                    prompt_version="test-v1",
                    generated_content={"subject": f"Assunto {index}", "body": "Corpo"},
                    input_snapshot={},
                    usage={},
                    requested_by_user_id=user.id,
                    created_at=datetime.now(UTC),
                )
            )
        session.commit()
        return user.id, category.id, company.id


def _generate(engine, provider, user_id, company_id, draft_type, barrier):
    with Session(engine) as session:
        actor = session.get(User, user_id)
        barrier.wait()
        return MessageDraftService(MessageDraftRepository(session), provider, RequestLimiter(100), True).generate(
            company_id, actor, draft_type
        )


def _run_pair(engine, provider, user_id, company_id, draft_type):
    barrier = threading.Barrier(2)
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(_generate, engine, provider, user_id, company_id, draft_type, barrier) for _ in range(2)
        ]
    results = []
    for future in futures:
        try:
            results.append(future.result())
        except Exception as error:  # noqa: BLE001 - the test asserts the exact concurrent outcome below
            results.append(error)
    return results


def _cleanup(engine, user_id, category_id, company_id):
    with Session(engine) as session:
        session.execute(delete(Company).where(Company.id == company_id))
        session.execute(delete(Category).where(Category.id == category_id))
        session.execute(delete(User).where(User.id == user_id))
        session.commit()


def test_daily_limit_is_atomic_at_nineteen_of_twenty() -> None:
    engine = create_database_engine(os.environ["DATABASE_URL"])
    user_id, category_id, company_id = _seed(engine, existing_drafts=19)
    provider = CountingProvider()
    try:
        results = _run_pair(engine, provider, user_id, company_id, "COMMERCIAL_INTRODUCTION")
        assert provider.calls == 1
        assert sum(isinstance(item, GeneratedMessage) for item in results) == 1
        assert sum(isinstance(item, AIDailyLimitExceededError) for item in results) == 1
        with Session(engine) as session:
            count = session.scalar(
                select(func.count()).select_from(GeneratedMessage).where(GeneratedMessage.company_id == company_id)
            )
            assert count == 20
    finally:
        _cleanup(engine, user_id, category_id, company_id)
        engine.dispose()


def test_only_one_concurrent_diagnostic_is_created_per_company() -> None:
    engine = create_database_engine(os.environ["DATABASE_URL"])
    user_id, category_id, company_id = _seed(engine)
    provider = CountingProvider()
    try:
        results = _run_pair(engine, provider, user_id, company_id, "COMMERCIAL_DIAGNOSTIC")
        assert provider.calls == 1
        assert sum(isinstance(item, GeneratedMessage) for item in results) == 1
        assert sum(isinstance(item, DiagnosticLimitExceededError) for item in results) == 1
    finally:
        _cleanup(engine, user_id, category_id, company_id)
        engine.dispose()


def test_provider_failure_leaves_no_partial_message() -> None:
    engine = create_database_engine(os.environ["DATABASE_URL"])
    user_id, category_id, company_id = _seed(engine)
    provider = CountingProvider(fail=True)
    try:
        with Session(engine) as session:
            actor = session.get(User, user_id)
            service = MessageDraftService(MessageDraftRepository(session), provider, RequestLimiter(100), True)
            with pytest.raises(OpenAIResponseError, match="falha simulada"):
                service.generate(company_id, actor)
            session.rollback()
        with Session(engine) as session:
            count = session.scalar(
                select(func.count()).select_from(GeneratedMessage).where(GeneratedMessage.company_id == company_id)
            )
            assert count == 0
    finally:
        _cleanup(engine, user_id, category_id, company_id)
        engine.dispose()
