# from datetime import datetime, timedelta
# from jose import jwt
# from passlib.context import CryptContext
# from core.config import settings

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """Verify a plain password against a hashed password"""
#     # Truncate password to 72 bytes (bcrypt limit)
#     if isinstance(plain_password, str):
#         plain_password_bytes = plain_password.encode('utf-8')
#         if len(plain_password_bytes) > 72:
#             plain_password = plain_password_bytes[:72].decode('utf-8', errors='ignore')
    
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password: str) -> str:
#     """Hash a password"""
#     # Truncate password to 72 bytes (bcrypt limit)
#     if isinstance(password, str):
#         password_bytes = password.encode('utf-8')
#         if len(password_bytes) > 72:
#             password = password_bytes[:72].decode('utf-8', errors='ignore')
    
#     return pwd_context.hash(password)

# def create_access_token(data: dict) -> str:
#     """Create a JWT access token"""
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
#     return encoded_jwt
from datetime import datetime, timedelta
from jose import jwt
import bcrypt
from core.config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    """Hash a password"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


