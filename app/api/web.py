from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(include_in_schema=False)
_index = Path(__file__).resolve().parents[1] / "static" / "index.html"
_privacy = Path(__file__).resolve().parents[1] / "static" / "privacy.html"
_terms = Path(__file__).resolve().parents[1] / "static" / "terms.html"


@router.get("/")
def index() -> FileResponse:
    return FileResponse(_index)


@router.get("/privacy")
def privacy() -> FileResponse:
    return FileResponse(_privacy)


@router.get("/terms")
def terms() -> FileResponse:
    return FileResponse(_terms)
