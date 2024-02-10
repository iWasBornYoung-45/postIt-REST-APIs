from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import main
import os

main.load_dotenv()

DATABASE_CNX_STR = os.getenv('POSTGRES_CNX_STR')

engine = create_engine(DATABASE_CNX_STR)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()