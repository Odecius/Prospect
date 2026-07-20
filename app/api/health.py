from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["infrastructure"])


class HealthResponse(BaseModel):
    status: Literal["ok"]


@router.get("/health", response_model=HealthResponse, summary="Verificar disponibilidade da aplicação")
def health() -> HealthResponse:
    return HealthResponse(status="ok")
