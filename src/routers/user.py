from fastapi import APIRouter, HTTPException, Depends
from database import get_db_connection
from models import User

router = APIRouter()

@router.post("/register/")
async def register(user: User):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 이메일 중복 체크
    cursor.execute('SELECT * FROM user WHERE email = %s', (user.email,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    # 유저 정보 삽입
    cursor.execute('''INSERT INTO user (email, name, password, team_id, contact) 
                      VALUES (%s, %s, %s, %s, %s)''', 
                   (user.email, user.name, user.password, user.team_id, user.contact))
    conn.commit()
    conn.close()

    return {"message": "User registered successfully"}
