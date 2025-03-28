from fastapi import APIRouter, HTTPException, Depends
from database import get_db_connection
from models import User, LoginModel, LogoutRequest
from auth import create_access_token, verify_token, create_refresh_token
import bcrypt

router = APIRouter()


@router.post("/register/")
async def register(user: User):
    print("Register endpoint hit")  # 디버깅을 위한 출력문
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 이메일 중복 확인
        cursor.execute('SELECT * FROM user WHERE email = %s', (user.email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # 비밀번호 해싱
        hashed_password = hash_password(user.password)

        # 사용자 등록 (해시된 비밀번호 저장)
        cursor.execute(
            'INSERT INTO user (email, name, password, team_id, contact, refresh_token) VALUES (%s, %s, %s, %s, %s, %s)',
            (user.email, user.name, hashed_password, user.team_id, user.contact, None)
        )
        conn.commit()

        return {"message": "User registered successfully"}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        cursor.close()
        conn.close()


@router.post("/login/")
async def login(login_data: LoginModel):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 사용자 조회
        cursor.execute('SELECT * FROM user WHERE email = %s', (login_data.email,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=400, detail="User not found")

        # 비밀번호 검증
        if not verify_password(login_data.password, user['password']):
            raise HTTPException(status_code=400, detail="Invalid credentials")

        # 엑세스 토큰 생성
        access_token = create_access_token(
            data={"sub": user['email'], "user_id": user['id']}
        )

        # 리프레시 토큰 생성
        refresh_token = create_refresh_token(
            data={"sub": user['email'], "user_id": user['id']}
        )

        # 리프레시 토큰을 DB에 저장 (선택 사항)
        cursor.execute("UPDATE user SET refresh_token = %s WHERE id = %s", (refresh_token, user['id']))
        conn.commit()

        return {
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": user['id'],
            "user_name": user['name']
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        conn.close()

@router.post("/refresh/")
async def refresh(refresh_data: dict):
    refresh_token = refresh_data.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token is required")

    # 리프레시 토큰 검증
    payload = verify_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user_id = payload.get("user_id")
    user_email = payload.get("sub")

    # 새로운 엑세스 토큰 발급
    new_access_token = create_access_token(
        data={"sub": user_email, "user_id": user_id}
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@router.post("/logout/")
async def logout(logout_data: LogoutRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 리프레시 토큰 삭제 (DB 저장 방식인 경우)
        cursor.execute("UPDATE user SET refresh_token = NULL WHERE id = %s", (logout_data.user_id,))
        conn.commit()

        return {"message": "Logout successful"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()


# Protected route example
@router.get("/protected-route")
async def protected_route(token: str):
    """
    Example of a route that requires JWT authentication
    """
    verified_token = verify_token(token)
    if not verified_token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return {
        "message": "Access granted",
        "user_email": verified_token.get("sub")
    }



def hash_password(password: str) -> str:
    # 비밀번호를 솔트와 함께 해싱
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

import logging

def verify_password(plain_password: str, hashed_password: str) -> bool:
    logging.debug(f"Plain password: {plain_password}")
    logging.debug(f"Hashed password from DB: {hashed_password}")
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )
