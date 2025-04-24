from repositories.user_repository import UserRepository
from models import User, LoginModel
from fastapi import HTTPException
import bcrypt
from auth.jwt_utils import create_access_token, create_refresh_token, verify_token
from typing import Dict, Any, List
import logging

class UserService:
    @staticmethod
    def register_user(user: User) -> dict:
        # login_id 중복 확인
        existing_user = UserRepository.find_by_login_id(user.login_id)
        if existing_user:
            raise HTTPException(status_code=400, detail="Login ID already registered")
            
        # ibk_id 중복 확인
        existing_user = UserRepository.find_by_ibk_id(user.ibk_id)
        if existing_user:
            raise HTTPException(status_code=400, detail="IBK ID already registered")
        
        # 비밀번호 해싱
        hashed_password = UserService.hash_password(user.password)
        
        # 사용자 데이터 준비
        user_data = user.dict()
        user_data['password'] = hashed_password
        
        # 사용자 생성
        UserRepository.create_user(user_data)
        
        return {"message": "User registered successfully"}
    
    @staticmethod
    def login_user(login_data: LoginModel) -> dict:
        # 사용자 조회
        user = UserRepository.find_by_login_id(login_data.login_id)
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        
        # 비밀번호 검증
        if not UserService.verify_password(login_data.password, user['password']):
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        # 엑세스 토큰 생성
        access_token = create_access_token(
            data={"sub": user['login_id'], "user_id": user['id'], "ibk_id": user['ibk_id']}
        )
        
        # 리프레시 토큰 생성
        refresh_token = create_refresh_token(
            data={"sub": user['login_id'], "user_id": user['id'], "ibk_id": user['ibk_id']}
        )
        
        # 리프레시 토큰을 DB에 저장
        UserRepository.update_refresh_token(user['id'], refresh_token)
        
        return {
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": user['id'],
            "user_name": user['name']
        }
    
    @staticmethod
    def refresh_token(refresh_token: str) -> dict:
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Refresh token is required")
        
        # 리프레시 토큰 검증
        payload = verify_token(refresh_token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        
        user_id = payload.get("user_id")
        login_id = payload.get("sub")
        ibk_id = payload.get("ibk_id")
        
        # 새로운 엑세스 토큰 발급
        new_access_token = create_access_token(
            data={"sub": login_id, "user_id": user_id, "ibk_id": ibk_id}
        )
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def logout_user(user_id: int) -> dict:
        # 리프레시 토큰 삭제
        UserRepository.update_refresh_token(user_id, None)
        return {"message": "Logout successful"}
    
    @staticmethod
    def hash_password(password: str) -> str:
        # 비밀번호를 솔트와 함께 해싱
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    
    @staticmethod
    def validate_token(token: str) -> dict:
        verified_token = verify_token(token)
        if not verified_token:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return {
            "message": "Access granted",
            "login_id": verified_token.get("sub"),
            "ibk_id": verified_token.get("ibk_id")
        }
    
    @staticmethod
    def get_all_users(user_id: int) -> List[Dict[str, Any]]:
        """
        모든 활성화된 사용자 정보를 가져옵니다.
        SYSTEM ADMINISTRATOR 역할을 가진 사용자만 사용 가능합니다.
        
        Args:
            user_id: 현재 로그인한 사용자의 ID
            
        Returns:
            List[Dict[str, Any]]: 활성화된 모든 사용자 목록
            
        Raises:
            PermissionError: 권한이 없는 사용자가 접근할 경우
            ValueError: 사용자를 찾을 수 없는 경우
        """
        # 현재 사용자 정보 조회
        current_user = UserRepository.find_by_id(user_id)
        if not current_user:
            raise ValueError(f"사용자 ID {user_id}를 찾을 수 없습니다.")
        
        # 권한 검사: SYSTEM ADMINISTRATOR 역할 확인
        if current_user.get('system_role') != 'SYSTEM':
            raise PermissionError("시스템 관리자만 모든 사용자 정보를 조회할 수 있습니다.")
        
        # 저장소에서 모든 사용자 정보 가져오기
        return UserRepository.find_all()