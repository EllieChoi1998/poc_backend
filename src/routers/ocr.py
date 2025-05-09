from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Depends
from fastapi.responses import Response, JSONResponse
import logging
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

from services.ocr_service import OcrService, get_ocr_service

# 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

# API 라이센스 키와 서버 주소 환경 변수에서 가져오기
LICENSE_KEY = os.getenv("OCR_LICENSE_KEY")
BASE_URL = os.getenv("OCR_BASE_URL")

# 라우터 생성
router = APIRouter()

# OCR 서비스 초기화 함수
def initialize_ocr_service():
    """OCR 서비스를 초기화합니다."""
    if not LICENSE_KEY or not BASE_URL:
        logger.warning("OCR_LICENSE_KEY 또는 OCR_BASE_URL 환경 변수가 설정되지 않았습니다.")
        return None
    
    logger.info(f"OCR 서비스 초기화: BASE_URL={BASE_URL}")
    return OcrService.initialize(LICENSE_KEY, BASE_URL)

@router.post("/process")
async def process_ocr(
    image_file: UploadFile = File(...),
    fid: str = Form(""),
    page_index: str = Form("0"),
    path: str = Form(""),
    restoration: str = Form(""),
    rot_angle: bool = Form(False),
    bbox_roi: str = Form(""),
    type_: str = Form(...),
    recog_form: bool = Form(False),
    ocr_service: OcrService = Depends(get_ocr_service)
):
    """이미지를 OCR 처리합니다."""
    try:
        ocr_result = await ocr_service.ocr(
            image_file, fid, page_index, path, restoration,
            rot_angle, bbox_roi, type_, recog_form
        )
        
        # OCR 결과에 대한 추가 처리 로직
        # 예: 결과 분석, 검증, 데이터베이스 저장 등
        
        return JSONResponse(content=ocr_result.dict())
    except Exception as e:
        logger.error("OCR 처리 중 오류 발생", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download")
async def download_file(
    path: str = Form(...),
    ocr_service: OcrService = Depends(get_ocr_service)
):
    """파일을 다운로드합니다."""
    try:
        file_content = await ocr_service.download_img(path)
        return Response(content=file_content)
    except Exception as e:
        logger.error("파일 다운로드 중 오류 발생", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/worker-status")
async def worker_status(
    ocr_service: OcrService = Depends(get_ocr_service)
):
    """워커 상태를 확인합니다."""
    try:
        status = await ocr_service.get_worker_status()
        return status
    except Exception as e:
        logger.error("워커 상태 확인 중 오류 발생", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-map")
async def ocr_to_map(
    image_file: UploadFile = File(...),
    fid: str = Form(""),
    page_index: str = Form("0"),
    path: str = Form(""),
    restoration: str = Form(""),
    rot_angle: bool = Form(False),
    bbox_roi: str = Form(""),
    type_: str = Form(...),
    recog_form: bool = Form(False),
    ocr_service: OcrService = Depends(get_ocr_service)
):
    """이미지를 OCR 처리하고 결과를 맵 형태로 반환합니다."""
    try:
        result_map = await ocr_service.ocr_to_map(
            image_file, fid, page_index, path, restoration,
            rot_angle, bbox_roi, type_, recog_form
        )
        return result_map
    except Exception as e:
        logger.error("OCR 맵 변환 중 오류 발생", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# 새로운 엔드포인트: 특정 패턴 추출
@router.post("/extract-pattern")
async def extract_pattern(
    image_file: UploadFile = File(...),
    pattern_type: str = Form(...),  # 예: "주민번호", "계약번호", "금액" 등
    ocr_service: OcrService = Depends(get_ocr_service)
):
    """OCR 처리 후 특정 패턴을 추출합니다."""
    try:
        extraction_result = await ocr_service.extract_pattern(image_file, pattern_type)
        return extraction_result
    except Exception as e:
        logger.error("패턴 추출 중 오류 발생", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# 새로운 엔드포인트: 문서 분류
@router.post("/classify-document")
async def classify_document(
    image_file: UploadFile = File(...),
    ocr_service: OcrService = Depends(get_ocr_service)
):
    """OCR 처리 후 문서 유형을 분류합니다."""
    try:
        # 기본 OCR 처리
        ocr_result = await ocr_service.ocr(
            image_file, "", "0", "", "", False, "", "auto", False
        )
        
        # 여기서 문서 분류 로직을 구현할 수 있음
        # 예: OCR 결과의 텍스트를 분석하여 문서 유형 결정
        document_type = "unknown"
        confidence = 0.0
        
        # 간단한 키워드 기반 분류 예시
        text = ocr_result.full_text.lower()
        if "계약서" in text:
            document_type = "contract"
            confidence = 0.8
        elif "신청서" in text:
            document_type = "application"
            confidence = 0.7
        elif "영수증" in text:
            document_type = "receipt"
            confidence = 0.9
        
        return {
            "document_type": document_type,
            "confidence": confidence,
            "full_text": ocr_result.full_text[:200] + "..." if len(ocr_result.full_text) > 200 else ocr_result.full_text
        }
    except Exception as e:
        logger.error("문서 분류 중 오류 발생", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))