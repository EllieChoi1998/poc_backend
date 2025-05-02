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
    def find_all_checklist_results_by_contract_id(contract_id: int) -> List[Dict[str, Any]]:
        cursor, conn = ChecklistResultRepository.open_db()

        try:
            query = """
                SELECT
                    c.contract_name,
                    c.file_name,
                    c.uploader_id,
                    c.checklist_processer_id,
                    c.uploaded_at,
                    c.checklist_processed,
                    c.checklist_printable_file_path,
                    c.current_state,

                    cr.id AS checklist_result_id,
                    cr.contract_id,
                    cr.checklist_id,
                    cr.memo,

                    crv.id AS checklist_result_value_id,
                    crv.clause_num,
                    crv.located_page,

                    cl.id AS checklist_id_full,
                    cl.question
                FROM contract c
                LEFT JOIN checklist_result cr ON c.id = cr.contract_id
                LEFT JOIN checklist_result_value crv ON cr.id = crv.checklist_result_id
                LEFT JOIN checklist cl ON cr.checklist_id = cl.id
                WHERE c.id = %s
            """

            cursor.execute(query, (contract_id,))
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            # 결과 구조화
            result_dict: Dict[int, Dict[str, Any]] = {}
            for row in rows:
                row_data = dict(zip(columns, row))
                checklist_result_id = row_data['checklist_result_id']

                if checklist_result_id not in result_dict:
                    result_dict[checklist_result_id] = {
                        "contract": {
                            "contract_name": row_data["contract_name"],
                            "file_name": row_data["file_name"],
                            "uploader_id": row_data["uploader_id"],
                            "checklist_processer_id": row_data["checklist_processer_id"],
                            "uploaded_at": row_data["uploaded_at"],
                            "checklist_processed": row_data["checklist_processed"],
                            "checklist_printable_file_path": row_data["checklist_printable_file_path"],
                            "current_state": row_data["current_state"]
                        },
                        "checklist_result": {
                            "id": checklist_result_id,
                            "contract_id": row_data["contract_id"],
                            "checklist_id": row_data["checklist_id"],
                            "memo": row_data["memo"],
                            "checklist": {
                                "id": row_data["checklist_id_full"],
                                "question": row_data["question"]
                            },
                            "values": []
                        }
                    }

                if row_data["checklist_result_value_id"] is not None:
                    result_dict[checklist_result_id]["checklist_result"]["values"].append({
                        "id": row_data["checklist_result_value_id"],
                        "clause_num": row_data["clause_num"],
                        "located_page": row_data["located_page"]
                    })

            return list(result_dict.values())

        finally:
            ChecklistResultRepository.close_db(cursor=cursor, conn=conn)
