# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base


# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:123456@localhost:5432/careermate_db"

# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
from sqlalchemy.orm import sessionmaker
from database.base import engine

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()