from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(include_in_schema=False)
_index = Path(__file__).resolve().parents[1] / "static" / "index.html"


@router.get("/")
def index() -> FileResponse:
    return FileResponse(_index)
