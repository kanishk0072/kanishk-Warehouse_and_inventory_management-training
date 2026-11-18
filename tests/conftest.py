import os

import pytest
from dotenv import dotenv_values
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from database import Base, get_db, engine as dev_engine
import models
from main import app


# 1. Connect only to the TEST database
@pytest.fixture(scope="session")
def test_engine():
    env = dotenv_values(".env")

    test_url = os.getenv("TEST_DATABASE_URL") or env.get(
        "TEST_DATABASE_URL"
    )

    if not test_url:
        raise RuntimeError("TEST_DATABASE_URL is missing")

    url = make_url(test_url)

    # Safety: Never run tests against development DB
    if url.database != "warehouse_inventory_test":
        raise RuntimeError("Incorrect test database")

    if (
        url.host,
        url.port,
        url.database,
    ) == (
        dev_engine.url.host,
        dev_engine.url.port,
        dev_engine.url.database,
    ):
        raise RuntimeError("Test DB cannot be development DB")

    engine = create_engine(test_url)

    # Create tables only in test database
    Base.metadata.create_all(bind=engine)

    yield engine

    engine.dispose()


# 2. One isolated DB session per test
@pytest.fixture
def db_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()

    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
        expire_on_commit=False,
    )

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


# 3. FastAPI TestClient with test database
@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)