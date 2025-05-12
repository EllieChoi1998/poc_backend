# repositories/ocr_repository.py (신규 파일)
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from mysql.connector import Error
from database import get_db_connection
from models import (
    OcrEngineType, OcrFileStatus, OcrStatus, OcrBox, OcrResult, Point,
    OcrFile, OcrFileCreate, OcrFileUpdate, OcrPage, OcrBoxCreate
)

logger = logging.getLogger(__name__)

class OcrRepository:
    @staticmethod
    def save_ocr_file(ocr_file: OcrFileCreate) -> Optional[int]:
        """OCR 파일 정보 저장"""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = """
            INSERT INTO ocr_files 
            (file_name, file_path, engine_type, ocr_file_status, created_date, contract_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            values = (
                ocr_file.file_name,
                ocr_file.file_path,
                ocr_file.engine_type.value,
                ocr_file.ocr_file_status.value,
                ocr_file.created_date,
                ocr_file.contract_id
            )
            
            cursor.execute(query, values)
            ocr_file_id = cursor.lastrowid
            conn.commit()
            
            return ocr_file_id
            
        except Error as e:
            logger.error(f"OCR 파일 저장 중 오류 발생: {str(e)}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def update_ocr_file(file_id: int, update_data: OcrFileUpdate) -> bool:
        """OCR 파일 정보 업데이트"""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            update_parts = []
            params = []
            
            if update_data.total_page is not None:
                update_parts.append("total_page = %s")
                params.append(update_data.total_page)
                
            if update_data.fid is not None:
                update_parts.append("fid = %s")
                params.append(update_data.fid)
                
            if update_data.ocr_file_status is not None:
                update_parts.append("ocr_file_status = %s")
                params.append(update_data.ocr_file_status.value)
            
            if not update_parts:
                return True  # 업데이트할 내용이 없으면 성공으로 처리
            
            query = f"""
            UPDATE ocr_files 
            SET {', '.join(update_parts)}
            WHERE id = %s
            """
            
            params.append(file_id)
            cursor.execute(query, params)
            conn.commit()
            
            return cursor.rowcount > 0
            
        except Error as e:
            logger.error(f"OCR 파일 업데이트 중 오류 발생: {str(e)}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def save_ocr_page(ocr_file_id: int, page: int, full_text: str, executed_at: datetime,
                    execute_seconds: float, ocr_status: OcrStatus, page_file_data: str,
                    rotate: float) -> Optional[int]:
        """OCR 페이지 정보 저장"""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = """
            INSERT INTO ocr_pages 
            (ocr_file_id, page, full_text, executed_at, execute_seconds, 
             ocr_status, page_file_data, rotate)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                ocr_file_id,
                page,
                full_text,
                executed_at,
                execute_seconds,
                ocr_status.value,
                page_file_data,
                rotate
            )
            
            cursor.execute(query, values)
            page_id = cursor.lastrowid
            conn.commit()
            
            return page_id
            
        except Error as e:
            logger.error(f"OCR 페이지 저장 중 오류 발생: {str(e)}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def save_ocr_boxes(page_id: int, boxes: List[OcrBox]) -> bool:
        """OCR 박스(텍스트 영역) 정보 저장"""
        if not boxes:
            return True
            
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = """
            INSERT INTO ocr_boxes 
            (ocr_page_id, label, left_top_x, left_top_y, right_top_x, right_top_y,
             right_bottom_x, right_bottom_y, left_bottom_x, left_bottom_y, confidence_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = []
            for box in boxes:
                values.append((
                    page_id,
                    box.label,
                    box.left_top.x,
                    box.left_top.y,
                    box.right_top.x,
                    box.right_top.y,
                    box.right_bottom.x,
                    box.right_bottom.y,
                    box.left_bottom.x,
                    box.left_bottom.y,
                    box.confidence_score
                ))
            
            cursor.executemany(query, values)
            conn.commit()
            
            return True
            
        except Error as e:
            logger.error(f"OCR 박스 저장 중 오류 발생: {str(e)}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_ocr_file_by_id(file_id: int) -> Optional[Dict[str, Any]]:
        """ID로 OCR 파일 조회"""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM ocr_files WHERE id = %s"
            cursor.execute(query, (file_id,))
            
            result = cursor.fetchone()
            return result
            
        except Error as e:
            logger.error(f"OCR 파일 조회 중 오류 발생: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_ocr_file_by_contract_id(contract_id: int) -> Optional[Dict[str, Any]]:
        """계약서 ID로 OCR 파일 조회"""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
            SELECT * FROM ocr_files 
            WHERE contract_id = %s 
            ORDER BY created_date DESC
            LIMIT 1
            """
            
            cursor.execute(query, (contract_id,))
            result = cursor.fetchone()
            return result
            
        except Error as e:
            logger.error(f"계약서 ID로 OCR 파일 조회 중 오류 발생: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_ocr_pages_by_file_id(file_id: int) -> List[Dict[str, Any]]:
        """파일 ID로 OCR 페이지 목록 조회"""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
            SELECT * FROM ocr_pages 
            WHERE ocr_file_id = %s 
            ORDER BY page
            """
            
            cursor.execute(query, (file_id,))
            result = cursor.fetchall()
            return result or []
            
        except Error as e:
            logger.error(f"파일 ID로 OCR 페이지 조회 중 오류 발생: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_ocr_boxes_by_page_id(page_id: int) -> List[Dict[str, Any]]:
        """페이지 ID로 OCR 박스 목록 조회"""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
            SELECT * FROM ocr_boxes 
            WHERE ocr_page_id = %s 
            ORDER BY id
            """
            
            cursor.execute(query, (page_id,))
            result = cursor.fetchall()
            return result or []
            
        except Error as e:
            logger.error(f"페이지 ID로 OCR 박스 조회 중 오류 발생: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_ocr_result_by_contract_id(contract_id: int) -> Optional[Dict[str, Any]]:
        """계약서 ID로 OCR 결과 조회 (파일, 페이지, 텍스트 등 종합 정보)"""
        ocr_file = OcrRepository.get_ocr_file_by_contract_id(contract_id)
        if not ocr_file:
            return None
            
        file_id = ocr_file["id"]
        ocr_pages = OcrRepository.get_ocr_pages_by_file_id(file_id)
        
        # 페이지별 텍스트 및 박스 정보 추가
        pages_with_boxes = []
        for page in ocr_pages:
            page_id = page["id"]
            boxes = OcrRepository.get_ocr_boxes_by_page_id(page_id)
            
            pages_with_boxes.append({
                "page_info": page,
                "boxes": boxes
            })
        
        # 결과 종합
        result = {
            "file_info": ocr_file,
            "pages": pages_with_boxes,
            "total_pages": len(ocr_pages)
        }
        
        return result