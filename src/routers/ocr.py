import os
import tempfile
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse, Response
import aiofiles

from models import OcrResult, WorkerStatus
from services.ocr_engine import OcrEngine

router = APIRouter()

# OCR 엔진 의존성 주입 (Dependency Injection)
async def get_ocr_engine():
    # 환경 변수나 설정 파일에서 라이센스 키와 서버 주소를 가져옵니다.
    # 여기서는 예시로 환경 변수를 사용합니다.
    license_key = os.getenv("OCR_LICENSE_KEY")
    base_url = os.getenv("OCR_SERVER_URL")
    
    if not license_key or not base_url:
        raise HTTPException(status_code=500, detail="OCR 서버 설정이 올바르지 않습니다.")
    
    return OcrEngine.create_ocr_engine(license_key, base_url)

@router.post("/ocr/", response_model=OcrResult)
async def ocr_image(
    file: UploadFile = File(...),
    fid: Optional[str] = Form(None),
    page_index: Optional[str] = Form("0"),
    path: Optional[str] = Form(None),
    restoration: Optional[str] = Form(None),
    rot_angle: bool = Form(False),
    bbox_roi: Optional[str] = Form(None),
    type_: str = Form("upload"),
    recog_form: bool = Form(False),
    ocr_engine: OcrEngine = Depends(get_ocr_engine)
):
    """
    이미지 파일에 대해 OCR을 수행합니다.
    """
    try:
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            # 업로드된 파일 내용을 임시 파일에 쓰기
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # OCR 수행
            result = await ocr_engine.ocr(
                temp_file_path, fid, page_index, path,
                restoration, rot_angle, bbox_roi, type_, recog_form
            )
            return result
        finally:
            # 임시 파일 삭제
            os.unlink(temp_file_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ocr-to-map/", response_model=Dict[str, Any])
async def ocr_image_to_map(
    file: UploadFile = File(...),
    fid: Optional[str] = Form(None),
    page_index: Optional[str] = Form("0"),
    path: Optional[str] = Form(None),
    restoration: Optional[str] = Form(None),
    rot_angle: bool = Form(False),
    bbox_roi: Optional[str] = Form(None),
    type_: str = Form("upload"),
    recog_form: bool = Form(False),
    ocr_engine: OcrEngine = Depends(get_ocr_engine)
):
    """
    이미지 파일에 대해 OCR을 수행하고 결과를 Map 형태로 반환합니다.
    """
    try:
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            # 업로드된 파일 내용을 임시 파일에 쓰기
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # OCR 수행 및 Map 변환
            result = await ocr_engine.ocr_to_map(
                temp_file_path, fid, page_index, path,
                restoration, rot_angle, bbox_roi, type_, recog_form
            )
            return result
        finally:
            # 임시 파일 삭제
            os.unlink(temp_file_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download-image/")
async def download_image(
    file_path: str = Form(...),
    ocr_engine: OcrEngine = Depends(get_ocr_engine)
):
    """
    OCR 결과 이미지를 다운로드합니다.
    """
    try:
        image_data = await ocr_engine.download_img(file_path)
        return Response(content=image_data, media_type="application/octet-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/worker-status/", response_model=WorkerStatus)
async def get_worker_status(
    ocr_engine: OcrEngine = Depends(get_ocr_engine)
):
    """
    OCR 워커 상태를 조회합니다.
    """
    try:
        worker_status = await ocr_engine.get_worker_status()
        return worker_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/simple-upload/")
async def simple_upload(file: UploadFile = File(...)):
    """매우 간단한 파일 업로드 테스트"""
    content = await file.read()
    return {
        "filename": file.filename,
        "size": len(content),
        "content_type": file.content_type
    }