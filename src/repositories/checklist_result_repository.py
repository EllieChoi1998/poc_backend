from database import get_db_connection
from typing import Optional, Dict, Any, List
from models import Checklist_Result_Value

class ChecklistResultRepository:
    @staticmethod
    def open_db():
        conn = get_db_connection()
        cursor = conn.cursor()
        return cursor, conn
    @staticmethod
    def close_db(conn, cursor):
        cursor.close()
        conn.close()

    @staticmethod
    def create_result(checklist_result_values: List[Checklist_Result_Value], contract_id: int, checklist_id: int) -> bool:
        cursor, conn = ChecklistResultRepository.open_db()

        try:
            cursor.execute(
                'INSERT INTO checklist_result(contract_id, checklist_id) VALUES (%s, %s)',
                (contract_id, checklist_id,)
            )
            checklist_result_id = cursor.lastrowid

            
            for crv in checklist_result_values:
                cursor.execute(
                    'INSERT INTO checklist_result_value(checklist_result_id, clause_num, located_page) VALUES (%s, %s, %s)',
                    (checklist_result_id, crv.clause_num, crv.located_page)
                )

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            ChecklistResultRepository.close_db(cursor=cursor, conn=conn)

    @staticmethod
    def update_memo(checklist_result_id:int, memo:str) -> bool:
        cursor, conn = ChecklistResultRepository.open_db()

        try:
            cursor.execute(
                'UPDATE checklist_result SET memo = %s WHERE id=%s',
                (memo, checklist_result_id)
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            ChecklistResultRepository.close_db(cursor=cursor, conn=conn)