from fastapi import HTTPException, Header, Depends
from auth.jwt_utils import verify_token, get_current_user
from services.system_service import SystemService

def get_system_user(current_user = Depends(get_current_user)):
    """
    시스템 관리자 권한이 있는지 확인하는 의존성 함수
    """
    user_id = current_user["id"]
    
    if not SystemService.is_system_user(user_id):
        raise HTTPException(
            status_code=403,
            detail="Only system administrators can perform this action"
        )
    
    return current_user