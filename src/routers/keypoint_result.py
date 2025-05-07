from fastapi import APIRouter, HTTPException, Depends, Path, Query
from services.keypoint_result_service import KeypointResultService
from auth.jwt_utils import get_current_user
from typing import List, Dict, Any
from models import AIKeypointResultCreate, KeypointResultCreate

router = APIRouter()

@router.get("/", response_model=Dict[str,str])
async def init():
    return {"message": "Contract - KeyPoint Result Domain Server is running"}

@router.post("/add-by-user", response_model=Dict[str, str], dependencies=[Depends(get_current_user)])
async def add_keypoint_result_by_user(
    keypoint_result: KeypointResultCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """사용자가 키포인트 결과를 추가합니다."""
    try:
        current_user_id = current_user["id"]
        KeypointResultService.add_by_user(
            user_id=current_user_id,
            contract_id=keypoint_result.contract_id,
            termsNconditions_id=keypoint_result.termsNconditions_id
        )
        return {"message": "키포인트 결과가 성공적으로 추가되었습니다."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류가 발생했습니다.\n{e}")

@router.post("/add-by-ai", response_model=Dict[str, str])
async def add_keypoint_result_by_ai(
    keypoint_result: AIKeypointResultCreate
):
    """AI가 키포인트 결과를 추가합니다."""
    try:
        KeypointResultService.add_by_ai(
            match_rate=keypoint_result.match_rate,
            contract_id=keypoint_result.contract_id,
            termsNconditions_id=keypoint_result.termsNconditions_id
        )
        return {"message": "AI 키포인트 결과가 성공적으로 추가되었습니다."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

@router.get("/get-by-contract/{contract_id}", response_model=Dict[str, Any])
async def get_keypoint_results_by_contract(
    contract_id: int = Path(..., description="결과를 조회할 계약서 ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """계약서 ID별 키포인트 결과를 조회합니다."""
    try:
        current_user_id = current_user["id"]
        results = KeypointResultService.get_all_results_by_contract_id(
            user_id=current_user_id,
            contract_id=contract_id
        )
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")

@router.delete("/{keypoint_result_id}", response_model=Dict[str, str])
async def delete_keypoint_result(
    keypoint_result_id: int = Path(..., description="삭제할 키포인트 결과 ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """키포인트 결과를 삭제합니다."""
    try:
        current_user_id = current_user["id"]
        KeypointResultService.delete_keypoint_result(
            user_id=current_user_id,
            keypoint_result_id=keypoint_result_id
        )
        return {"message": "키포인트 결과가 성공적으로 삭제되었습니다."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")