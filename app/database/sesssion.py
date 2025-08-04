from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Reemplaza los valores con los reales si no estás usando variables de entorno
DATABASE_URL = f"postgresql://image_user:{DB_PASSWORD}@localhost:5432/image_processor"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
