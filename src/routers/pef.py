from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services.pef_service import PEFService
from auth.jwt_utils import get_current_user
import os
import shutil
from typing import List, Dict, Any, Optional
from models import InstructionPEF, TransactionHistory
import uuid
from datetime import datetime
# from utils.ai_client import send_to_ai_server  # AI 서버 통신 유틸리티 가정

router = APIRouter()
UPLOAD_DIR = "./pefs/original"

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/pef-start", status_code=status.HTTP_201_CREATED)
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
    user_id = current_user["id"]
    
    # 파일 저장을 위한 고유 파일명 생성
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # 파일 저장
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 저장 중 오류가 발생했습니다: {str(e)}"
        )
    
    # AI 서버로 파일 전송하여 분석 결과 받기
    try:
        
        # ai_result = await send_to_ai_server(file_path)

        ai_result = {
            "pef_data": {
                "is_fund_item": "F",
                "company_detail": "",
                "other_specs_text": "CMA매도 및 원천징수 이자 발급"
            },
            "transaction_data": [
                {
                    "deal_type": "입금",
                    "deal_object": "CMA 매도",
                    "bank_name": "유리은행",
                    "account_number": "110-143-14678941777",
                    "holder_name": "앨리초이",
                    "amount": "279,620,789",
                    "process_date": "2025.12.31"
                },
                {
                    "deal_type": "입금",
                    "deal_object": "CMA 이자",
                    "bank_name": "유리은행",
                    "account_number": "110-143-14678941777",
                    "holder_name": "앨리초이",
                    "amount": "379,211",
                    "process_date": "2025.12.31"
                }
            ]
        }
        
        # AI 결과에서 InstructionPEF 및 TransactionHistory 정보 추출
        pef_data = ai_result.get("pef_data", {})
        transaction_data_list = ai_result.get("transaction_data", [])
        print(transaction_data_list)
        # InstructionPEF 객체 생성 - 명시적으로 모든 필드 설정
        pef = InstructionPEF(
            performer_id=user_id,
            file_name=file.filename,
            created_at=datetime.now(),  # 현재 시간으로 명시적 설정
            is_fund_item=pef_data.get("is_fund_item", "F"),
            company_detail=pef_data.get("company_detail", ""),
            other_specs_text=pef_data.get("other_specs_text", "")
        )
        
        # TransactionHistory 목록 생성
        transactions = []
        if transaction_data_list:
            for tx_data in transaction_data_list:
                # 문자열 날짜를 datetime.date 객체로 변환
                process_date_str = tx_data.get("process_date", "")
                try:
                    if process_date_str:
                        process_date = datetime.strptime(process_date_str, "%Y.%m.%d").date()
                    else:
                        process_date = datetime.now().date()
                except ValueError:
                    process_date = datetime.now().date()
                
                transaction = TransactionHistory(
                    deal_type=tx_data.get("deal_type", ""),
                    deal_object=tx_data.get("deal_object", ""),
                    bank_name=tx_data.get("bank_name", ""),
                    account_number=tx_data.get("account_number", ""),
                    holder_name=tx_data.get("holder_name", ""),
                    amount=tx_data.get("amount", 0),
                    process_date=process_date
                )
                transactions.append(transaction)
        
        # PEF 지시서 및 거래 내역 생성
        instruction_pef_id = PEFService.create_pef_with_transactions(
            user_id=user_id,
            pef=pef,
            transactions=transactions if transactions else None
        )
        
        return {
            "status": "success",
            "message": "PEF 지시서가 성공적으로 처리되었습니다.",
            "instruction_pef_id": instruction_pef_id
        }
        
    except Exception as e:
        # 에러 발생 시 저장한 파일 삭제
        if os.path.exists(file_path):
            os.remove(file_path)
            
        # 예외 추적 정보를 로그에 기록하고 사용자에게는 간략한 메시지만 제공
        import traceback
        print(f"Error details: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 서버 처리 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/all", response_model=List[InstructionPEF])
async def get_all_pefs(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    모든 PEF 지시서 목록 조회
    """
    user_id = current_user["id"]
    pef_instructions = PEFService.get_all_pef_instructions(user_id)
    return pef_instructions

@router.get("/{pef_id}", response_model=Optional[InstructionPEF])
async def get_pef_by_id(
    pef_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    특정 ID의 PEF 지시서 조회
    """
    user_id = current_user["id"]
    pef_instruction = PEFService.get_pef_instruction_by_id(user_id, pef_id)
    
    if not pef_instruction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {pef_id}인 PEF 지시서를 찾을 수 없습니다."
        )
    
    return pef_instruction

@router.get("/{pef_id}/transactions", response_model=List[TransactionHistory])
async def get_transactions_by_pef_id(
    pef_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    특정 PEF 지시서의 모든 거래 내역 조회
    """
    user_id = current_user["id"]
    transactions = PEFService.get_transaction_histories_by_pef_id(user_id, pef_id)
    return transactions

@router.post("/{pef_id}/transactions", status_code=status.HTTP_201_CREATED)
async def add_transaction(
    pef_id: int,
    transaction: TransactionHistory,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    기존 PEF 지시서에 새로운 거래 내역 추가
    """
    user_id = current_user["id"]
    
    # instruction_pef_id 설정
    transaction.instruction_pef_id = pef_id
    
    success = PEFService.add_transaction_to_pef(user_id, pef_id, transaction)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="거래 내역 추가 중 오류가 발생했습니다."
        )
    
    return {
        "status": "success",
        "message": "거래 내역이 성공적으로 추가되었습니다."
    }

@router.put("/transactions/{transaction_id}", status_code=status.HTTP_200_OK)
async def update_transaction(
    transaction_id: int,
    transaction: TransactionHistory,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    거래 내역 정보 업데이트
    """
    user_id = current_user["id"]
    
    # transaction_id 설정
    transaction.id = transaction_id
    
    success = PEFService.update_transaction_history(user_id, transaction)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {transaction_id}인 거래 내역을 찾을 수 없습니다."
        )
    
    return {
        "status": "success",
        "message": "거래 내역이 성공적으로 업데이트되었습니다."
    }

@router.delete("/{pef_id}", status_code=status.HTTP_200_OK)
async def delete_pef(
    pef_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    PEF 지시서 삭제
    """
    user_id = current_user["id"]
    success = PEFService.delete_pef_instruction(user_id, pef_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {pef_id}인 PEF 지시서를 찾을 수 없습니다."
        )
    
    return {
        "status": "success",
        "message": "PEF 지시서가 성공적으로 삭제되었습니다."
    }

@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_200_OK)
async def delete_transaction_history(
    transaction_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    거래 내역 삭제
    """
    user_id = current_user["id"]
    success = PEFService.delete_transaction(user_id, transaction_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {transaction_id}인 거래 내역을 찾을 수 없습니다."
        )
    
    return {
        "status": "success",
        "message": "거래 내역이 성공적으로 삭제되었습니다."
    }