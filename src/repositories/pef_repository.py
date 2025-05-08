from base_repository import BaseRepository
from typing import Optional, Dict, Any, List
from models import TransactionHistory,OtherSpecifications, InstructionPEFDetail, InstructionPEFResultDetail

class PEFRepository:
    @staticmethod
    def create_pef(performer_id: int, filename: str) -> int:
        cursor, conn = BaseRepository.open_db()
        try:
            cursor.execute(
                '''
                INSERT INTO instruction_pef (performer_id, filename) VALUES (%s, %s)
                ''',
                (performer_id, filename)
            )

            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            BaseRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        cursor, conn = BaseRepository.open_db()
        try:
            cursor.execute('SELECT * FROM instruction_pef')
            return cursor.fetchall()
        finally:
            BaseRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def delete_pef(id: int) -> bool:
        with BaseRepository.DB() as (cursor, conn):
            cursor.execute('DELETE FROM contract WHERE id= %s', (id, ))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def get_all_results_by_pef(pef_id: int) -> InstructionPEFDetail:
        cursor, conn = BaseRepository.open_db()
        try:
            # 1. PEF 기본 정보 조회
            cursor.execute('SELECT id, performer_id, filename, created_at FROM instruction_pef WHERE id = %s', (pef_id,))
            pef_row = cursor.fetchone()
            if not pef_row:
                return None
            
            pef = InstructionPEFDetail(
                id=pef_row[0],
                performer_id=pef_row[1],
                file_name=pef_row[2],
                created_at=pef_row[3]
            )

            # 2. 결과 정보 조회
            cursor.execute('SELECT id, instruction_pef_id, is_fund_item, company_detail FROM instruction_pef_result WHERE instruction_pef_id = %s', (pef.id,))
            result_row = cursor.fetchone()
            if not result_row:
                return pef  # 결과가 없으면 빈 PEF 객체 반환
            
            result = InstructionPEFResultDetail(
                id=result_row[0],
                instruction_pef_id=result_row[1],
                is_fund_item=result_row[2],
                company_detail=result_row[3],
            )

            # 3. 거래 내역 조회
            cursor.execute('SELECT id, instruction_pef_result_id, deal_type, deal_object, bank_name, account_number, holder_name, amount, process_date FROM transaction_history WHERE instruction_pef_result_id = %s', (result.id,))
            for row in cursor.fetchall():
                result.transaction_history.append(TransactionHistory(
                    id=row[0], instruction_pef_result_id=row[1], deal_type=row[2],
                    deal_object=row[3], bank_name=row[4], account_number=row[5],
                    holder_name=row[6], amount=row[7], process_date=row[8]
                ))

            # 4. 기타 명세 조회
            cursor.execute('SELECT id, instruction_pef_result_id, other_specs_text, other_specs_detail FROM other_specifications WHERE instruction_pef_result_id = %s', (result.id,))
            for row in cursor.fetchall():
                result.other_specifications.append(OtherSpecifications(
                    id=row[0], instruction_pef_result_id=row[1],
                    other_specs_text=row[2], other_specs_detail=row[3]
                ))

            pef.result = result
            return pef

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            BaseRepository.close_db(conn=conn, cursor=cursor)
