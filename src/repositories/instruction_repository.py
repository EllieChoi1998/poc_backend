from base_repository import BaseRepository
from typing import Optional, Dict, Any, List
from datetime import datetime


class InstructionRepository:
    
    @staticmethod
    def create_instruction(
        type: int, 
        performer_id: int, 
        file_name: str,
        is_fund_item: str = 'F',
        company_detail: Optional[str] = None,
        deal_type: Optional[str] = None,
        deal_object: Optional[str] = None,
        bank_name: Optional[str] = None,
        account_number: Optional[str] = None,
        holder_name: Optional[str] = None,
        amount: Optional[str] = None,
        process_date: Optional[datetime] = None,
        other_specs_text: Optional[str] = None,
        other_specs_detail: Optional[str] = None
    ) -> int:
        """
        새로운 instruction을 생성합니다.
        
        Args:
            type: 1 => PEF, 2 => 특자
            performer_id: 수행자 ID
            file_name: 파일 이름
            is_fund_item: 펀드 아이템 여부 ('T' 또는 'F')
            company_detail: 회사 상세 정보
            deal_type: 거래 유형
            deal_object: 거래 대상
            bank_name: 은행 이름
            account_number: 계좌 번호
            holder_name: 예금주 이름
            amount: 금액
            process_date: 처리 날짜
            other_specs_text: 기타 명세 텍스트
            other_specs_detail: 기타 명세 상세 정보
            
        Returns:
            생성된 instruction의 ID
        """
        cursor, conn = BaseRepository.open_db()
        try:
            # 프로시저에 전달할 파라미터 준비
            params = [
                type, 
                performer_id, 
                file_name,
                is_fund_item,
                company_detail,
                deal_type,
                deal_object,
                bank_name,
                account_number,
                holder_name,
                amount,
                process_date,
                other_specs_text,
                other_specs_detail,
                0  # OUT 파라미터 (inserted_id)
            ]
            
            # 프로시저 호출
            cursor.callproc('sp_create_instruction', params)
            
            # OUT 파라미터 가져오기
            inserted_id = None
            for result in cursor.stored_results():
                row = result.fetchone()
                if row:
                    inserted_id = row[0]
                    break
            
            conn.commit()
            return inserted_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            BaseRepository.close_db(conn=conn, cursor=cursor)