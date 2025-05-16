from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from services.contract_service import ContractService
from services.user_service import UserService
from auth.jwt_utils import get_current_user
import os
from typing import List, Dict, Any
from models import Contract, OcrResultResponse

import logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload")
async def upload_contract(
    current_user: Dict[str, Any] = Depends(get_current_user),
    contract_name: str = Form(...),
    file: UploadFile = File(...)
):
     # 임시 파일로 저장
    temp_file_path = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)
    
    try:
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        logger.info(f"파일 업로드: {file.filename}, 크기: {os.path.getsize(temp_file_path)} 바이트")
        
        # # 계약서 업로드 및 OCR 처리
        # returned_result = ContractService.upload_contract(
        #     uploader_id= current_user["id"],
        #     contract_name=contract_name,
        #     file_name=file.filename,
        #     file_path=temp_file_path
        # )
        
        # logger.info(f"업로드 결과 타입: {type(result)}")
        # logger.info(f"업로드 결과: {result}")
        
        # 딕셔너리 반환
        if hasattr(returned_result, "dict"):
            result = returned_result.dict()
        elif hasattr(result, "model_dump"):
            result = returned_result.model_dump()
        else:
            result = returned_result

        return result
    
    except Exception as e:
        logger.error(f"계약서 업로드 중 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"계약서 업로드 중 오류 발생: {str(e)}")
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@router.get("/{contract_id}/ocr", response_model=OcrResultResponse)
async def get_contract_ocr_result(contract_id: int):
    """
    계약서의 OCR 처리 결과를 조회합니다.
    """
    result = ContractService.get_contract_ocr_result(contract_id)
    
    if not result.success and result.ocr_status == "not_found":
        raise HTTPException(status_code=404, detail=result.message)
    
    return result

@router.get("/all")
async def read_all_contracts(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        contract_objects = ContractService.get_all_contracts(user_id=current_user["id"])
        
        results = []
        
        for contract in contract_objects:
            # Convert to dictionary
            if hasattr(contract, "dict"):
                contract_dict = contract.dict()
            elif hasattr(contract, "model_dump"):
                contract_dict = contract.model_dump()
            else:
                contract_dict = contract
                
            # Add user names with safe handling of potentially None IDs
            contract_dict["uploader_name"] = UserService.get_username_by_id(contract_dict.get("uploader_id"))
            contract_dict["checklist_processer_name"] = UserService.get_username_by_id(contract_dict.get("checklist_processer_id"))
            contract_dict["keypoint_processer_name"] = UserService.get_username_by_id(contract_dict.get("keypoint_processer_id"))
            
            # Safely remove ID fields if they exist
            contract_dict.pop("uploader_id", None)
            contract_dict.pop("checklist_processer_id", None)
            contract_dict.pop("keypoint_processer_id", None)
            
            results.append(contract_dict)
            
        return results
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