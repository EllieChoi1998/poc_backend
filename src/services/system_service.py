from repositories.user_repository import UserRepository
from services.user_service import UserService
import os
from fastapi import HTTPException
import bcrypt
from models import User
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 시스템 계정 정보 (환경 변수에서 가져오거나 기본값 사용)
SYSTEM_LOGIN_ID = os.getenv("SYSTEM_LOGIN_ID", "system_admin")
SYSTEM_IBK_ID = os.getenv("SYSTEM_IBK_ID", "system_ibk_id")
SYSTEM_NAME = os.getenv("SYSTEM_NAME", "System Administrator")
SYSTEM_PASSWORD = os.getenv("SYSTEM_PASSWORD", "secureSystemPassword123!")
SYSTEM_HIERARCHY = os.getenv("SYSTEM_HIERARCHY", "ADMIN")
SYSTEM_ROLE = os.getenv("SYSTEM_ROLE", "SYSTEM")

class SystemService:
    @staticmethod
    def initialize_system_account():
        """
        시스템 실행 시 시스템 계정이 없으면 생성
        """
        # 시스템 계정 존재 여부 확인
        system_user = UserRepository.find_by_login_id(SYSTEM_LOGIN_ID)
        
        if not system_user:
            print("시스템 계정이 존재하지 않습니다. 시스템 계정을 생성합니다...")
            
            # 시스템 계정 생성
            system_user = User(
                login_id=SYSTEM_LOGIN_ID,
                ibk_id=SYSTEM_IBK_ID,
                name=SYSTEM_NAME,
                password=SYSTEM_PASSWORD,
                hiearchy=SYSTEM_HIERARCHY,
                system_role=SYSTEM_ROLE,
                activate="T"
            )
            
            # 시스템 계정 등록
            try:
                hashed_password = UserService.hash_password(system_user.password)
                
                # 사용자 데이터 준비
                user_data = system_user.dict()
                user_data['password'] = hashed_password
                
                # 사용자 생성
                UserRepository.create_user(user_data)
                print("시스템 계정 생성이 완료되었습니다.")
                
            except Exception as e:
                print(f"시스템 계정 생성 중 오류 발생: {str(e)}")
                raise e
        else:
            print("시스템 계정이 이미 존재합니다.")
    
    @staticmethod
    def is_system_user(user_id: int) -> bool:
        """
        시스템 계정인지 확인하는 함수
        """
        user = UserRepository.find_by_id(user_id)
        
        if not user:
            return False
            
        return user['system_role'] == SYSTEM_ROLE