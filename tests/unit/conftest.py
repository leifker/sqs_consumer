import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from project.database_models import Base


@pytest.fixture(scope="module")
def engine():
    return create_engine("sqlite://", echo=True, future=True)


@pytest.fixture(scope="module")
def db_session(engine):
    Base.metadata.create_all(engine)
    session = Session(engine)
    yield session
    session.close()
    Base.metadata.drop_all(engine)
