from repositories.user_repository import UserRepository
from models import User, LoginModel
from fastapi import HTTPException
import bcrypt
from auth.jwt_utils import create_access_token, create_refresh_token, verify_token
from typing import Dict, Any, List
import logging

class UserService:
    @staticmethod
    def check_system_admin(user_id: int) -> Dict[str, Any]:
        """
        사용자가 시스템 관리자인지 확인하고 사용자 정보를 반환합니다.
        
        Args:
            user_id: 확인할 사용자 ID
            
        Returns:
            Dict[str, Any]: 사용자 정보
            
        Raises:
            ValueError: 사용자를 찾을 수 없는 경우
            PermissionError: 사용자가 시스템 관리자가 아닌 경우
        """
        # 현재 사용자 정보 조회
        current_user = UserRepository.find_by_id(user_id)
        if not current_user:
            raise ValueError(f"사용자 ID {user_id}를 찾을 수 없습니다.")
        
        if current_user.get('system_role') != 'SYSTEM':
            raise PermissionError("이 작업은 시스템 관리자만 수행할 수 있습니다.")
            
        return current_user

    @staticmethod
    def register_user(current_user_id: int, user: User) -> dict:
        """
        새 사용자를 등록합니다.
        시스템 관리자(SYSTEM) 권한을 가진 사용자만 등록할 수 있습니다.

        Args:
            current_user_id: 현재 로그인한 사용자 ID
            user: 생성할 사용자 정보

        Returns:
            dict: 성공 메시지

        Raises:
            PermissionError: 권한이 없는 경우
            ValueError: 사용자 중복 또는 등록 실패
        """
        # 시스템 관리자 권한 확인
        UserService.check_system_admin(current_user_id)
        
        # login_id 중복 확인
        if UserRepository.find_by_login_id(user.login_id):
            raise ValueError(f"로그인 ID '{user.login_id}'는 이미 등록되어 있습니다.")

        # ibk_id 중복 확인
        if UserRepository.find_by_ibk_id(user.ibk_id):
            raise ValueError(f"IBK ID '{user.ibk_id}'는 이미 등록되어 있습니다.")

        # 비밀번호 해싱
        hashed_password = UserService.hash_password(user.password)

        # 사용자 데이터 준비 및 생성
        user_data = user.dict()
        user_data['password'] = hashed_password

        UserRepository.create_user(user_data)

        return {"message": "사용자가 성공적으로 등록되었습니다."}
    
    @staticmethod
    def login_user(login_data: LoginModel) -> dict:
        # 사용자 조회
        user = UserRepository.find_by_login_id(login_data.login_id)
        if not user:
            raise HTTPException(status_code=400, detail="사용자를 찾을 수 없습니다.")
        
        # 비활성화된 사용자 확인
        if user['activate'] != 'T':
            raise HTTPException(status_code=400, detail="비활성화된 계정입니다. 관리자에게 문의하세요.")
        
        # 비밀번호 검증
        if not UserService.verify_password(login_data.password, user['password']):
            raise HTTPException(status_code=400, detail="로그인 정보가 올바르지 않습니다.")
        
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
            "message": "로그인에 성공했습니다.",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": user['id'],
            "user_name": user['name'],
            "system_role": user['system_role']
        }
    
    @staticmethod
    def refresh_token(refresh_token: str) -> dict:
        if not refresh_token:
            raise HTTPException(status_code=400, detail="리프레시 토큰이 필요합니다.")
        
        # 리프레시 토큰 검증
        payload = verify_token(refresh_token)
        if not payload:
            raise HTTPException(status_code=401, detail="유효하지 않거나 만료된 리프레시 토큰입니다.")
        
        user_id = payload.get("user_id")
        login_id = payload.get("sub")
        ibk_id = payload.get("ibk_id")
        
        # 사용자 확인 및 활성화 상태 확인
        user = UserRepository.find_by_id(user_id)
        if not user or user.get('activate') != 'T':
            raise HTTPException(status_code=401, detail="비활성화되었거나 존재하지 않는 사용자입니다.")
        
        # 저장된 리프레시 토큰과 일치하는지 확인
        if user.get('refresh_token') != refresh_token:
            raise HTTPException(status_code=401, detail="유효하지 않은 리프레시 토큰입니다.")
        
        # 새로운 엑세스 토큰 발급
        new_access_token = create_access_token(
            data={"sub": login_id, "user_id": user_id, "ibk_id": ibk_id}
        )
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
        }
    
    @staticmethod
    def logout_user(user_id: int) -> dict:
        # 사용자 존재 확인
        user = UserRepository.find_by_id(user_id)
        if not user:
            raise ValueError(f"사용자 ID {user_id}를 찾을 수 없습니다.")
            
        # 리프레시 토큰 삭제
        UserRepository.update_refresh_token(user_id, None)
        return {"message": "로그아웃에 성공했습니다."}
    
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
            raise HTTPException(status_code=401, detail="유효하지 않거나 만료된 토큰입니다.")
        
        return {
            "message": "접근이 허용되었습니다.",
            "login_id": verified_token.get("sub"),
            "ibk_id": verified_token.get("ibk_id")
        }
    
    @staticmethod
    def get_all_users(user_id: int) -> List[Dict[str, Any]]:
        """
        모든 활성화된 사용자 정보를 가져옵니다.
        SYSTEM 역할을 가진 사용자만 사용 가능합니다.
        
        Args:
            user_id: 현재 로그인한 사용자의 ID
            
        Returns:
            List[Dict[str, Any]]: 활성화된 모든 사용자 목록
            
        Raises:
            PermissionError: 권한이 없는 사용자가 접근할 경우
            ValueError: 사용자를 찾을 수 없는 경우
        """
        # 시스템 관리자 권한 확인
        UserService.check_system_admin(user_id)
        
        # 저장소에서 모든 사용자 정보 가져오기
        return UserRepository.find_all()
    
    @staticmethod
    def update_user(current_user_id: int, user_id: int, user_data: User) -> Dict[str, Any]:
        """
        사용자 정보를 업데이트합니다.
        SYSTEM 역할을 가진 사용자만 다른 사용자를 업데이트할 수 있습니다.
        일반 사용자는 자신의 정보만 업데이트할 수 있습니다.
        
        Args:
            current_user_id: 현재 로그인한 사용자의 ID
            user_id: 업데이트할 사용자의 ID
            user_data: 업데이트할 사용자 데이터
            
        Returns:
            Dict[str, Any]: 업데이트된 사용자 정보
            
        Raises:
            PermissionError: 권한이 없는 사용자가 접근할 경우
            ValueError: 사용자를 찾을 수 없는 경우, 업데이트에 실패한 경우
        """
        # 현재 사용자 정보 조회
        current_user = UserRepository.find_by_id(current_user_id)
        if not current_user:
            raise ValueError(f"사용자 ID {current_user_id}를 찾을 수 없습니다.")
        
        # 타겟 사용자 정보 조회
        target_user = UserRepository.find_by_id(user_id)
        if not target_user:
            raise ValueError(f"업데이트할 사용자 ID {user_id}를 찾을 수 없습니다.")
        
        # 권한 검사
        is_admin = current_user.get('system_role') == 'SYSTEM'
        is_self = current_user_id == user_id
        
        if not (is_admin or is_self):
            raise PermissionError("자신의 정보 또는 시스템 관리자만 사용자 정보를 수정할 수 있습니다.")
        
        # 일반 사용자는 특정 필드만 수정 가능
        user_dict = user_data.dict(exclude_unset=True)
        if not is_admin:
            # 관리자가 아닌 경우 수정 불가능한 필드 제외
            restricted_fields = ['system_role', 'activate', 'hiearchy', 'team_id']
            for field in restricted_fields:
                user_dict.pop(field, None)
        
        # 비밀번호 업데이트가 포함된 경우 해싱 처리
        if 'password' in user_dict and user_dict['password']:
            user_dict['password'] = UserService.hash_password(user_dict['password'])
        
        # 사용자 정보 업데이트
        success = UserRepository.update(user_id, user_dict)
        if not success:
            raise ValueError(f"사용자 ID {user_id} 업데이트에 실패했습니다.")
        
        # 업데이트된 사용자 정보 반환
        updated_user = UserRepository.find_by_id(user_id)
        if not updated_user:
            raise ValueError(f"업데이트된 사용자 정보를 조회할 수 없습니다.")
        
        return updated_user
    
    @staticmethod
    def delete_user(current_user_id: int, user_id: int) -> bool:
        """
        사용자를 삭제합니다.
        SYSTEM 역할을 가진 사용자만 다른 사용자를 삭제할 수 있습니다.
        
        Args:
            current_user_id: 현재 로그인한 사용자의 ID
            user_id: 삭제할 사용자의 ID
            
        Returns:
            bool: 삭제 성공 여부
            
        Raises:
            PermissionError: 권한이 없는 사용자가 접근할 경우
            ValueError: 사용자를 찾을 수 없는 경우, 삭제에 실패한 경우
        """
        # 시스템 관리자 권한 확인
        UserService.check_system_admin(current_user_id)
        
        # 타겟 사용자 정보 조회
        target_user = UserRepository.find_by_id(user_id)
        if not target_user:
            raise ValueError(f"삭제할 사용자 ID {user_id}를 찾을 수 없습니다.")
        
        # 자기 자신은 삭제할 수 없음
        if current_user_id == user_id:
            raise ValueError("자기 자신은 삭제할 수 없습니다.")
        
        # 사용자 삭제 (비활성화)
        success = UserRepository.delete(user_id)
        if not success:
            raise ValueError(f"사용자 ID {user_id} 삭제에 실패했습니다.")
        
        return True