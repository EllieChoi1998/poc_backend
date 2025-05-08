from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from services.contract_service import ContractService
from auth.jwt_utils import get_current_user
import os
import shutil
from typing import List, Dict, Any
from models import Contract

router = APIRouter()
UPLOAD_DIR = "./contracts/original/"

# 디렉토리 생성
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_contract_file(
    file: UploadFile = File(...),
    contract_name: str = Form(...),
    doc_type: str = Form(...),  # 현재는 사용되지 않음. 필요 시 서비스에 반영
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    계약서 파일 업로드 및 DB 등록
    """
    try:
        # 1. 서비스 계층 호출
        result = ContractService.upload_contract(
            uploader_id=current_user["id"],
            contract_name=contract_name,
            file_name=file.filename
        )

        # 2. 파일 저장
        file_path = os.path.join(UPLOAD_DIR, f"{contract_name}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return JSONResponse(content={
            "message": result["message"],
            "file_path": result["file_path"],
            "filename": file.filename
        })

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.get("/all", response_model=List[Contract])
async def read_all_contracts(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        return ContractService.get_all_contracts(user_id=current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    
@router.get("/uploaded", response_model=List[Contract])
async def read_only_uploaded_contracts(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        return ContractService.get_only_uploaded_contracts(user_id=current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    
@router.get("/checklist-onprogress", response_model=List[Contract])
async def read_only_uploaded_contracts(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        return ContractService.get_on_progress_checklist_contracts(user_id=current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    
@router.get("/checklist-finished", response_model=List[Contract])
async def read_only_uploaded_contracts(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        return ContractService.get_finished_checklist_contracts(user_id=current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    
@router.get("/keypoint-onprogress", response_model=List[Contract])
async def read_only_uploaded_contracts(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        return ContractService.get_on_progress_keypoint_contracts(user_id=current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    
@router.get("/keypoint-finished", response_model=List[Contract])
async def read_only_uploaded_contracts(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        return ContractService.get_finished_keypoint_contracts(user_id=current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")