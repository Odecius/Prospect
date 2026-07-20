import os

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://test:test@localhost/test")
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("APP_SECRET_KEY", "test-only-secret-key-at-least-32-chars")
