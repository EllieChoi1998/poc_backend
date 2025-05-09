from typing import Dict, List, Optional, Any, Union
import httpx
import json
import logging
import os
from fastapi import HTTPException, UploadFile
import io
import time

# 모델 가져오기
from models import Point, OcrBox, OcrResult, WorkerStatus

# 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OcrService:
    _instance = None

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
        self.http_client = httpx.AsyncClient(timeout=60.0)

        # 로그
        logger.info(f"OCR 서비스 초기화: 라이센스 키={license_key[:3]}***")
        logger.info(f"OCR URL: {self.ocr_url}")
        logger.info(f"DOWNLOAD URL: {self.download_url}")

    @classmethod
    def initialize(cls, license_key: str, server_addr: str) -> 'OcrService':
        """OCR 서비스의 싱글톤 인스턴스를 초기화하고 반환합니다."""
        if cls._instance is None:
            if not license_key or license_key.strip() == "":
                raise ValueError("라이센스 키가 필요합니다.")
            cls._instance = OcrService(license_key, server_addr)
        return cls._instance

    @classmethod
    def get_instance(cls) -> Optional['OcrService']:
        """초기화된 OCR 서비스 인스턴스를 반환합니다."""
        return cls._instance

    def determine_content_type(self, file_name: str) -> str:
        """파일 이름에서 콘텐츠 타입을 결정합니다."""
        file_name = file_name.lower()
        if file_name.endswith(".pdf"):
            return "application/pdf"
        elif file_name.endswith(".png"):
            return "image/png"
        elif file_name.endswith(".jpg") or file_name.endswith(".jpeg"):
            return "image/jpeg"
        elif file_name.endswith(".tiff") or file_name.endswith(".tif"):
            return "image/tiff"
        return "application/octet-stream"

    async def ocr(self, image_file: UploadFile, fid: str, page_index: str, path: str,
                 restoration: str, rot_angle: bool, bbox_roi: str,
                 type_: str, recog_form: bool) -> OcrResult:
        """OCR을 수행합니다."""
        try:
            return await self.perform_ocr(image_file, fid, page_index, path, restoration,
                                     rot_angle, bbox_roi, type_, recog_form)
        except Exception as e:
            logger.error(f"OCR 처리 중 오류 발생 (파일: {image_file.filename})", exc_info=True)
            raise RuntimeError("OCR 처리 실패") from e

    async def perform_ocr(self, image_file: UploadFile, fid: str, page_index: str, path: str,
                        restoration: str, rot_angle: bool, bbox_roi: str,
                        type_: str, recog_form: bool) -> OcrResult:
        """실제 OCR 처리를 수행합니다."""
        # 콘텐츠 타입 결정
        content_type = self.determine_content_type(image_file.filename)
        file_content = await image_file.read()
        
        try:
            start_time = time.time()
            
            # 폼 데이터 구성
            files = {'imagefile': (image_file.filename, file_content, content_type)}
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
            response = await self.http_client.post(self.ocr_url, files=files, data=data)
            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"OCR API 요청 응답 시간: {duration_ms:.2f} ms")

            # 응답 확인
            if response.status_code != 200:
                logger.error(f"OCR API 요청 실패: {response.status_code}, {response.text}")
                raise HTTPException(status_code=response.status_code, detail="OCR API 요청 실패")

            # 응답 파싱
            ocr_result = self.parse_response(response.text)
            
            # 여기서 OCR 결과에 대한 추가 처리를 수행할 수 있음
            # 예: 결과 필터링, 분석, 데이터베이스 저장 등
            
            return ocr_result
            
        except httpx.HTTPError as e:
            logger.error("OCR 요청 실패", exc_info=True)
            raise RuntimeError("OCR 실행 중 오류가 발생했습니다.") from e
        finally:
            # 파일 포인터 위치 리셋
            await image_file.seek(0)

    def parse_response(self, response_text: str) -> OcrResult:
        """OCR API 응답을 파싱합니다."""
        if not response_text:
            raise RuntimeError("빈 응답이 반환되었습니다.")
        
        try:
            root_node = json.loads(response_text)
            ocr_result_node = root_node.get("ocr_result", [])
            
            if not isinstance(ocr_result_node, list):
                logger.error(f"OCR 응답에 'ocr_result' 필드가 없거나 올바르지 않습니다. 응답: {response_text}")
                raise RuntimeError("OCR 응답 오류: 'ocr_result' 누락")

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
                boxes=boxes,
                rotate=root_node.get("rotate", 0)  # 회전 정보 추가
            )
            
        except Exception as e:
            logger.error("OCR 응답 파싱 실패", exc_info=True)
            raise RuntimeError("OCR 실행 중 오류 발생") from e

    async def download_img(self, file_path: str) -> bytes:
        """파일을 다운로드합니다."""
        data = {
            'lic': self.license_key,
            'path': file_path
        }
        
        try:
            response = await self.http_client.post(self.download_url, data=data)
            
            if response.status_code != 200:
                logger.error(f"파일 다운로드 실패. HTTP 상태 코드: {response.status_code}, 응답 내용: {response.text}")
                raise RuntimeError(f"파일 다운로드 실패, HTTP 상태 코드: {response.status_code}")
            
            return response.content
            
        except httpx.HTTPError as e:
            logger.error(f"파일 다운로드 중 오류 발생. path: {file_path}", exc_info=True)
            raise RuntimeError("파일 다운로드 중 오류가 발생했습니다.") from e

    async def get_worker_status(self) -> WorkerStatus:
        """워커 상태를 확인합니다."""
        try:
            response = await self.http_client.post(self.worker_status_url)
            
            if response.status_code != 200:
                logger.error(f"상태 조회 실패. HTTP 상태 코드: {response.status_code}, 응답 내용: {response.text}")
                raise RuntimeError(f"상태 조회 실패, HTTP 상태 코드: {response.status_code}")
            
            result = WorkerStatus(**response.json())
            return result
            
        except httpx.HTTPError as e:
            logger.error(f"상태 조회 중 오류 발생. URL: {self.worker_status_url}", exc_info=True)
            raise RuntimeError("상태 조회 중 오류가 발생했습니다.") from e

    async def ocr_to_map(self, image_file: UploadFile, fid: str, page_index: str, path: str,
                        restoration: str, rot_angle: bool, bbox_roi: str,
                        type_: str, recog_form: bool) -> Dict[str, Any]:
        """OCR 결과를 맵 형태로 변환합니다."""
        ocr_result = await self.ocr(image_file, fid, page_index, path, restoration,
                                  rot_angle, bbox_roi, type_, recog_form)
        
        # OCR 결과를 맵으로 변환
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
        
        # 여기서 결과에 대한 추가 처리를 수행할 수 있음
        # 예: 특정 텍스트 추출, 특정 패턴 검색, 결과 필터링 등
        
        return result_map

    # 예시: OCR 결과에서 특정 패턴을 추출하는 메서드 추가
    async def extract_pattern(self, image_file: UploadFile, pattern_type: str) -> Dict[str, Any]:
        """OCR 결과에서 특정 패턴(예: 주민등록번호, 계약번호 등)을 추출합니다."""
        # 기본 OCR 수행
        ocr_result = await self.ocr(
            image_file, "", "0", "", "", False, "", "auto", False
        )
        
        # 추출된 패턴을 저장할 결과 딕셔너리
        extracted_data = {
            "original_text": ocr_result.full_text,
            "pattern_type": pattern_type,
            "extracted_values": []
        }
        
        # 패턴 타입에 따른 추출 로직
        if pattern_type == "주민번호":
            # 주민번호 패턴 추출 로직 구현
            # 예: 정규식 매칭, 형식 검증 등
            pass
        elif pattern_type == "계약번호":
            # 계약번호 패턴 추출 로직 구현
            pass
        elif pattern_type == "금액":
            # 금액 패턴 추출 로직 구현
            pass
        
        return extracted_data

# 싱글톤 인스턴스 가져오기 위한 함수 (FastAPI dependency로 사용)
def get_ocr_service() -> OcrService:
    service = OcrService.get_instance()
    if service is None:
        raise HTTPException(status_code=500, detail="OCR 서비스가 초기화되지 않았습니다.")
    return service