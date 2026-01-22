
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import declarative_base
from core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    echo=True
)   


Base = declarative_base()

#test connect db
def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Kết nối csdl thành công", result.scalar())
            return True
    except Exception as e:
        print("Kết nối csdl thất bại", e) 
        return False