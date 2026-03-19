from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from modules.users import schemas, curd
from core import security
from database.session import get_db
from core.dependencies import get_current_user

from fastapi.responses import RedirectResponse, HTMLResponse
from modules.users.google_oauth import get_google_auth_url, exchange_code_for_token, get_google_user_info
from modules.users import curd
from core import security


router = APIRouter()

# Type alias for database dependency
DbDependency = Annotated[Session, Depends(get_db)]

@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: DbDependency):
    """
    Register a new user
    """
    # Check if user already exists
    existing_user = curd.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng"
        )
    
    # Create new user
    new_user = curd.create_user(
        db=db,
        email=user.email,
        full_name=user.full_name,
        password=user.password,
        role=user.role
    )
    
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: DbDependency):
    """
    Login user and return access token
    """
    # Verify user credentials
    db_user = curd.get_user_by_email(db, user.email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác"
        )
    
    if not security.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác"
        )
    
    
    # Create access token
    access_token = security.create_access_token(
        data={"sub": db_user.email,
            "role": db_user.role}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": db_user.role,
        "email": db_user.email
    }

@router.get("/profile", response_model=schemas.UserOut)
def get_profile(current_user = Depends(get_current_user)):
    return current_user

@router.get("/google/login")
def google_login():
    """Redirect người dùng đến trang đăng nhập Google"""
    auth_url = get_google_auth_url()
    return RedirectResponse(url=auth_url)

# GG Oauth2 Routes
@router.get("/google/callback")
async def google_callback(code: str, db: DbDependency):
    """
    Google redirect về đây sau khi user đăng nhập thành công.
    Đổi code -> token -> user info -> tạo/lấy user -> trả JWT
    """
    # 1. Đổi code lấy access_token
    token_data = await exchange_code_for_token(code)
    access_token_google = token_data.get("access_token")

    if not access_token_google:
        raise HTTPException(status_code=400, detail="Không nhận được access token từ Google")

    # 2. Lấy thông tin user từ Google
    google_user = await get_google_user_info(access_token_google)
    email = google_user.get("email")
    full_name = google_user.get("name", "")

    if not email:
        raise HTTPException(status_code=400, detail="Không lấy được email từ Google")

    # 3. Tìm hoặc tạo user trong DB
    db_user = curd.get_user_by_email(db, email)
    if not db_user:
        db_user = curd.create_user(
            db=db,
            email=email,
            full_name=full_name,
            password=None,   # User Google không cần password
            role="candidate"
        )

    # 4. Tạo JWT token của hệ thống
    jwt_token = security.create_access_token(data={"sub": db_user.email})

    # 5. Redirect về frontend kèm token
    # ✅ Đổi thành Homepage.html
    return RedirectResponse(
    url=f"http://127.0.0.1:5500/client/page/Homepage.html?token={jwt_token}&email={email}&role={db_user.role}"
)