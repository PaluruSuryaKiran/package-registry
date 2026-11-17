import os
from dotenv import load_dotenv
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


load_dotenv()

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError(
        "TEST_DATABASE_URL is not set. Copy .env.example to .env and fill it in."
    )

if TEST_DATABASE_URL == os.environ.get("DATABASE_URL"):
    raise RuntimeError(
        "TEST_DATABASE_URL must differ from DATABASE_URL: the tests drop all tables."
    )

# Point the app at the test database before anything imports package_service.db.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from package_service import models  # noqa: F401  (registers the tables on Base)
from package_service.db import Base
from fastapi.testclient import TestClient
from package_service.main import app

@pytest.fixture
def engine():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def session(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture
def client():
    return TestClient(app)