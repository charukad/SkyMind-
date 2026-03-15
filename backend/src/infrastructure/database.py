from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Get DB URL from env or use default for local docker
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://skymind_user:skymind_password@localhost:5432/skymind_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
