from base_repository import BaseRepository
from typing import Optional, Dict, Any, List



class InstructionRepository:
    

    @staticmethod
    def create_instruction(type: int, performer_id: int, file_name: str) -> int:
        # type = 1 => PEF   type = 2 => 특자
        cursor, conn = BaseRepository.open_db()
        try:
            # 프로시저 호출
            cursor.callproc('sp_create_instruction', [type, performer_id, file_name, 0])
            
            # OUT 파라미터 가져오기
            for result in cursor.stored_results():
                inserted_id = result.fetchone()[0]
                break
            conn.commit()
            return inserted_id
        except Exception as e:
            conn.rollback()
            return e
        finally:
            BaseRepository.close_db(conn=conn, cursor=cursor)

    # @staticmethod
    # def get_all_instruction(type: int) -> List[Dict[str, Any]]:
    #     cursor, conn = BaseRepository.open_db()
    #     try:
