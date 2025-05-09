from repositories.user_repository import UserRepository
from typing import Dict, Any

class BaseService:
    @staticmethod
    def validate_user(user_id: int) -> None:
        """
        사용자의 존재 및 활성화 여부를 검증합니다.
        
        Args:
            user_id: 검증할 사용자 ID
        Raises:
            ValueError: 사용자를 찾을 수 없는 경우
            PermissionError: 사용자 계정이 비활성화된 경우
        """
        user = UserRepository.find_by_id(user_id=user_id)
        if not user:
            raise ValueError(f"ID {user_id} 사용자가 존재하지 않습니다.")
        if not UserRepository.find_user_activation(user_id=user_id):
            raise PermissionError(f"사용자 ID {user_id} 계정은 비활성화(삭제)된 계정입니다.")
        
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