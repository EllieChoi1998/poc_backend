from datetime import datetime, timedelta
from jose import jwt
from typing import Optional
import secrets
import os
from dotenv import load_dotenv
from fastapi import Header, HTTPException
from jose.exceptions import ExpiredSignatureError, JWTError

# Load environment variables
load_dotenv()

# Generate a secure secret key if not exists
def generate_secret_key():
    """Generate a secure secret key for JWT"""
    return secrets.token_hex(32)

# Set up secret key
SECRET_KEY = os.getenv("JWT_SECRET_KEY", generate_secret_key())

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token
    
    :param data: Dictionary containing token payload
    :param expires_delta: Optional expiration time
    :return: Encoded JWT token
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Generate the JWT token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        # 만료된 토큰은 명확하게 401 Unauthorized
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    JWT 리프레시 토큰 생성
    :param data: 토큰에 포함할 데이터 (user_id 등)
    :param expires_delta: 만료 시간 (기본 7일)
    :return: JWT 리프레시 토큰
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.now(datetime.timezone.utc) + timedelta(days=7)  # 기본 7일 설정
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def get_current_user(authorization: str = Header(...)):
    """
    Authorization 헤더로부터 JWT를 받아 유저 정보 반환
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    token = authorization[7:]  # "Bearer " 제거

    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="user_id not found in token")

    return {"id": user_id}