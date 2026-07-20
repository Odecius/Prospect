import os
import sys

from app.database.session import SessionLocal
from app.repositories.users import UserRepository
from app.services.authentication import AuthenticationService, DuplicateAdministratorError


def required_environment(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"A variável {name} é obrigatória.")
    return value


def main() -> int:
    try:
        email = required_environment("ADMIN_EMAIL")
        display_name = required_environment("ADMIN_DISPLAY_NAME")
        password = required_environment("ADMIN_PASSWORD")
        with SessionLocal() as session:
            service = AuthenticationService(UserRepository(session))
            user = service.create_administrator(email, display_name, password)
        print(f"Administrador criado com sucesso: {user.email_normalized}")
        return 0
    except (DuplicateAdministratorError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
