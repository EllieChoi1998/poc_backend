from fastapi import APIRouter, HTTPException, Depends, Path, Query
from models import User, Checklist
from services.checklist_service import ChecklistService
from auth.jwt_utils import get_current_user
from auth.dependencies import get_system_user
from typing import List, Dict, Any

router = APIRouter()

@router.get("/", response_model=Dict[str,str])
async def init():
    return {"message": "Checklist Domain Server is running"}

@router.post("/add", response_model=Dict[str, str])
async def add_checklist(
    checklist: Checklist,
    current_user: Dict[str, Any] = Depends(get_system_user)
):
    """체크리스트 항목을 추가합니다. 시스템 관리자만 접근 가능합니다."""
    try:
        current_user_id = current_user["id"]
        return ChecklistService.add_question(current_user_id=current_user_id, question=checklist.question)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    
@router.get("/get-all", response_model=List[Checklist])
async def get_all_checklist(current_user: Dict[str, Any] = Depends(get_current_user)):
    """모든 체크리스트 항목을 조회합니다."""
    try:
        return ChecklistService.get_all_questions()
    except Exception as e:
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

@router.put("/edit", response_model=Dict[str, str])
async def update_checklist(
    checklist: Checklist,
    current_user: Dict[str, Any] = Depends(get_system_user)
):
    """체크리스트 항목을 수정합니다. 시스템 관리자만 접근 가능합니다."""
    try:
        current_user_id = current_user["id"]
        return ChecklistService.edit_question(
            current_user_id=current_user_id, 
            checklist_id=checklist.id,
            question=checklist.question
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


@router.delete("/{checklist_id}", response_model=Dict[str, str])
async def delete_checklist(
    checklist_id: int = Path(..., description="삭제할 체크리스트 ID"),
    current_user: Dict[str, Any] = Depends(get_system_user)
):
    """체크리스트 항목을 삭제합니다. 시스템 관리자만 접근 가능합니다."""
    try:
        current_user_id = current_user["id"]
        return ChecklistService.delete_question(
            current_user_id=current_user_id,
            checklist_id=checklist_id
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")