import os
import time
import json
import logging
import aiofiles
import asyncio
from typing import Dict, List, Optional, Any, Union, Tuple, BinaryIO
from pathlib import Path

import httpx
from pydantic import ValidationError

from models import OcrBox, OcrResult, Point, WorkerStatus

logger = logging.getLogger(__name__)


class OcrEngine:
    def __init__(self, license_key: str, base_url: str):
        if not license_key or license_key.strip() == "":
            raise ValueError("라이센스 키가 필요합니다.")
        if not base_url or base_url.strip() == "":
            raise ValueError("서버 주소가 필요합니다.")

        # 1. 스킴(http:// 또는 https://)이 없으면 추가
        lower_addr = base_url.lower()
        if not lower_addr.startswith("http://") and not lower_addr.startswith("https://"):
            base_url = f"http://{base_url}"

        # 2. baseUrl의 끝에 있는 슬래시(/)를 제거 (중복 슬래시 방지)
        base_url = base_url.rstrip("/")

        self.license_key = license_key

        # 실제 OCR 요청용 URL
        self.ocr_url = f"{base_url}/do-ocr/"
        # 파일 다운로드용 URL
        self.download_url = f"{base_url}/download_file/"
        # 워커 확인용 URL
        self.worker_status_url = f"{base_url}/worker-status/"

        # 타임아웃 설정
        self.timeout = httpx.Timeout(60.0, connect=60.0)

        # 로그 출력
        logger.info(f"OCR URL: {self.ocr_url}")
        logger.info(f"DOWNLOAD URL: {self.download_url}")

    @classmethod
    def create_ocr_engine(cls, api_key: str, server_addr: str) -> 'OcrEngine':
        """
        정적 팩토리 메서드를 통해 API 라이센스와 서버 주소를 받아 OcrEngine을 생성합니다.
        """
        if not api_key or api_key.strip() == "":
            raise ValueError("라이센스 키가 필요합니다.")

        # OcrEngine의 생성자에서 server_addr를 바탕으로
        # do-ocr/와 download_file/ 엔드포인트를 각각 세팅
        engine = cls(api_key, server_addr)
        return engine

    async def ocr(self, image_file: Union[str, Path, BinaryIO], 
                 fid: Optional[str] = None, 
                 page_index: Optional[str] = None, 
                 path: Optional[str] = None,
                 restoration: Optional[str] = None, 
                 rot_angle: bool = False,
                 bbox_roi: Optional[str] = None, 
                 type_: str = "upload",
                 recog_form: bool = False) -> OcrResult:
        """
        OCR 처리를 수행합니다.
        """
        return await self.process_ocr(
            image_file, fid, page_index, path, restoration, 
            rot_angle, bbox_roi, type_, recog_form
        )

    async def process_ocr(self, image_file: Union[str, Path, BinaryIO], 
                         fid: Optional[str] = None, 
                         page_index: Optional[str] = None, 
                         path: Optional[str] = None,
                         restoration: Optional[str] = None, 
                         rot_angle: bool = False,
                         bbox_roi: Optional[str] = None, 
                         type_: str = "upload",
                         recog_form: bool = False) -> OcrResult:
        """
        OCR 처리를 수행하고 예외가 발생할 경우 처리합니다.
        """
        try:
            return await self.perform_ocr(
                image_file, fid, page_index, path, restoration, 
                rot_angle, bbox_roi, type_, recog_form
            )
        except Exception as e:
            file_path = getattr(image_file, 'name', str(image_file))
            logger.error(f"OCR 처리 중 오류 발생 (파일: {file_path})", exc_info=e)
            raise RuntimeError(f"OCR 처리 실패: {str(e)}") from e

    async def perform_ocr(self, image_file: Union[str, Path, BinaryIO], 
                         fid: Optional[str] = None, 
                         page_index: Optional[str] = None, 
                         path: Optional[str] = None,
                         restoration: Optional[str] = None, 
                         rot_angle: bool = False,
                         bbox_roi: Optional[str] = None, 
                         type_: str = "upload",
                         recog_form: bool = False) -> OcrResult:
        """
        실제 OCR 처리를 수행합니다.
        """
        # 파일 객체인지 아니면 파일 경로인지 확인 및 처리
        file_name = ""
        file_bytes = None
        content_type = "application/octet-stream"

        if isinstance(image_file, (str, Path)):
            file_path = Path(image_file)
            file_name = file_path.name
            content_type = self.determine_content_type(file_name)
            async with aiofiles.open(file_path, 'rb') as f:
                file_bytes = await f.read()
        else:
            # 파일 객체로 가정하고 처리
            file_name = getattr(image_file, 'name', 'uploaded_file')
            content_type = self.determine_content_type(file_name)
            # 파일 포인터 위치 저장
            position = image_file.tell()
            # 파일 포인터를 처음으로 이동
            image_file.seek(0)
            file_bytes = image_file.read()
            # 파일 포인터 복원
            image_file.seek(position)

        try:
            start_time = time.time()
            # 멀티파트 폼 데이터 구성
            form_data = {
                "fid": fid or "",
                "page_index": page_index or "0",
                "path": path or "",
                "lic": self.license_key,
                "restoration": restoration or "",
                "rot_angle": str(rot_angle).lower(),
                "bbox_roi": bbox_roi or "",
                "type": type_,
                "recog_form": str(recog_form).lower()
            }
            
            files = {
                "imagefile": (file_name, file_bytes, content_type)
            }

            # HTTP 요청 전송
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.ocr_url,
                    data=form_data,
                    files=files,
                    headers={"Accept": "application/json"}
                )
                
                duration_ms = (time.time() - start_time) * 1000
                logger.info(f"API 요청 응답 시간: {duration_ms:.2f} ms")
                
                # 응답 내용 추출
                response_text = response.text.strip()
                if not response_text:
                    raise RuntimeError("빈 응답이 반환되었습니다.")
                
                return self.parse_response(response_text)
        
        except httpx.HTTPError as e:
            logger.error("OCR 요청 실패", exc_info=e)
            raise RuntimeError(f"OCR 실행 중 HTTP 오류가 발생했습니다: {str(e)}") from e
        except Exception as e:
            logger.error("OCR 요청 처리 중 오류 발생", exc_info=e)
            raise RuntimeError(f"OCR 실행 중 오류가 발생했습니다: {str(e)}") from e

    def determine_content_type(self, file_name: str) -> str:
        """
        파일의 확장자에 따라 Content-Type을 결정합니다.
        """
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

    def parse_response(self, response_text: str) -> OcrResult:
        """
        OCR API의 응답을 파싱하여 OcrResult 객체를 생성합니다.
        """
        try:
            data = json.loads(response_text)
            ocr_result_node = data.get("ocr_result")
            
            if not ocr_result_node or not isinstance(ocr_result_node, list):
                logger.error(f"OCR 응답에 'ocr_result' 필드가 없거나 올바르지 않습니다. 응답: {response_text}")
                raise RuntimeError("OCR 응답 오류: 'ocr_result' 누락")
            
            full_text_builder = []
            boxes = []
            
            for ocr_page_node in ocr_result_node:
                text = ocr_page_node.get("text", "")
                if text:
                    full_text_builder.append(text)
                
                bbox_node = ocr_page_node.get("bbox")
                if bbox_node and isinstance(bbox_node, list) and len(bbox_node) == 4:
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
                fid=data.get("fid", ""),
                total_pages=data.get("totalpage", 0),
                full_text=" ".join(full_text_builder).strip(),
                page_file_data=data.get("file_path", ""),
                boxes=boxes
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {response_text}", exc_info=e)
            raise RuntimeError("OCR 응답을 JSON으로 파싱할 수 없습니다") from e
        except Exception as e:
            logger.error("OCR 응답 파싱 실패", exc_info=e)
            raise RuntimeError(f"OCR 응답 파싱 중 오류 발생: {str(e)}") from e

    async def download_img(self, file_path: str) -> bytes:
        """
        OCR 결과 이미지를 다운로드합니다.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            form_data = {
                "lic": self.license_key,
                "path": file_path
            }
            
            try:
                response = await client.post(self.download_url, data=form_data)
                status_code = response.status_code
                logger.info(f"Response Status Code: {status_code}")
                
                if status_code != 200:
                    response_body = response.text
                    logger.error(f"파일 다운로드 실패. HTTP 상태 코드: {status_code}, 응답 내용: {response_body}")
                    raise RuntimeError(f"파일 다운로드 실패, HTTP 상태 코드: {status_code}")
                
                if not response.content:
                    raise RuntimeError("다운로드한 파일 데이터가 없습니다.")
                
                return response.content
            
            except httpx.HTTPError as e:
                logger.error(f"파일 다운로드 중 오류 발생. path: {file_path}", exc_info=e)
                raise RuntimeError(f"파일 다운로드 중 오류가 발생했습니다: {str(e)}") from e

    async def get_worker_status(self) -> WorkerStatus:
        """
        OCR 워커 상태를 조회합니다.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(self.worker_status_url)
                status_code = response.status_code
                
                # 정상 응답(200) 아닐 경우 예외 처리
                if status_code != 200:
                    response_body = response.text
                    logger.error(f"상태 조회 실패. HTTP 상태 코드: {status_code}, 응답 내용: {response_body}")
                    raise RuntimeError(f"상태 조회 실패, HTTP 상태 코드: {status_code}")
                
                # 응답 본문을 분석
                json_response = response.json()
                return WorkerStatus.parse_obj(json_response)
                
            except httpx.HTTPError as e:
                logger.error(f"상태 조회 중 오류 발생. URL: {self.worker_status_url}", exc_info=e)
                raise RuntimeError(f"상태 조회 중 오류가 발생했습니다: {str(e)}") from e
            except ValidationError as e:
                logger.error("응답을 WorkerStatus 모델로 변환 중 오류 발생", exc_info=e)
                raise RuntimeError(f"워커 상태 응답을 파싱할 수 없습니다: {str(e)}") from e

    async def ocr_to_map(self, image_file: Union[str, Path, BinaryIO], 
                        fid: Optional[str] = None, 
                        page_index: Optional[str] = None, 
                        path: Optional[str] = None,
                        restoration: Optional[str] = None, 
                        rot_angle: bool = False,
                        bbox_roi: Optional[str] = None, 
                        type_: str = "upload",
                        recog_form: bool = False) -> Dict[str, Any]:
        """
        OCR 결과를 Map 형태로 반환하는 메서드
        """
        ocr_result = await self.ocr(
            image_file, fid, page_index, path, restoration, 
            rot_angle, bbox_roi, type_, recog_form
        )
        
        result_map = {
            "fid": ocr_result.fid,
            "fullText": ocr_result.full_text,
            "totalPages": ocr_result.total_pages,
            "rotate": ocr_result.rotate,
            "pageFileData": ocr_result.page_file_data
        }
        
        boxes_list = []
        if ocr_result.boxes:
            for box in ocr_result.boxes:
                box_map = {
                    "label": box.label,
                    "confidenceScore": box.confidence_score,
                    
                    # 좌표 정보 변환
                    "leftTop": {"x": box.left_top.x, "y": box.left_top.y},
                    "rightTop": {"x": box.right_top.x, "y": box.right_top.y},
                    "leftBottom": {"x": box.left_bottom.x, "y": box.left_bottom.y},
                    "rightBottom": {"x": box.right_bottom.x, "y": box.right_bottom.y}
                }
                boxes_list.append(box_map)
        
        result_map["boxes"] = boxes_list
        return result_map