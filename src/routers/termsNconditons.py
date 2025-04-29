from fastapi import APIRouter, HTTPException, Depends, Path, Query
from models import User, TermsNConditions
from services.termsNconditions_service import TermsNConditionsService
from auth.jwt_utils import get_current_user
from typing import List, Dict, Any

router = APIRouter()

@router.get("/", response_model=Dict[str,str])
async def init():
    return {"message": "Terms And Conditions Domain Server is running"}

@router.post("/add", response_model=Dict[str, str], dependencies=[Depends(get_current_user)])
async def add_termsNconditions(
    termsNcondition: TermsNConditions,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """약관제한목록 항목을 추가합니다. 시스템 관리자만 접근 가능합니다."""
    try:
        current_user_id = current_user["id"]
        return TermsNConditionsService.add_query(current_user_id=current_user_id, code=termsNcondition.code, query=termsNcondition.query)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

    
@router.get("/get-all", response_model=List[Dict[str, Any]])
async def get_all_termsNconditions(current_user: Dict[str, Any] = Depends(get_current_user)):
    """모든 약관제한목록 항목을 조회합니다."""
    try:
        return TermsNConditionsService.get_all_querys()
    except Exception as e:
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

@router.put("/edit", response_model=Dict[str, str])
async def update_termsNconditions(
    termsNcondition: TermsNConditions,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """약관제한목록 항목을 수정합니다. 시스템 관리자만 접근 가능합니다."""
    try:
        current_user_id = current_user["id"]
        return TermsNConditionsService.edit_query(
            current_user_id=current_user_id, 
            termsNconditions_id=termsNcondition.termsNconditions_id,
            query=termsNcondition.query,
            code=termsNcondition.code,
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")


@router.delete("/{termsNconditions_id}", response_model=Dict[str, str])
async def delete_termsNconditions(
    termsNconditions_id: int = Path(..., description="삭제할 약관제한목록 ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """약관제한목록 항목을 삭제합니다. 시스템 관리자만 접근 가능합니다."""
    try:
        current_user_id = current_user["id"]
        return TermsNConditionsService.delete_query(
            current_user_id=current_user_id,
            termsNconditions_id=termsNconditions_id
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")