from fastapi import APIRouter, HTTPException, Depends, Path, Query
from services.checklist_result_service import ChecklistResultService
from auth.jwt_utils import get_current_user
from typing import List, Dict, Any, Optional
from models import Checklist_Result_Value

router = APIRouter()

@router.get("/", response_model=Dict[str, str])
async def init():
    return {"message": "Contract - Checklist Result Domain Server is running"}

@router.post("/create", response_model=Dict[str, str], dependencies=[Depends(get_current_user)])
async def create_checklist_result(
    contract_id: int,
    checklist_id: int,
    checklist_result_values: Optional[List[Checklist_Result_Value]] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """체크리스트 결과를 생성합니다."""
    try:
        current_user_id = current_user["id"]
        ChecklistResultService.create_result(
            user_id=current_user_id,
            contract_id=contract_id,
            checklist_id=checklist_id,
            checklist_result_values=checklist_result_values
        )
        return {"message": "체크리스트 결과가 성공적으로 생성되었습니다."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류가 발생했습니다.\n{e}")

@router.patch("/update-memo/{checklist_result_id}", response_model=Dict[str, str], dependencies=[Depends(get_current_user)])
async def update_checklist_result_memo(
    checklist_result_id: int = Path(..., description="메모를 업데이트할 체크리스트 결과 ID"),
    memo: str = Query(..., description="업데이트할 메모 내용"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """체크리스트 결과의 메모를 업데이트합니다."""
    try:
        current_user_id = current_user["id"]
        ChecklistResultService.update_memo(
            user_id=current_user_id,
            checklist_result_id=checklist_result_id,
            memo=memo
        )
        return {"message": "체크리스트 결과 메모가 성공적으로 업데이트되었습니다."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류가 발생했습니다.\n{e}")

@router.get("/get-by-contract/{contract_id}", response_model=Dict[str, Any])
async def get_checklist_results_by_contract(
    contract_id: int = Path(..., description="결과를 조회할 계약서 ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """계약서 ID별 체크리스트 결과를 조회합니다."""
    try:
        current_user_id = current_user["id"]
        results = ChecklistResultService.find_all_results_by_contract(
            user_id=current_user_id,
            contract_id=contract_id
        )
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류가 발생했습니다.\n{e}")

@router.delete("/delete-value/{value_id}", response_model=Dict[str, str])
async def delete_checklist_result_value(
    value_id: int = Path(..., description="삭제할 체크리스트 결과 값 ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """체크리스트 결과 값을 삭제합니다."""
    try:
        current_user_id = current_user["id"]
        ChecklistResultService.delete_result_value(
            user_id=current_user_id,
            value_id=value_id
        )
        return {"message": "체크리스트 결과 값이 성공적으로 삭제되었습니다."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류가 발생했습니다.\n{e}")

@router.delete("/delete-result/{result_id}", response_model=Dict[str, str])
async def delete_checklist_result(
    result_id: int = Path(..., description="삭제할 체크리스트 결과 ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """체크리스트 결과를 삭제합니다."""
    try:
        current_user_id = current_user["id"]
        ChecklistResultService.delete_result(
            user_id=current_user_id,
            result_id=result_id
        )
        return {"message": "체크리스트 결과가 성공적으로 삭제되었습니다."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류가 발생했습니다.\n{e}")