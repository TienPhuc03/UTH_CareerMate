
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from server.modules.users import schemas, curd 
from server.core import security 
from server.database.session import get_db

router = APIRouter()
@router.post("/regsiter")
def register ( user: schemas.UserCreate, db: Session = Depends (get_db)):
    existing_user = curd.get_user_by_email (db, user.email)
    if existing_user:
        raise HTTPException (
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng"
        )
    new_user = curd.create_user (
        db,
        email = user.email,
        full_name = user.full_name,
        password = user.password
    )
    return ("Dăng ký thành công" , new_user)

@router.post("/login")
def login( user: schemas.UserLogin, db: Session = Depends (get_db)):
    db_user = curd.get_user_by_email (db, user.email)
    if not db_user or not security.verify_password (user.password, db_user.hashed_password):
        raise HTTPException (
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác"
        )
    access_token = security.create_access_token (
        data={"sub": db_user.email}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
