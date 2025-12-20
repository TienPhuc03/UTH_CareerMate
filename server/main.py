# main.py
from fastapi import FastAPI
from modules.items import router as item_router
# from modules.users import router as user_router # Sẽ thêm sau

app = FastAPI(title="My Monolithic FastAPI App")

# Gắn router. Thêm prefix để tạo ra URL hoàn chỉnh: /api/v1/items/...
app.include_router(item_router.router, prefix="/api/v1/items", tags=["Items"])

# app.include_router(user_router.router, prefix="/api/v1/users", tags=["Users"])