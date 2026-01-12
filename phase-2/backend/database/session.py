from sqlmodel import create_engine, Session
from core.config import settings

# Use a default SQLite database if DATABASE_URL is not set
if settings.DATABASE_URL:
    engine = create_engine(settings.DATABASE_URL)

def get_db():
    with Session(engine) as session:
        yield session