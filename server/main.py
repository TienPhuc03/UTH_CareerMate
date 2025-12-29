from fastapi import FastAPI
from modules.users import router as user_router
from database.base import test_connection, engine, Base

app = FastAPI(title="Career Mates")

app.include_router(
    user_router.router,
    prefix="/api/auth",
    tags=["Auth"]
)
test_connection()
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to Career Mates API!"}

