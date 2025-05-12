# services/ocr_service.py (신규 파일)
import os
import logging
import time
import concurrent.futures
from datetime import datetime
from typing import List, Dict, Any, Optional, TypeVar, TYPE_CHECKING

from models import (
    OcrEngineType, OcrFileStatus, OcrStatus, OcrResult,
    OcrFileCreate, OcrFileUpdate, OcrProcessResponse
)
from services.ocr_engine import OcrEngine
from repositories.ocr_repository import OcrRepository
from config import OCR_LICENSE_KEY, OCR_SERVER_ADDR

logger = logging.getLogger(__name__)


# OcrService 타입을 위한 타입 변수 정의
T = TypeVar('T', bound='OcrService')

class OcrService:
    # 클래스 변수로 싱글톤 인스턴스 저장
    _instance = None
    
    @classmethod
    def initialize(cls, license_key: str, server_addr: str, max_workers: int = 5):
        """
        OCR 서비스를 초기화하고 전역 인스턴스를 생성합니다.
        
        Args:
            license_key: OCR 라이센스 키
            server_addr: OCR 서버 주소
            max_workers: 동시 작업 처리 가능한 워커 수
        """
        cls._instance = cls(license_key, server_addr, max_workers)
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        """
        초기화된 OCR 서비스 인스턴스를 반환합니다.
        인스턴스가 없으면 기본 설정으로 생성합니다.
        """
        if cls._instance is None:
            cls._instance = cls(OCR_LICENSE_KEY, OCR_SERVER_ADDR)
        return cls._instance
    
    def __init__(self, license_key: str = OCR_LICENSE_KEY, server_addr: str = OCR_SERVER_ADDR, max_workers: int = 5):
        self.license_key = license_key
        self.server_addr = server_addr
        self.max_workers = max_workers
        self._engine = OcrEngine.create_ocr_engine(license_key, server_addr)
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    
    def process_file(self, file_path: str, contract_id: Optional[int] = None) -> OcrProcessResponse:
        """
        파일 OCR 처리를 시작합니다.
        
        Args:
            file_path: OCR 처리할 파일 경로
            contract_id: 연결된 계약서 ID (선택 사항)
            
        Returns:
            OcrProcessResponse: OCR 처리 요청 결과 정보
        """
        try:
            # OCR 파일 정보 저장
            file_name = os.path.basename(file_path)
            created_date = datetime.now()
            
            ocr_file = OcrFileCreate(
                file_name=file_name,
                file_path=file_path,
                engine_type=OcrEngineType.GMS,
                ocr_file_status=OcrFileStatus.READY,
                created_date=created_date,
                contract_id=contract_id
            )
            
            # services/ocr_service.py (계속)
            ocr_file_id = OcrRepository.save_ocr_file(ocr_file)
            
            if not ocr_file_id:
                return OcrProcessResponse(
                    success=False,
                    message="OCR 파일 정보 저장에 실패했습니다.",
                    ocr_status="failed"
                )
            
            # 비동기 OCR 처리 시작
            self._executor.submit(self._process_ocr, file_path, ocr_file_id)
            
            return {
                "success": True,
                "message": "OCR 처리가 시작되었습니다.",
                "ocr_file_id": ocr_file_id,
                "ocr_status": "processing"
            }
            
        except Exception as e:
            logger.error(f"OCR 처리 요청 중 오류 발생: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"OCR 처리 요청 중 오류 발생: {str(e)}",
                "ocr_status": "failed"
            }
    
    def _process_ocr(self, file_path: str, ocr_file_id: int):
        """
        실제 OCR 처리를 수행하는 내부 메서드 (비동기 실행)
        
        Args:
            file_path: OCR 처리할 파일 경로
            ocr_file_id: 저장된 OCR 파일 ID
        """
        try:
            # 상태 업데이트: 처리 중
            OcrRepository.update_ocr_file(
                file_id=ocr_file_id,
                update_data=OcrFileUpdate(ocr_file_status=OcrFileStatus.PROCESSING)
            )
            
            # 첫 페이지 OCR 처리
            start_time = time.time()
            ocr_result = self._engine.ocr(
                image_file=file_path,
                page_index="0",
                file_type="local"
            )
            execution_time = time.time() - start_time
            
            # 전체 페이지 수 및 파일 ID 업데이트
            OcrRepository.update_ocr_file(
                file_id=ocr_file_id,
                update_data=OcrFileUpdate(
                    total_page=ocr_result.total_pages,
                    fid=ocr_result.fid
                )
            )
            
            # 첫 페이지 저장
            page_id = OcrRepository.save_ocr_page(
                ocr_file_id=ocr_file_id,
                page=1,  # 1-based page number
                full_text=ocr_result.full_text,
                executed_at=datetime.now(),
                execute_seconds=execution_time,
                ocr_status=OcrStatus.SUCCESS,
                page_file_data=ocr_result.page_file_data,
                rotate=ocr_result.rotate
            )
            
            if page_id and ocr_result.boxes:
                OcrRepository.save_ocr_boxes(page_id, ocr_result.boxes)
            
            # 추가 페이지 처리 (있는 경우)
            for page_idx in range(1, ocr_result.total_pages):
                start_time = time.time()
                page_result = self._engine.ocr(
                    image_file=file_path,
                    page_index=str(page_idx),
                    file_type="local"
                )
                execution_time = time.time() - start_time
                
                page_id = OcrRepository.save_ocr_page(
                    ocr_file_id=ocr_file_id,
                    page=page_idx + 1,  # 1-based page number
                    full_text=page_result.full_text,
                    executed_at=datetime.now(),
                    execute_seconds=execution_time,
                    ocr_status=OcrStatus.SUCCESS,
                    page_file_data=page_result.page_file_data,
                    rotate=page_result.rotate
                )
                
                if page_id and page_result.boxes:
                    OcrRepository.save_ocr_boxes(page_id, page_result.boxes)
            
            # 상태 업데이트: 완료
            OcrRepository.update_ocr_file(
                file_id=ocr_file_id,
                update_data=OcrFileUpdate(ocr_file_status=OcrFileStatus.COMPLETE)
            )
            
            logger.info(f"OCR 처리 완료: 파일 ID {ocr_file_id}, 총 {ocr_result.total_pages}페이지")
            
        except Exception as e:
            logger.error(f"OCR 처리 중 오류 발생: 파일 ID {ocr_file_id}", exc_info=True)
            
            # 상태 업데이트: 오류
            OcrRepository.update_ocr_file(
                file_id=ocr_file_id,
                update_data=OcrFileUpdate(ocr_file_status=OcrFileStatus.ERROR)
            )


# 클래스 외부에 helper 함수 정의
def get_ocr_service() -> OcrService:
    """
    초기화된 OCR 서비스 인스턴스를 반환합니다.
    """
    return OcrService.get_instance()