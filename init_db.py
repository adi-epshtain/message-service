"""Initialize database tables."""

from app.db.base import Base
from app.db.session import engine
from app.models import Message  # noqa: F401 - Import to register models

if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

