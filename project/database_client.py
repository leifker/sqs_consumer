from sqlalchemy.orm import Session
import logging
logger = logging.getLogger(__name__)


class DatabaseClient:
    """
    Client wrapper for managing database connections
    """

    def __init__(self, engine):
        self._engine = engine
        self._session = Session(self._engine)
        logger.info("Database session active.")

    def add_all(self, rows):
        self._session.add_all(rows)
        self._session.commit()
