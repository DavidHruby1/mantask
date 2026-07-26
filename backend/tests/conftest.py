import os


# Unit and endpoint tests do not connect, but application imports require a valid URL.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:55432/mantask_test",
)
