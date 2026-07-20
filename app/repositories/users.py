import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_email(self, email_normalized: str) -> User | None:
        return self.session.scalar(select(User).where(User.email_normalized == email_normalized))

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.session.get(User, user_id)

    def add(self, user: User) -> None:
        self.session.add(user)

    def record_login(self, user: User) -> None:
        user.last_login_at = datetime.now(UTC)

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
