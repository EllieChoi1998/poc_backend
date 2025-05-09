from fastapi import APIRouter, File, Form, UploadFile, HTTPException
import httpx
import json
import logging
import os
from typing import Dict, List, Optional, Any, Union
import time
from fastapi.responses import Response, JSONResponse
import io

# 모델 가져오기
from models import Point, OcrBox, OcrResult, WorkerStatus

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OCR 엔진 클래스
class OcrEngine:
    def __init__(self, license_key: str, base_url: str):
        if not license_key or license_key.strip() == "":
            raise ValueError("라이센스 키가 필요합니다.")
        if not base_url or base_url.strip() == "":
            raise ValueError("서버 주소가 필요합니다.")

        # 1. 스킴(http:// 또는 https://)이 없으면 추가
        if not base_url.lower().startswith("http://") and not base_url.lower().startswith("https://"):
            base_url = "http://" + base_url

        # 2. baseUrl의 끝에 있는 슬래시(/) 제거
        base_url = base_url.rstrip("/")

        self.license_key = license_key
        self.ocr_url = f"{base_url}/do-ocr/"
        self.download_url = f"{base_url}/download_file/"
        self.worker_status_url = f"{base_url}/worker-status/"

        # 타임아웃 설정으로 httpx 클라이언트 생성
        self.http_client = httpx.Client(timeout=60.0)

        # 로그
        logger.info(f"OCR URL: {self.ocr_url}")
        logger.info(f"DOWNLOAD URL: {self.download_url}")

    @staticmethod
    def create_ocr_engine(api_key: str, server_addr: str) -> 'OcrEngine':
        if not api_key or api_key.strip() == "":
            raise ValueError("라이센스 키가 필요합니다.")
        
        engine = OcrEngine(api_key, server_addr)
        return engine

    def ocr(self, image_file, fid: str, page_index: str, path: str,
            restoration: str, rot_angle: bool, bbox_roi: str,
            type_: str, recog_form: bool) -> OcrResult:
        return self.process_ocr(image_file, fid, page_index, path, restoration,
                               rot_angle, bbox_roi, type_, recog_form)

    def process_ocr(self, image_file, fid: str, page_index: str, path: str,
                   restoration: str, rot_angle: bool, bbox_roi: str,
                   type_: str, recog_form: bool) -> OcrResult:
        try:
            return self.perform_ocr(image_file, fid, page_index, path, restoration,
                                   rot_angle, bbox_roi, type_, recog_form)
        except Exception as e:
            logger.error(f"OCR 처리 중 오류 발생 (파일: {getattr(image_file, 'filename', 'unknown')})", exc_info=True)
            raise RuntimeError("OCR 처리 실패") from e

    def determine_content_type(self, file_name: str) -> str:
        file_name = file_name.lower()
        if file_name.endswith(".pdf"):
            return "application/pdf"
        elif file_name.endswith(".png"):
            return "image/png"
        elif file_name.endswith(".tiff") or file_name.endswith(".tif"):
            return "image/tiff"
        return "application/octet-stream"

    def perform_ocr(self, image_file, fid: str, page_index: str, path: str,
                   restoration: str, rot_angle: bool, bbox_roi: str,
                   type_: str, recog_form: bool) -> OcrResult:
        # 파일 이름에서 콘텐츠 타입 결정
        try:
            if hasattr(image_file, 'filename'):
                content_type = self.determine_content_type(image_file.filename)
                file_content = image_file.file.read()
                file_name = image_file.filename
            else:
                # 파일 객체인 경우
                file_name = os.path.basename(image_file.name)
                content_type = self.determine_content_type(file_name)
                file_content = image_file.read()
        except AttributeError:
            # bytes나 BytesIO인 경우
            content_type = "application/octet-stream"
            file_content = image_file
            file_name = "file.bin"

        try:
            start_time = time.time()
            
            # 폼 데이터 구성
            files = {'imagefile': (file_name, file_content, content_type)}
            data = {
                'fid': fid or "",
                'page_index': page_index or "0",
                'path': path or "",
                'lic': self.license_key,
                'restoration': restoration or "",
                'rot_angle': str(rot_angle),
                'bbox_roi': bbox_roi or "",
                'type': type_,
                'recog_form': str(recog_form)
            }

            # API 요청
            response = self.http_client.post(self.ocr_url, files=files, data=data)
            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"API 요청 응답 시간: {duration_ms:.2f} ms")

            # 응답 확인
            if response.status_code != 200:
                logger.error(f"OCR API 요청 실패: {response.status_code}, {response.text}")
                raise HTTPException(status_code=response.status_code, detail="OCR API 요청 실패")

            # 응답 파싱
            return self.parse_response(response.text)
            
        except httpx.HTTPError as e:
            logger.error("OCR 요청 실패", exc_info=True)
            raise RuntimeError("OCR 실행 중 오류가 발생했습니다.") from e

    def parse_response(self, response_text: str) -> OcrResult:
        if not response_text:
            raise RuntimeError("빈 응답이 반환되었습니다.")
        
        try:
            root_node = json.loads(response_text)
            ocr_result_node = root_node.get("ocr_result", [])
            
            if not isinstance(ocr_result_node, list):
                logger.error(f"OCR 응답에 'ocr_result' 필드가 없거나 올바르지 않습니다. 응답: {response_text}")
                raise RuntimeError("OCR 응답 오류: 'ocr_result' or 누락")

            full_text_builder = []
            boxes = []

            for ocr_page_node in ocr_result_node:
                text = ocr_page_node.get("text", "")
                if text:
                    full_text_builder.append(text)
                
                bbox_node = ocr_page_node.get("bbox", [])
                if isinstance(bbox_node, list) and len(bbox_node) == 4:
                    left_top = Point(x=bbox_node[0][0], y=bbox_node[0][1])
                    right_top = Point(x=bbox_node[1][0], y=bbox_node[1][1])
                    right_bottom = Point(x=bbox_node[2][0], y=bbox_node[2][1])
                    left_bottom = Point(x=bbox_node[3][0], y=bbox_node[3][1])

                    ocr_box = OcrBox(
                        label=text,
                        left_top=left_top,
                        right_top=right_top,
                        right_bottom=right_bottom,
                        left_bottom=left_bottom,
                        confidence_score=ocr_page_node.get("score", 0.0)
                    )
                    boxes.append(ocr_box)

            return OcrResult(
                fid=root_node.get("fid", ""),
                total_pages=root_node.get("totalpage", 0),
                full_text=" ".join(full_text_builder).strip(),
                page_file_data=root_node.get("file_path", ""),
                boxes=boxes
            )
            
        except Exception as e:
            logger.error("OCR 응답 파싱 실패", exc_info=True)
            raise RuntimeError("OCR 실행 중 오류 발생") from e

    def download_img(self, file_path: str) -> bytes:
        data = {
            'lic': self.license_key,
            'path': file_path
        }
        
        try:
            response = self.http_client.post(self.download_url, data=data)
            
            if response.status_code != 200:
                logger.error(f"파일 다운로드 실패. HTTP 상태 코드: {response.status_code}, 응답 내용: {response.text}")
                raise RuntimeError(f"파일 다운로드 실패, HTTP 상태 코드: {response.status_code}")
            
            return response.content
            
        except httpx.HTTPError as e:
            logger.error(f"파일 다운로드 중 오류 발생. path: {file_path}", exc_info=True)
            raise RuntimeError("파일 다운로드 중 오류가 발생했습니다.") from e

    def get_worker_status(self) -> WorkerStatus:
        try:
            response = self.http_client.post(self.worker_status_url)
            
            if response.status_code != 200:
                logger.error(f"상태 조회 실패. HTTP 상태 코드: {response.status_code}, 응답 내용: {response.text}")
                raise RuntimeError(f"상태 조회 실패, HTTP 상태 코드: {response.status_code}")
            
            result = WorkerStatus(**response.json())
            return result
            
        except httpx.HTTPError as e:
            logger.error(f"상태 조회 중 오류 발생. URL: {self.worker_status_url}", exc_info=True)
            raise RuntimeError("상태 조회 중 오류가 발생했습니다.") from e

    def ocr_to_map(self, image_file, fid: str, page_index: str, path: str,
                  restoration: str, rot_angle: bool, bbox_roi: str,
                  type_: str, recog_form: bool) -> Dict[str, Any]:
        ocr_result = self.ocr(image_file, fid, page_index, path, restoration,
                             rot_angle, bbox_roi, type_, recog_form)
        
        result_map = {
            "fid": ocr_result.fid,
            "fullText": ocr_result.full_text,
            "totalPages": ocr_result.total_pages,
            "rotate": ocr_result.rotate,
            "pageFileData": ocr_result.page_file_data,
        }
        
        boxes_list = []
        if ocr_result.boxes:
            for box in ocr_result.boxes:
                box_map = {
                    "label": box.label,
                    "confidenceScore": box.confidence_score,
                    "leftTop": {"x": box.left_top.x, "y": box.left_top.y},
                    "rightTop": {"x": box.right_top.x, "y": box.right_top.y},
                    "leftBottom": {"x": box.left_bottom.x, "y": box.left_bottom.y},
                    "rightBottom": {"x": box.right_bottom.x, "y": box.right_bottom.y}
                }
                boxes_list.append(box_map)
        
        result_map["boxes"] = boxes_list
        return result_map


# FastAPI Router 생성
router = APIRouter(prefix="/ocr", tags=["OCR"])

# OcrEngine 인스턴스를 생성하기 위한 전역 변수
ocr_engine: Optional[OcrEngine] = None

def initialize_ocr_engine(license_key: str, base_url: str):
    """OCR 엔진을 초기화합니다."""
    global ocr_engine
    ocr_engine = OcrEngine(license_key, base_url)
    return ocr_engine

def get_ocr_engine() -> OcrEngine:
    """초기화된 OCR 엔진을 반환합니다."""
    if ocr_engine is None:
        raise RuntimeError("OCR 엔진이 초기화되지 않았습니다.")
    return ocr_engine

@router.post("/do-ocr/")
async def do_ocr(
    image_file: UploadFile = File(...),
    fid: str = Form(""),
    page_index: str = Form("0"),
    path: str = Form(""),
    restoration: str = Form(""),
    rot_angle: bool = Form(False),
    bbox_roi: str = Form(""),
    type_: str = Form(...),
    recog_form: bool = Form(False)
):
    """이미지를 OCR 처리합니다."""
    try:
        engine = get_ocr_engine()
        ocr_result = engine.ocr(
            image_file, fid, page_index, path, restoration,
            rot_angle, bbox_roi, type_, recog_form
        )
        return JSONResponse(content=ocr_result.dict())
    except Exception as e:
        logger.error("OCR 처리 중 오류 발생", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download_file/")
async def download_file(path: str = Form(...)):
    """파일을 다운로드합니다."""
    try:
        engine = get_ocr_engine()
        file_content = engine.download_img(path)
        return Response(content=file_content)
    except Exception as e:
        logger.error("파일 다운로드 중 오류 발생", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/worker-status/")
async def worker_status():
    """워커 상태를 확인합니다."""
    try:
        engine = get_ocr_engine()
        status = engine.get_worker_status()
        return status
    except Exception as e:
        logger.error("워커 상태 확인 중 오류 발생", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ocr-to-map/")
async def ocr_to_map(
    image_file: UploadFile = File(...),
    fid: str = Form(""),
    page_index: str = Form("0"),
    path: str = Form(""),
    restoration: str = Form(""),
    rot_angle: bool = Form(False),
    bbox_roi: str = Form(""),
    type_: str = Form(...),
    recog_form: bool = Form(False)
):
    """이미지를 OCR 처리하고 결과를 맵 형태로 반환합니다."""
    try:
        engine = get_ocr_engine()
        result_map = engine.ocr_to_map(
            image_file, fid, page_index, path, restoration,
            rot_angle, bbox_roi, type_, recog_form
        )
        return result_map
    except Exception as e:
        logger.error("OCR 맵 변환 중 오류 발생", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))