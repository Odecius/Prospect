import uuid
from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError

from app.database.models import (
    CompanyMergeAudit,
    Contact,
    ContactType,
    DuplicateCandidate,
    DuplicateLevel,
    DuplicateStatus,
    PipelineStatus,
    User,
)
from app.domain.normalization import normalize_contact
from app.repositories.contacts import ContactRepository


class ContactValidationError(Exception):
    pass


class ContactService:
    def __init__(self, repository: ContactRepository) -> None:
        self.repository = repository

    def list_contacts(self, company_id: uuid.UUID) -> list[Contact]:
        return self.repository.list_contacts(company_id)

    def create_contact(
        self,
        company_id: uuid.UUID,
        contact_type: ContactType,
        value: str,
        is_primary: bool,
        actor: User,
        person_name: str | None = None,
        job_title: str | None = None,
    ) -> Contact:
        company = self.repository.get_company(company_id)
        if company is None or company.archived_at or company.merged_into_company_id:
            raise ContactValidationError("Empresa ativa não encontrada.")
        if (person_name and len(person_name.strip()) > 120) or (job_title and len(job_title.strip()) > 120):
            raise ContactValidationError("Nome ou cargo excede o limite.")
        try:
            normalized = normalize_contact(contact_type.value, value)
            if is_primary:
                current_primary = self.repository.get_active_primary(company_id, contact_type)
                if current_primary:
                    current_primary.is_primary = False
            contact = Contact(
                company_id=company_id,
                contact_type=contact_type,
                value=value.strip(),
                value_normalized=normalized,
                is_primary=is_primary,
                person_name=person_name.strip() if person_name else None,
                job_title=job_title.strip() if job_title else None,
                created_by_user_id=actor.id,
            )
            self.repository.add(contact)
            self.repository.flush()
            for match in self.repository.find_matching_contacts(contact):
                first, second = sorted((company_id, match.company_id), key=str)
                existing = self.repository.get_candidate_pair(first, second)
                signals = {"contact_type": contact_type.value, "value_normalized": normalized}
                if existing:
                    existing.level = DuplicateLevel.PROBABLE
                    existing.status = DuplicateStatus.OPEN
                    existing.signals = {**existing.signals, **signals}
                else:
                    self.repository.add(
                        DuplicateCandidate(
                            company_a_id=first,
                            company_b_id=second,
                            level=DuplicateLevel.PROBABLE,
                            status=DuplicateStatus.OPEN,
                            signals=signals,
                        )
                    )
            self.repository.commit()
            return contact
        except (IntegrityError, ValueError) as error:
            self.repository.rollback()
            message = "Contato já cadastrado para esta empresa." if isinstance(error, IntegrityError) else str(error)
            raise ContactValidationError(message) from error

    def invalidate(self, contact_id: uuid.UUID) -> Contact | None:
        contact = self.repository.get_contact(contact_id)
        if contact is None:
            return None
        contact.invalidated_at = datetime.now(UTC)
        contact.is_primary = False
        self.repository.commit()
        return contact

    def list_candidates(self) -> list[DuplicateCandidate]:
        return self.repository.list_candidates()

    def review_candidate(
        self, candidate_id: uuid.UUID, status: DuplicateStatus, reason: str, actor: User
    ) -> DuplicateCandidate | None:
        candidate = self.repository.get_candidate(candidate_id)
        if candidate is None:
            return None
        if status not in {
            DuplicateStatus.DISTINCT,
            DuplicateStatus.CONFIRMED_DUPLICATE,
            DuplicateStatus.MERGE_REQUESTED,
        }:
            raise ContactValidationError("Decisão de revisão inválida.")
        if not reason.strip() or len(reason.strip()) > 500:
            raise ContactValidationError("Justificativa obrigatória.")
        candidate.status = status
        candidate.level = DuplicateLevel.DISTINCT if status is DuplicateStatus.DISTINCT else candidate.level
        candidate.decision_reason = reason.strip()
        candidate.reviewed_by_user_id = actor.id
        candidate.reviewed_at = datetime.now(UTC)
        self.repository.commit()
        return candidate

    def merge(self, candidate_id: uuid.UUID, survivor_id: uuid.UUID, reason: str, actor: User) -> CompanyMergeAudit:
        candidate = self.repository.get_candidate(candidate_id)
        if candidate is None or candidate.status not in {
            DuplicateStatus.CONFIRMED_DUPLICATE,
            DuplicateStatus.MERGE_REQUESTED,
        }:
            raise ContactValidationError("Candidato não está aprovado para mesclagem.")
        ids = {candidate.company_a_id, candidate.company_b_id}
        if survivor_id not in ids or not reason.strip():
            raise ContactValidationError("Sobrevivente e justificativa são obrigatórios.")
        merged_id = next(item for item in ids if item != survivor_id)
        survivor = self.repository.get_company(survivor_id)
        merged = self.repository.get_company(merged_id)
        if survivor is None or merged is None or merged.merged_into_company_id:
            raise ContactValidationError("Empresas inválidas para mesclagem.")
        if survivor.archived_at or survivor.merged_into_company_id or merged.archived_at:
            raise ContactValidationError("A mesclagem exige duas empresas ativas.")
        moved = 0
        contacts_preserved = 0
        existing_keys = {
            (item.contact_type, item.value_normalized) for item in self.repository.contacts_for_merge(survivor_id)
        }
        for contact in self.repository.contacts_for_merge(merged_id):
            if (contact.contact_type, contact.value_normalized) in existing_keys:
                contacts_preserved += 1
            else:
                contact.company_id = survivor_id
                existing_keys.add((contact.contact_type, contact.value_normalized))
                moved += 1
        sources_moved = 0
        sources_preserved = 0
        survivor_sources = {
            (item.data_source_id, item.external_id)
            for item in self.repository.source_refs_for_merge(survivor_id)
            if item.external_id
        }
        for source_ref in self.repository.source_refs_for_merge(merged_id):
            key = (source_ref.data_source_id, source_ref.external_id)
            if source_ref.external_id and key in survivor_sources:
                sources_preserved += 1
            else:
                source_ref.company_id = survivor_id
                if source_ref.external_id:
                    survivor_sources.add(key)
                sources_moved += 1
        merged.merged_into_company_id = survivor_id
        merged.archived_at = datetime.now(UTC)
        merged.pipeline_status = PipelineStatus.ARCHIVED
        merged.updated_by_user_id = actor.id
        candidate.status = DuplicateStatus.CLOSED
        audit = CompanyMergeAudit(
            survivor_company_id=survivor_id,
            merged_company_id=merged_id,
            performed_by_user_id=actor.id,
            reason=reason.strip(),
            details={
                "contacts_moved": moved,
                "contacts_preserved_on_archived_company": contacts_preserved,
                "sources_moved": sources_moved,
                "sources_preserved_on_archived_company": sources_preserved,
            },
        )
        self.repository.add(audit)
        self.repository.commit()
        return audit
