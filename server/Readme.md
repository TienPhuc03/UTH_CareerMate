# 1. Cài đặt packages 
cd server
pip install -r requirements.txt

# 2. Cài Redis (nếu chưa có)
# Ubuntu: sudo apt install redis-server
# macOS: brew install redis
redis-server  # Start Redis

# 3. Tạo .env file 
cp .env.example .env
nano .env
# Thêm GEMINI_API_KEY của bạn

# 4. Tạo database 
createdb users_db

# 5. Setup Alembic 
alembic init alembic
# Copy nội dung từ artifact vào alembic/env.py
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head

# 6. Chạy server
python main.py

# 7. Test API
# Mở http://localhost:8000/docs

# 8. Test với Docker (optional)
docker-compose up -d
docker-compose logs -f