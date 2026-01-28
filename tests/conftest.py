import pytest
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from core.db import Base, engine, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides = {get_db: override_get_db}
    # Hack to inject DB into app route calls if they use next(get_db()) manually
    # Since my code uses `next(get_db())`, dependency overrides in Flask aren't native like FastAPI.
    # I replaced `next(get_db())` in the code, which creates a NEW session. 
    # For testing, I might need to monkeypatch `core.db.get_db` or ensuring `init_db` uses the test engine.
    
    # Better approach for Flask with this pattern:
    # Modify `core.db` to allow engine override, or minimal monkeypatching.
    
    with app.test_client() as client:
        yield client
