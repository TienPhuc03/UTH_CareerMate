
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import declarative_base

DATABASE_URL = "postgresql://postgres:106006@localhost:5432/users_db"

engine = create_engine(
    DATABASE_URL,
    echo=True
)


Base = declarative_base()

#test connect db
def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Kết nối csdl thành công!!! :))", result.scalar())
    except Exception as e:
        print("Kết nối csdl thất bại :((", e) 