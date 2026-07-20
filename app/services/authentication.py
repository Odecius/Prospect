import uuid

from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password, normalize_email, verify_password
from app.database.models import User, UserStatus
from app.repositories.users import UserRepository


class DuplicateAdministratorError(Exception):
    pass


class AuthenticationService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def authenticate(self, email: str, password: str) -> User | None:
        try:
            normalized = normalize_email(email)
        except ValueError:
            return None
        user = self.repository.get_by_email(normalized)
        if user is None or user.status is not UserStatus.ACTIVE or not verify_password(user.password_hash, password):
            return None
        self.repository.record_login(user)
        self.repository.commit()
        return user

    def get_active_user(self, user_id: str) -> User | None:
        try:
            parsed_id = uuid.UUID(user_id)
        except ValueError:
            return None
        user = self.repository.get_by_id(parsed_id)
        return user if user is not None and user.status is UserStatus.ACTIVE else None

    def create_administrator(self, email: str, display_name: str, password: str) -> User:
        normalized = normalize_email(email)
        name = display_name.strip()
        if not name or len(name) > 120:
            raise ValueError("O nome deve conter entre 1 e 120 caracteres.")
        if self.repository.get_by_email(normalized) is not None:
            raise DuplicateAdministratorError("Já existe um administrador com este email.")
        user = User(
            email_normalized=normalized,
            display_name=name,
            password_hash=hash_password(password),
            status=UserStatus.ACTIVE,
        )
        self.repository.add(user)
        try:
            self.repository.commit()
        except IntegrityError as error:
            self.repository.rollback()
            raise DuplicateAdministratorError("Já existe um administrador com este email.") from error
        return user
