"""Test fixtures for backend tests."""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.api.deps import get_db, get_current_user
from app.models import User


# Test database
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database session for each test."""
    SQLModel.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        SQLModel.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_user(db: Session):
    """Create a test user."""
    user = User(
        telegram_user_id="123456789",
        username="test_user",
        first_name="Test",
        last_name="User",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def mock_auth():
    """Mock authentication token."""
    return "mock_token"


@pytest.fixture(scope="function")
def client(db: Session, test_user: User):
    """Create a test client with mocked dependencies."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    def override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
