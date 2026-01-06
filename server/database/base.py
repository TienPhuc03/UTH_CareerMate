
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import declarative_base

DATABASE_URL = "postgresql+psycopg2://postgres:123456@127.0.0.1:5432/careermate_db"

engine = create_engine(
    DATABASE_URL,
    echo=True
)


Base = declarative_base()

# AsyncSessionLocal = sessionmaker(
#     engine,
#     class_=AsyncSession,
#     expire_on_commit=False
# )

#test connect db
def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Kết nối csdl thành công!!! :))", result.scalar())
    except Exception as e:
        print("Kết nối csdl thất bại :((", e)