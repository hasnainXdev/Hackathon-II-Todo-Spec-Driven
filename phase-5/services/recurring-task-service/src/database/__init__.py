from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy import event
from typing import Generator
import os
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL - defaults to PostgreSQL, but can be overridden with environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/todo_recurring_task")

# Create the database engine
engine = create_engine(DATABASE_URL, echo=False)  # Set echo=True for SQL debugging


def create_db_and_tables():
    """Create database tables if they don't exist."""
    logger.info("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully.")


def get_session() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    with Session(engine) as session:
        yield session


def get_db_session():
    """Get a database session directly (for non-dependency injection use)."""
    return Session(engine)


# Event listener to update updated_at field before updates
@event.listens_for(SQLModel, 'before_update', propagate=True)
def set_updated_at_timestamp(mapper, connection, target):
    """Automatically update the 'updated_at' field when a record is updated."""
    if hasattr(target, 'updated_at'):
        target.updated_at = datetime.utcnow()


def init_database():
    """Initialize the database with required setup."""
    logger.info("Initializing database...")

    # Create all tables
    create_db_and_tables()

    # Additional initialization can be added here
    logger.info("Database initialization completed.")