from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL - Using SQLite for MVP, PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_website_generator.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for development
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True if os.getenv("DEBUG") == "True" else False
    )
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL,
        echo=True if os.getenv("DEBUG") == "True" else False
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database - create all tables"""
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")