
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import declarative_base
from core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)


Base = declarative_base()

# test connect db
def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Ket noi csdl thanh cong", result.scalar())
            return True
    except Exception as e:
        print("Ket noi csdl that bai", e)
        return False
