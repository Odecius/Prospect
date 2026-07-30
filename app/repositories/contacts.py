import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Company, CompanyMergeAudit, CompanySourceRef, Contact, DuplicateCandidate


class ContactRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_company(self, company_id: uuid.UUID) -> Company | None:
        return self.session.get(Company, company_id)

    def list_contacts(self, company_id: uuid.UUID) -> list[Contact]:
        return list(
            self.session.scalars(select(Contact).where(Contact.company_id == company_id).order_by(Contact.created_at))
        )

    def get_contact(self, contact_id: uuid.UUID) -> Contact | None:
        return self.session.get(Contact, contact_id)

    def find_matching_contacts(self, contact: Contact) -> list[Contact]:
        return list(
            self.session.scalars(
                select(Contact).where(
                    Contact.company_id != contact.company_id,
                    Contact.contact_type == contact.contact_type,
                    Contact.value_normalized == contact.value_normalized,
                    Contact.invalidated_at.is_(None),
                )
            )
        )

    def get_candidate_pair(self, company_a_id: uuid.UUID, company_b_id: uuid.UUID) -> DuplicateCandidate | None:
        return self.session.scalar(
            select(DuplicateCandidate).where(
                DuplicateCandidate.company_a_id == company_a_id,
                DuplicateCandidate.company_b_id == company_b_id,
            )
        )

    def get_active_primary(self, company_id: uuid.UUID, contact_type: object) -> Contact | None:
        return self.session.scalar(
            select(Contact).where(
                Contact.company_id == company_id,
                Contact.contact_type == contact_type,
                Contact.is_primary.is_(True),
                Contact.invalidated_at.is_(None),
            )
        )

    def list_candidates(self) -> list[DuplicateCandidate]:
        return list(self.session.scalars(select(DuplicateCandidate).order_by(DuplicateCandidate.created_at.desc())))

    def get_candidate(self, candidate_id: uuid.UUID) -> DuplicateCandidate | None:
        return self.session.get(DuplicateCandidate, candidate_id)

    def contacts_for_merge(self, company_id: uuid.UUID) -> list[Contact]:
        return self.list_contacts(company_id)

    def source_refs_for_merge(self, company_id: uuid.UUID) -> list[CompanySourceRef]:
        return list(self.session.scalars(select(CompanySourceRef).where(CompanySourceRef.company_id == company_id)))

    def add(self, value: Contact | DuplicateCandidate | CompanyMergeAudit) -> None:
        self.session.add(value)

    def flush(self) -> None:
        self.session.flush()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
