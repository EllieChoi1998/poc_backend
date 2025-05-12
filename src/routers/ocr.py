# routes/ocr_routes.py (신규 파일)
import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Any
from services.contract_service import ContractService
from models import OcrResultResponse
from repositories.ocr_repository import OcrRepository

router = APIRouter(prefix="/ocr", tags=["OCR"])

@router.get("/status/{ocr_file_id}", response_model=Dict[str, Any])
async def get_ocr_status(ocr_file_id: int):
    """
    OCR 처리 상태를 조회합니다.
    """
    ocr_file = OcrRepository.get_ocr_file_by_id(ocr_file_id)
    if not ocr_file:
        raise HTTPException(status_code=404, detail="존재하지 않는 OCR 파일입니다.")
    
    return {
        "ocr_file_id": ocr_file_id,
        "ocr_status": ocr_file["ocr_file_status"].lower(),
        "file_info": ocr_file
    }

@router.get("/result/{contract_id}", response_model=OcrResultResponse)
async def get_ocr_result(contract_id: int):
    """
    계약서의 OCR 처리 결과를 조회합니다.
    """
    result = ContractService.get_contract_ocr_result(contract_id)
    
    if not result.success and result.ocr_status == "not_found":
        raise HTTPException(status_code=404, detail=result.message)
    
    return result