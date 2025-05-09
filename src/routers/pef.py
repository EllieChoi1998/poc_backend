from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from services.contract_service import ContractService
from auth.jwt_utils import get_current_user
import os
import shutil
from typing import List, Dict, Any
from models import InstructionPEF, TransactionHistory

router = APIRouter()
UPLOAD_DIR = "./pefs/original"

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/pef-start")
async def upload_process_pef(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    운용지시서-PEF 파일 업로드 및 
    AI 서버로 파일 전송해서 결과값 두가지 받음.
    1. InstructionPEF - is_fund_item('T' or 'F'), company_detail(text), other_specs_text(text) 
    2. Optional[List[TransactionHistory]]
    받아온 값들로 한번에 instruction_pef, transaction_history에 데이터 저장하는 로직.
    """
    