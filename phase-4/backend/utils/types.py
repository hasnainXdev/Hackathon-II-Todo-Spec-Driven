from sqlalchemy.types import TypeDecorator
import uuid
import sqlalchemy as sa
from sqlalchemy import String


# Custom type to ensure UUIDs are stored and retrieved as strings
class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Stores UUIDs as VARCHAR/TEXT to avoid type conflicts.
    """
    impl = String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        # Always use VARCHAR/TEXT to avoid UUID type conflicts
        return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif isinstance(value, str):
            # Ensure it's a valid UUID string format
            try:
                uuid.UUID(value)
                # Return as string to ensure consistency
                return value
            except ValueError:
                # If it's not a valid UUID string, return as-is
                return value
        elif isinstance(value, uuid.UUID):
            # Convert to string to ensure consistency
            return str(value)
        else:
            # Convert to string to ensure consistency
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            # Ensure we always return a string
            return str(value)

    def compare_values(self, x, y):
        # Ensure proper string comparison for UUID values
        return str(x) == str(y)