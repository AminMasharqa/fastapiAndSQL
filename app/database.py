from sqlmodel import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os



# Load environment variables from .env file
load_dotenv()

# Get database credentials from environment variables
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT", 5432)),  # Default to 5432 if DB_PORT is not set
}

# Build the SQLALCHEMY_DATABASE_URL from DB_CONFIG
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
)

# Create the database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal=sessionmaker(autocommit=False, autoflush=False,bind=engine)

Base = declarative_base()


# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()