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

@staticmethod
def find_all_checklist_results_by_contract(contract_id: int) -> Optional[Dict[str, Any]]:
    cursor, conn = ChecklistResultRepository.open_db()

    try:
        query = """
        SELECT 
            c.id AS contract_id,
            c.contract_name,
            c.file_name,
            c.uploader_id,
            c.checklist_processer_id,
            c.uploaded_at,
            c.checklist_processed,
            c.checklist_printable_file_path,
            c.current_state,

            cr.id AS checklist_result_id,
            cr.checklist_id,
            cr.memo,

            cl.id AS checklist_id,
            cl.question,

            crv.id AS checklist_result_value_id,
            crv.clause_num,
            crv.located_page

        FROM contract c
        LEFT JOIN checklist_result cr ON cr.contract_id = c.id
        LEFT JOIN checklist cl ON cl.id = cr.checklist_id
        LEFT JOIN checklist_result_value crv ON crv.checklist_result_id = cr.id
        WHERE c.id = %s
        ORDER BY cr.id, crv.id
        """

        cursor.execute(query, (contract_id,))
        rows = cursor.fetchall()

        if not rows:
            return {}

        # contract 정보는 하나만 가져오면 됨
        contract_info = {
            "contract_name": rows[0]["contract_name"],
            "file_name": rows[0]["file_name"],
            "uploader_id": rows[0]["uploader_id"],
            "checklist_processer_id": rows[0]["checklist_processer_id"],
            "uploaded_at": str(rows[0]["uploaded_at"]),
            "checklist_processed": str(rows[0]["checklist_processed"]) if rows[0]["checklist_processed"] else None,
            "checklist_printable_file_path": rows[0]["checklist_printable_file_path"],
            "current_state": rows[0]["current_state"]
        }

        checklist_results_dict = {}

        for row in rows:
            cr_id = row["checklist_result_id"]
            if cr_id is None:
                continue  # 연결된 checklist_result가 없을 경우

            if cr_id not in checklist_results_dict:
                checklist_results_dict[cr_id] = {
                    "id": cr_id,
                    "memo": row["memo"],
                    "checklist": {
                        "id": row["checklist_id"],
                        "question": row["question"]
                    },
                    "values": []
                }

            if row["checklist_result_value_id"] is not None:
                checklist_results_dict[cr_id]["values"].append({
                    "id": row["checklist_result_value_id"],
                    "clause_num": row["clause_num"],
                    "located_page": row["located_page"]
                })

        return {
            "contract": contract_info,
            "checklist_results": list(checklist_results_dict.values())
        }

    finally:
        ChecklistResultRepository.close_db(cursor=cursor, conn=conn)
