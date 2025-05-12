from repositories.contract_repository import ContractRepository
from repositories.user_repository import UserRepository
from typing import List, Dict, Any, Optional
from models import Contract, OcrResult
from base_service import BaseService
from services.ocr_service import OcrService, get_ocr_service
import os
import shutil
import asyncio

import os
import logging
import shutil
from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel
from base_service import BaseService
from repositories.contract_repository import ContractRepository
from repositories.user_repository import UserRepository
from services.ocr_service import OcrService
from models import OcrProcessResponse, OcrResultResponse
from config import OCR_LICENSE_KEY, OCR_SERVER_ADDR

logger = logging.getLogger(__name__)

# 계약 관련 Pydantic 모델
class ContractUploadResponse(BaseModel):
    message: str
    file_path: str
    contract_id: int
    ocr_result: OcrProcessResponse

class ContractService:
    @staticmethod
    def upload_contract(uploader_id: int, contract_name: str, file_name: str, file_path: str) -> ContractUploadResponse:
        """
        새로운 계약서를 업로드하고 OCR 처리를 수행합니다.
        모든 사용자가 업로드 할 수 있습니다.

        Args:
            uploader_id: 현재 로그인하여 파일을 업로드한 사용자 ID
            contract_name: 사용자가 지정한 계약 이름
            file_name: 업로드한 파일 이름
            file_path: 업로드된 파일의 임시 경로
        Returns:
            ContractUploadResponse: 파일 저장 경로 및 OCR 처리 상태 정보
        Raises:
            PermissionError: 활성화된 사용자 여부
            ValueError: 파일 저장 경로 (contract_name, file_name이 모두 중복되는 경우) 중복 또는 등록 실패
        """
        # 사용자 유효성 검사
        BaseService.validate_user(uploader_id)
        
        # 파일 중복 검사
        if ContractRepository.find_by_file_path(contract_name=contract_name, file_name=file_name):
            raise ValueError("이미 존재하는 파일 입니다. 삭제 후 다시 업로드 해 주세요.")
        
        # 계약서 저장 디렉토리 경로
        target_dir = os.path.join("contracts", "original")
        os.makedirs(target_dir, exist_ok=True)
        
        # 최종 저장 경로
        target_path = os.path.join(target_dir, f"{contract_name}_{file_name}")
        
        # 파일 복사
        shutil.copy2(file_path, target_path)
        
        # 계약서 정보 저장
        contract_id = ContractRepository.create_contract(
            uploader_id=uploader_id, 
            contract_name=contract_name, 
            file_name=file_name
        )
        
        if not contract_id:
            # 파일 저장에 실패한 경우 업로드된 파일 삭제
            if os.path.exists(target_path):
                os.remove(target_path)
            raise ValueError("계약서 정보 저장에 실패했습니다.")
        
        # OCR 처리 수행
        ocr_result = {
            "success": False,
            "message": "OCR 처리가 시작되지 않았습니다.",
            "ocr_status": "not_started"
        }
    
        try:
            # OCR 서비스 가져오기
            ocr_service = get_ocr_service()
            
            # OCR 처리 시작
            ocr_response = ocr_service.process_file(target_path, contract_id)
            
            # 응답 처리 - 타입 검사하여 안전하게 변환
            if hasattr(ocr_response, "dict") and callable(getattr(ocr_response, "dict")):
                ocr_result = ocr_response.dict()
            elif hasattr(ocr_response, "model_dump") and callable(getattr(ocr_response, "model_dump")):
                ocr_result = ocr_response.model_dump()
            elif isinstance(ocr_response, dict):
                ocr_result = ocr_response  # 이미 딕셔너리인 경우
            else:
                # 다른 타입인 경우 문자열로 변환하여 포함
                ocr_result = {
                    "success": True,
                    "message": f"OCR 처리가 시작되었습니다. 응답: {str(ocr_response)}",
                    "ocr_status": "processing"
                }
            
            logger.info(f"계약서 OCR 처리 시작: {contract_id}, 결과: {ocr_result}")
            
        except Exception as e:
            logger.error(f"OCR 처리 시작 중 오류 발생: {str(e)}", exc_info=True)
            ocr_result = {
                "success": False,
                "message": f"OCR 처리 시작 중 오류 발생: {str(e)}",
                "ocr_status": "failed"
            }
        
        return ContractUploadResponse(
            message="새로운 계약서가 성공적으로 업로드 되었습니다.", 
            file_path=f"contracts/original/{contract_name}_{file_name}",
            contract_id=contract_id,
            ocr_result=ocr_result
        )
    
    @staticmethod
    def get_contract_ocr_result(contract_id: int) -> OcrResultResponse:
        """
        계약서의 OCR 처리 결과를 조회합니다.
        
        Args:
            contract_id: 계약서 ID
        Returns:
            OcrResultResponse: OCR 처리 결과 정보
        """
        from repositories.ocr_repository import OcrRepository
        
        # 계약서 존재 확인
        contract = ContractRepository.find_by_id(contract_id)
        if not contract:
            return OcrResultResponse(
                success=False,
                message="존재하지 않는 계약서입니다.",
                ocr_status="not_found"
            )
        
        # OCR 결과 조회
        ocr_result = OcrRepository.get_ocr_result_by_contract_id(contract_id)
        if not ocr_result:
            return OcrResultResponse(
                success=False,
                message="OCR 처리 결과가 없습니다.",
                ocr_status="not_found"
            )
        
        # OCR 파일 상태에 따라 응답 생성
        file_info = ocr_result["file_info"]
        ocr_status = file_info["ocr_file_status"]
        
        if ocr_status == "PROCESSING":
            return OcrResultResponse(
                success=True,
                message="OCR 처리가 진행 중입니다.",
                ocr_status="processing",
                file_info=file_info
            )
        elif ocr_status == "ERROR":
            return OcrResultResponse(
                success=False,
                message="OCR 처리 중 오류가 발생했습니다.",
                ocr_status="error",
                file_info=file_info
            )
        elif ocr_status == "COMPLETE":
            # 완성된 OCR 결과 반환
            return OcrResultResponse(
                success=True,
                message="OCR 처리가 완료되었습니다.",
                ocr_status="complete",
                ocr_result=ocr_result
            )
        else:
            # 기타 상태
            return OcrResultResponse(
                success=True,
                message=f"OCR 상태: {ocr_status}",
                ocr_status=ocr_status.lower(),
                file_info=file_info
            )

    @staticmethod
    def get_all_contracts(user_id: int) -> List[Contract]:
        BaseService.validate_user(user_id)
        raw_data = ContractRepository.get_all_contracts()
        
        # ✅ 딕셔너리 형태 그대로 사용
        return [Contract(**row) for row in raw_data]


    @staticmethod
    def get_only_uploaded_contracts(user_id: int) -> List[Contract]:
        BaseService.validate_user(user_id)
        raw_data = ContractRepository.get_only_uploaded_contracts()
        
        # Contract 모델로 객체 생성
        return [Contract(**data) for data in raw_data]
    
    @staticmethod
    def get_on_progress_checklist_contracts(user_id: int) -> List[Contract]:
        BaseService.validate_user(user_id)
        raw_data = ContractRepository.get_on_progress_checklist_contracts()
        
        # Contract 모델로 객체 생성
        return [Contract(**data) for data in raw_data]
    
    @staticmethod
    def get_finished_checklist_contracts(user_id: int) -> List[Contract]:
        BaseService.validate_user(user_id)
        raw_data = ContractRepository.get_finished_checklist_contracts()
        
        # Contract 모델로 객체 생성
        return [Contract(**data) for data in raw_data]
    
    @staticmethod
    def get_on_progress_keypoint_contracts(user_id: int) -> List[Contract]:
        BaseService.validate_user(user_id)
        raw_data = ContractRepository.get_on_progress_keypoint_contracts()
        
        # Contract 모델로 객체 생성
        return [Contract(**data) for data in raw_data]
    
    @staticmethod
    def get_finished_keypoint_contracts(user_id: int) -> List[Contract]:
        BaseService.validate_user(user_id)
        raw_data = ContractRepository.get_finished_keypoint_contracts()

        
        # Contract 모델로 객체 생성
        return [Contract(**data) for data in raw_data]