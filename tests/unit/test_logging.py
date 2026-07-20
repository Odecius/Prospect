import logging

from app.core.logging import configure_logging


def test_logging_uses_configured_level() -> None:
    configure_logging("WARNING")
    assert logging.getLogger().level == logging.WARNING
