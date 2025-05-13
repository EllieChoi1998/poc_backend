from base_repository import BaseRepository
from typing import Optional, List, Dict, Any
from models import InstructionSpecialResult, Attachment
from datetime import date

class SpecialRepository(BaseRepository):

    @staticmethod
    def create_with_result(
        performer_id: int,
        file_name: str,
        result: Optional[InstructionSpecialResult] = None,
        attachments: Optional[List[Attachment]] = None
    ) -> int:
        """
        instruction_special +  instruction_special_result 함께 저장
        """
        with BaseRepository.DB() as (cursor, conn):
            try:
                # 1. instruction_special 저장
                insert_instruction_sql = """
                INSERT INTO instruction_special (
                    performer_id, file_name
                ) VALUES (%s, %s)
                """
                cursor.execute(insert_instruction_sql, (performer_id, file_name))
                instruction_special_id = cursor.lastrowid

                # 2. result 저장 (조건부)
                if result:
                    insert_result_sql = """
                    INSERT INTO instruction_special_result (
                        instruction_special_id, result_content, all_qualities, average_quality, saved_json
                    ) VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_result_sql, (instruction_special_id, result.result_content, result.all_qualities, result.average_quality, result.saved_json))
                
                # 3. attachment 저장 (조건부)
                if attachments:
                    for af in attachments:
                        cursor.execute(
                            "INSERT INTO attachment(instruction_special_id, file_name) VALUES(%s, %s)",
                            (instruction_special_id, af.file_name)
                        )

                conn.commit()
                return instruction_special_id
            except Exception as e:
                conn.rollback()
                raise e
    @staticmethod
    def create_another_result(
        instruction_special_id: int,
        result: Optional[InstructionSpecialResult] = None
    ) -> bool:
        if result:
            with BaseRepository.DB() as (cursor, conn):
                try:
                    insert_result_sql = """
                    INSERT INTO instruction_special_result (
                        instruction_special_id, result_content, all_qualities, average_quality, saved_json
                    ) VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_result_sql, (instruction_special_id, result.result_content, result.all_qualities, result.average_quality, result.saved_json))
                    conn.commit()
                    return True
                except Exception as e:
                    conn.rollback()
                    raise e
        return False
        
    @staticmethod
    def update_result_content(
        instruction_special_id: int,
        result_id: int,
        new_content: str
    ) -> bool:
        """
        InstructionSpecialResult.result_content만 수정
        """
        with BaseRepository.DB() as (cursor, conn):
            try:
                cursor.execute(
                    "UPDATE instruction_special_result SET result_content = %s WHERE id=%s AND instruction_special_id=%s",
                    (new_content, result_id, instruction_special_id,)
                )
                affected_rows = cursor.rowcount
                conn.commit()
                return affected_rows > 0
            except Exception as e:
                conn.rollback()
                raise e
    
    @staticmethod
    def update_result_usability(
        instruction_special_id: int,
        result_id: int,
        usability: str
    ) -> bool:
        """
        InstructionSpecialResult.usability만 수정
        """
        with BaseRepository.DB() as (cursor, conn):
            try:
                cursor.execute(
                    "UPDATE instruction_special_result SET usability = %s WHERE id=%s AND instruction_special_id=%s",
                    (usability, result_id, instruction_special_id,)
                )
                affected_rows = cursor.rowcount
                conn.commit()
                return affected_rows > 0
            except Exception as e:
                conn.rollback()
                raise e
            
    @staticmethod
    def update_result_json(
        instruction_special_id: int,
        result_id: int,
        new_json: str
    ) -> bool:
        """
        InstructionSpecialResult.saved_json만 수정
        """
        with BaseRepository.DB() as (cursor, conn):
            try:
                cursor.execute(
                    "UPDATE instruction_special_result SET saved_json = %s WHERE id=%s AND instruction_special_id=%s",
                    (new_json, result_id, instruction_special_id,)
                )
                affected_rows = cursor.rowcount
                conn.commit()
                return affected_rows > 0
            except Exception as e:
                conn.rollback()
                raise e
    
    @staticmethod
    def get_all_special_instructions() -> List[Dict[str, Any]]:
        sql = "SELECT * FROM instruction_special ORDER BY id DESC"
        with BaseRepository.DB() as (cursor, _):
            cursor.execute(sql)
            return cursor.fetchall()
    
    @staticmethod
    def get_all_results_by_special_instruction_id(instruction_special_id: int) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM instruction_special_result WHERE instruction_special_id = %s ORDER BY id DESC"
        with BaseRepository.DB() as (cursor, _):
            cursor.execute(sql, (instruction_special_id,))  # 수정: 튜플로 변환
            return cursor.fetchall()
    
    @staticmethod
    def get_result_by_id(result_id: int) -> Dict[str, Any]:
        sql = "SELECT * FROM instruction_special_result WHERE id = %s"
        with BaseRepository.DB() as (cursor, _):
            cursor.execute(sql, (result_id,))  # 수정: 튜플로 변환
            return cursor.fetchone()  # 수정: fetchall() -> fetchone()
        
    @staticmethod
    def delete_result_by_id(result_id: int) -> bool:
        with BaseRepository.DB() as (cursor, conn):  # 수정: try/except 블록에서 with 블록으로 변경
            try:
                sql = "DELETE FROM instruction_special_result WHERE id = %s"
                cursor.execute(sql, (result_id,))
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                conn.rollback()
                raise e

    @staticmethod
    def delete_special_instruction(instruction_special_id: int) -> bool:
        with BaseRepository.DB() as (cursor, conn):  # 수정: try/except 블록에서 with 블록으로 변경
            try:
                sql = "DELETE FROM instruction_special WHERE id = %s"
                cursor.execute(sql, (instruction_special_id,))
                conn.commit()
                return cursor.rowcount > 0
            except Exception as e:
                conn.rollback()
                raise e