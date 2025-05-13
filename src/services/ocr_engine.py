# services/ocr_engine.py (신규 파일)
import logging
import requests
import json
import os
import time
from typing import List, Dict, Any, Optional
from models import OcrResult, OcrBox, Point

logger = logging.getLogger(__name__)

class OcrEngine:
    def __init__(self, license_key: str, base_url: str):
        if not license_key or license_key.strip() == "":
            raise ValueError("라이센스 키가 필요합니다.")
        if not base_url or base_url.strip() == "":
            raise ValueError("서버 주소가 필요합니다.")
            
        # 스킴 추가 (http:// 또는 https://)
        lower_addr = base_url.lower()
        if not lower_addr.startswith("http://") and not lower_addr.startswith("https://"):
            base_url = "http://" + base_url
            
        # baseUrl의 끝에 있는 슬래시(/) 제거
        base_url = base_url.rstrip("/")
        
        self.license_key = license_key
        self.ocr_url = f"{base_url}/do-ocr/"
        self.download_url = f"{base_url}/download_file/"
        self.worker_status_url = f"{base_url}/worker-status/"
        
        logger.info(f"OCR URL: {self.ocr_url}")
        logger.info(f"DOWNLOAD URL: {self.download_url}")
    
    @classmethod
    def create_ocr_engine(cls, api_key: str, server_addr: str) -> 'OcrEngine':
        if not api_key or api_key.strip() == "":
            raise ValueError("라이센스 키가 필요합니다.")
        
        engine = cls(api_key, server_addr)
        return engine
    
    # 현재 활성화된 ocr 메서드를 주석 처리된 버전으로 교체
    def ocr(self, image_file: str, page_index: str = "0", 
        fid: str = "", path: str = "", restoration: str = "", 
        rot_angle: bool = False, bbox_roi: str = "", 
        file_type: str = "local", recog_form: bool = False) -> OcrResult:
        try:
            # 파일 타입 결정
            content_type = self._determine_content_type(image_file)
            
            # 요청 전 로깅 강화 - 파일 확인
            if not os.path.exists(image_file):
                logger.error(f"파일이 존재하지 않음: {image_file}")
                raise FileNotFoundError(f"파일이 존재하지 않음: {image_file}")
            
            logger.info(f"OCR 파일 크기: {os.path.getsize(image_file)} bytes, 유형: {content_type}")
            
            start_time = time.time()
            
            # HTTP 요청 준비
            with open(image_file, 'rb') as f:
                file_data = f.read()
                
            # multipart/form-data 형식으로 보내기
            files = {'imagefile': (os.path.basename(image_file), file_data, content_type)}
            
            # 문자열로 변환된 bool 값 사용
            rot_angle_str = "true" if rot_angle else "false"
            recog_form_str = "true" if recog_form else "false"
            
            data = {
                'fid': fid,
                'page_index': page_index,
                'path': path,
                'lic': self.license_key,
                'restoration': restoration,
                'rot_angle': rot_angle_str,  # Java에서는 문자열로 전송했을 가능성이 높음
                'bbox_roi': bbox_roi,
                'type': file_type,
                'recog_form': recog_form_str  # Java에서는 문자열로 전송했을 가능성이 높음
            }
            
            # 요청 데이터 로깅 (라이센스 키 일부는 마스킹)
            safe_data = data.copy()
            if 'lic' in safe_data and safe_data['lic']:
                safe_data['lic'] = safe_data['lic'][:4] + '****'
            logger.info(f"OCR 요청 데이터: {safe_data}")
            logger.info(f"OCR 요청 URL: {self.ocr_url}")
            
            # 요청 실행 - 타임아웃 증가
            response = requests.post(self.ocr_url, files=files, data=data, timeout=180)
            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"API 요청 응답 시간: {duration_ms:.2f} ms, 상태 코드: {response.status_code}")
            
            # 응답 확인
            if response.status_code != 200:
                logger.error(f"OCR 요청 실패. 상태 코드: {response.status_code}, 응답 본문: {response.text}")
                logger.error(f"응답 헤더: {dict(response.headers)}")
                raise RuntimeError(f"OCR 요청 실패. 상태 코드: {response.status_code}, 응답: {response.text}")
            
            logger.info("OCR 응답 성공적으로 수신")
            # 응답 파싱
            return self._parse_response(response.text)
            
        except Exception as e:
            logger.error(f"OCR 요청 실패: {str(e)}", exc_info=True)
            raise RuntimeError(f"OCR 실행 중 오류가 발생했습니다: {str(e)}")
    # def ocr(self, image_file: str, fid: str = "", page_index: str = "0", 
    #         path: str = "", restoration: str = "", rot_angle: bool = False, 
    #         bbox_roi: str = "", file_type: str = "local", recog_form: bool = False) -> OcrResult:
    #     try:
    #         # 파일 타입 결정
    #         content_type = self._determine_content_type(image_file)
            
    #         start_time = time.time()
            
    #         # HTTP 요청 준비
    #         with open(image_file, 'rb') as f:
    #             file_data = f.read()
                
    #         files = {'imagefile': (os.path.basename(image_file), file_data, content_type)}
    #         data = {
    #             'fid': fid or "",
    #             'page_index': page_index or "0",
    #             'path': path or "",
    #             'lic': self.license_key,
    #             'restoration': restoration or "",
    #             'rot_angle': str(rot_angle),
    #             'bbox_roi': bbox_roi or "",
    #             'type': file_type,
    #             'recog_form': str(recog_form)
    #         }
            
    #         # 요청 실행
    #         response = requests.post(self.ocr_url, files=files, data=data, timeout=60)
    #         duration_ms = (time.time() - start_time) * 1000
    #         logger.info(f"API 요청 응답 시간: {duration_ms} ms")
            
    #         # 응답 확인
    #         if response.status_code != 200:
    #             logger.error(f"OCR 요청 실패. 상태 코드: {response.status_code}, 응답: {response.text}")
    #             raise RuntimeError(f"OCR 요청 실패. 상태 코드: {response.status_code}, 응답: {response.text}")
            
    #         # 응답 파싱
    #         return self._parse_response(response.text)
            
    #     except Exception as e:
    #         logger.error(f"OCR 요청 실패: {str(e)}", exc_info=True)
    #         raise RuntimeError(f"OCR 실행 중 오류가 발생했습니다: {str(e)}")
    def check_server_status(self):
        """OCR 서버 연결 및 상태를 확인합니다."""
        try:
            # 서버 상태 URL 사용
            response = requests.get(self.worker_status_url, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"OCR 서버 상태 확인 성공: {response.status_code}")
                return True, response.text
            else:
                logger.error(f"OCR 서버 상태 확인 실패: {response.status_code}, 응답: {response.text}")
                return False, f"상태 코드: {response.status_code}, 응답: {response.text}"
                
        except Exception as e:
            logger.error(f"OCR 서버 연결 시도 중 오류: {str(e)}", exc_info=True)
            return False, str(e)
    
    def _determine_content_type(self, file_path: str) -> str:
        file_name = file_path.lower()
        if file_name.endswith(".pdf"):
            return "application/pdf"
        elif file_name.endswith(".png"):
            return "image/png"
        elif file_name.endswith(".tiff") or file_name.endswith(".tif"):
            return "image/tiff"
        elif file_name.endswith(".jpg") or file_name.endswith(".jpeg"):
            return "image/jpeg"
        return "application/octet-stream"
    
    def _parse_response(self, response_text: str) -> OcrResult:
        if not response_text:
            raise RuntimeError("빈 응답이 반환되었습니다.")
        
        try:
            data = json.loads(response_text)
            ocr_result_nodes = data.get("ocr_result", [])
            
            if not isinstance(ocr_result_nodes, list):
                logger.error(f"OCR 응답에 'ocr_result' 필드가 없거나 올바르지 않습니다. 응답: {response_text}")
                raise RuntimeError("OCR 응답 오류: 'ocr_result' 누락")
            
            full_text_parts = []
            boxes = []
            
            for node in ocr_result_nodes:
                text = node.get("text", "")
                if text:
                    full_text_parts.append(text)
                
                bbox = node.get("bbox", [])
                if isinstance(bbox, list) and len(bbox) == 4:
                    left_top = Point(x=bbox[0][0], y=bbox[0][1])
                    right_top = Point(x=bbox[1][0], y=bbox[1][1])
                    right_bottom = Point(x=bbox[2][0], y=bbox[2][1])
                    left_bottom = Point(x=bbox[3][0], y=bbox[3][1])
                    
                    ocr_box = OcrBox(
                        label=text,
                        left_top=left_top,
                        right_top=right_top,
                        right_bottom=right_bottom,
                        left_bottom=left_bottom,
                        confidence_score=node.get("score", 0.0)
                    )
                    boxes.append(ocr_box)
            
            return OcrResult(
                fid=data.get("fid", ""),
                total_pages=data.get("totalpage", 0),
                rotate=data.get("rotate", 0.0),
                full_text=" ".join(full_text_parts).strip(),
                page_file_data=data.get("file_path", ""),
                boxes=boxes
            )
        
        except Exception as e:
            logger.error("OCR 응답 파싱 실패", exc_info=True)
            raise RuntimeError(f"OCR 실행 중 오류 발생: {str(e)}")
    
    def download_img(self, file_path: str) -> bytes:
        data = {
            'lic': self.license_key,
            'path': file_path
        }
        
        try:
            response = requests.post(self.download_url, data=data, timeout=60)
            
            status_code = response.status_code
            logger.info(f"Response Status Code: {status_code}")
            
            if status_code != 200:
                logger.error(f"파일 다운로드 실패. HTTP 상태 코드: {status_code}, 응답 내용: {response.text}")
                raise RuntimeError(f"파일 다운로드 실패, HTTP 상태 코드: {status_code}")
            
            return response.content
            
        except Exception as e:
            logger.error(f"파일 다운로드 중 오류 발생. path: {file_path}", exc_info=True)
            raise RuntimeError(f"파일 다운로드 중 오류가 발생했습니다: {str(e)}")