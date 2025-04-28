from fastapi import APIRouter, HTTPException, Depends, Path, Query
from models import User, LoginModel
from services.user_service import UserService
from auth.jwt_utils import get_current_user
from auth.dependencies import get_system_user
from typing import List, Dict, Any

router = APIRouter()
    
@router.post("/register", response_model=Dict[str, str])
async def register(
    user: User,
    current_user: Dict[str, Any] = Depends(get_system_user)
):
    """
    새 사용자 등록 (시스템 관리자만 가능)
    """
    try:
        current_user_id = current_user["id"]
        return UserService.register_user(current_user_id, user)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="사용자 등록 중 오류가 발생했습니다.")

@router.post("/login")
async def login(login_data: LoginModel):
    """
    사용자 로그인
    """
    try:
        return UserService.login_user(login_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"로그인 처리 중 오류가 발생했습니다.")

@router.post("/refresh")
async def refresh(refresh_data: dict):
    """
    액세스 토큰 갱신
    """
    refresh_token = refresh_data.get("refresh_token")
    try:
        return UserService.refresh_token(refresh_token)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="토큰 갱신 중 오류가 발생했습니다.")

@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    사용자 로그아웃
    """
    try:
        return UserService.logout_user(current_user["id"])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="로그아웃 처리 중 오류가 발생했습니다.")

@router.get("/protected-route")
async def protected_route(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    JWT 인증이 필요한 예제 라우트
    """
    try:

        return {
            "message": "접근이 허용되었습니다.",
            "user_id": current_user["id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_all_users", response_model=Dict[str, List[Dict[str, Any]]])
async def get_all_users(current_user: Dict[str, Any] = Depends(get_system_user)):
    """
    모든 사용자 목록 조회 (시스템 관리자만 가능)
    """
    try:
        users = UserService.get_all_users(current_user["id"])
        return {"users": users}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="사용자 정보 조회 중 오류가 발생했습니다.")
    
@router.put("/{user_id}", response_model=Dict[str, Any])
async def update_user(
    user_data: User, 
    user_id: int = Path(..., title="업데이트할 사용자의 ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    사용자 정보를 업데이트합니다.
    SYSTEM 역할을 가진 사용자는 모든 사용자 정보를 업데이트할 수 있습니다.
    일반 사용자는 자신의 정보만 업데이트할 수 있으며, 일부 필드는 수정할 수 없습니다.
    """
    try:
        current_user_id = current_user["id"]
        updated_user = UserService.update_user(current_user_id, user_id, user_data)
        return updated_user
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="사용자 정보 업데이트 중 오류가 발생했습니다.")
    
@router.delete("/{user_id}", response_model=Dict[str, str])
async def delete_user(
    user_id: int = Path(..., title="삭제할 사용자의 ID"),
    current_user: Dict[str, Any] = Depends(get_system_user)
):
    """
    사용자를 삭제합니다(비활성화).
    SYSTEM 역할을 가진 사용자만 접근 가능합니다.
    """
    try:
        current_user_id = current_user["id"]
        UserService.delete_user(current_user_id, user_id)
        return {"message": f"사용자 ID {user_id}가 성공적으로 삭제되었습니다."}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="사용자 삭제 중 오류가 발생했습니다.")