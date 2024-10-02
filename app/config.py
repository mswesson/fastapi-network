import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = f'postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_DB")}'
ALEMBIC_DATABASE_URL = f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_DB")}'
TEST_DATABASE_URL = f'postgresql+asyncpg://{os.getenv("TEST_DB_USER")}:{os.getenv("TEST_DB_PASSWORD")}@{os.getenv("TEST_DB_HOST")}:{os.getenv("TEST_DB_PORT")}/{os.getenv("TEST_DB_DB")}'
