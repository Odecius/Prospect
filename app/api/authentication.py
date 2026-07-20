from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.security import csrf_tokens_match, new_csrf_token
from app.database.models import User
from app.database.session import get_database_session
from app.repositories.users import UserRepository
from app.services.authentication import AuthenticationService

router = APIRouter(prefix="/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=1024)


class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str


class AuthenticatedSessionResponse(BaseModel):
    authenticated: Literal[True]
    user: UserResponse
    csrf_token: str


class AnonymousSessionResponse(BaseModel):
    authenticated: Literal[False]


def get_authentication_service(
    session: Annotated[Session, Depends(get_database_session)],
) -> AuthenticationService:
    return AuthenticationService(UserRepository(session))


def require_current_user(
    request: Request,
    service: Annotated[AuthenticationService, Depends(get_authentication_service)],
) -> User:
    user_id = request.session.get("user_id")
    user = service.get_active_user(user_id) if isinstance(user_id, str) else None
    if user is None:
        request.session.clear()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticação necessária.")
    return user


def require_csrf_token(
    request: Request,
    supplied_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> None:
    if not csrf_tokens_match(request.session.get("csrf_token"), supplied_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token CSRF inválido.")


def user_response(user: User) -> UserResponse:
    return UserResponse(id=str(user.id), email=user.email_normalized, display_name=user.display_name)


@router.post("/login", response_model=AuthenticatedSessionResponse)
def login(
    payload: LoginRequest,
    request: Request,
    service: Annotated[AuthenticationService, Depends(get_authentication_service)],
) -> AuthenticatedSessionResponse:
    user = service.authenticate(payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas.")
    csrf_token = new_csrf_token()
    request.session.clear()
    request.session.update({"user_id": str(user.id), "csrf_token": csrf_token})
    return AuthenticatedSessionResponse(authenticated=True, user=user_response(user), csrf_token=csrf_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    _user: Annotated[User, Depends(require_current_user)],
    _csrf: Annotated[None, Depends(require_csrf_token)],
) -> None:
    request.session.clear()


@router.get("/session", response_model=AuthenticatedSessionResponse | AnonymousSessionResponse)
def session_status(
    request: Request,
    service: Annotated[AuthenticationService, Depends(get_authentication_service)],
) -> AuthenticatedSessionResponse | AnonymousSessionResponse:
    user_id = request.session.get("user_id")
    user = service.get_active_user(user_id) if isinstance(user_id, str) else None
    csrf_token = request.session.get("csrf_token")
    if user is None or not isinstance(csrf_token, str):
        request.session.clear()
        return AnonymousSessionResponse(authenticated=False)
    return AuthenticatedSessionResponse(authenticated=True, user=user_response(user), csrf_token=csrf_token)
