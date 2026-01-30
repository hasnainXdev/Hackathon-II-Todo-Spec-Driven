from sqlmodel import create_engine, Session
from core.config import settings
import urllib.parse


# Use a default SQLite database if DATABASE_URL is not set
if settings.DATABASE_URL:
    # Configure engine with proper SSL settings for NeonDB
    connect_args = {
        "connect_timeout": 10,
    }

    # Check if it's a PostgreSQL connection and configure SSL appropriately for Neon
    if settings.DATABASE_URL.startswith("postgresql://"):
        # Parse the database URL to modify SSL parameters
        parsed_url = urllib.parse.urlparse(settings.DATABASE_URL)

        # Ensure SSL mode is set to 'require' for NeonDB
        query_params = urllib.parse.parse_qs(parsed_url.query)
        if 'sslmode' not in query_params:
            # Add sslmode=require to the connection string if not present
            separator = '&' if parsed_url.query else '?'
            db_url = f"{settings.DATABASE_URL}{separator}sslmode=require"
        else:
            db_url = settings.DATABASE_URL

        # For NeonDB serverless, we should use connection pooling settings that work well with serverless
        engine = create_engine(
            db_url,
            pool_size=5,              # Small pool size for serverless
            max_overflow=10,          # Allow some overflow connections
            pool_pre_ping=True,       # Verify connections before use
            pool_recycle=300,         # Recycle connections every 5 minutes
            pool_reset_on_return='commit',  # Reset connection on return to pool
            connect_args=connect_args
        )
    else:
        engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
else:
    # Default to SQLite if no DATABASE_URL is provided
    engine = create_engine("sqlite:///./todo_app.db", connect_args={"check_same_thread": False})


def get_session():
    with Session(engine) as session:
        yield session


def get_db():
    with Session(engine) as session:
        yield session