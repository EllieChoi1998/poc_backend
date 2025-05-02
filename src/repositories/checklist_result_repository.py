from typing import Optional, Dict, Any, List
from models import Checklist_Result_Value
from database import get_db_connection


class ChecklistResultRepository:

    class DB:
        def __enter__(self):
            self.conn = get_db_connection()
            self.cursor = self.conn.cursor(dictionary=True)
            return self.cursor, self.conn

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.cursor.close()
            self.conn.close()

    @staticmethod
    def create_result(
        checklist_result_values: Optional[List[Checklist_Result_Value]],
        contract_id: int,
        checklist_id: int
    ) -> bool:
        with ChecklistResultRepository.DB() as (cursor, conn):
            try:
                cursor.execute(
                    'INSERT INTO checklist_result (contract_id, checklist_id) VALUES (%s, %s)',
                    (contract_id, checklist_id)
                )
                checklist_result_id = cursor.lastrowid

                if checklist_result_values:
                    for crv in checklist_result_values:
                        cursor.execute(
                            'INSERT INTO checklist_result_value (checklist_result_id, clause_num, located_page) VALUES (%s, %s, %s)',
                            (checklist_result_id, crv.clause_num, crv.located_page)
                        )

                conn.commit()
                return True
            except Exception:
                conn.rollback()
                raise

    @staticmethod
    def update_memo(checklist_result_id: int, memo: str) -> bool:
        with ChecklistResultRepository.DB() as (cursor, conn):
            try:
                cursor.execute(
                    'UPDATE checklist_result SET memo = %s WHERE id = %s',
                    (memo, checklist_result_id)
                )
                conn.commit()
                return cursor.rowcount > 0
            except Exception:
                conn.rollback()
                raise

    @staticmethod
    def find_all_checklist_results_by_contract(contract_id: int) -> Optional[Dict[str, Any]]:
        with ChecklistResultRepository.DB() as (cursor, _):
            cursor.execute("""
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
            """, (contract_id,))

            rows = cursor.fetchall()
            if not rows:
                return {}

            contract_info = {
                "contract_name": rows[0]["contract_name"],
                "file_name": rows[0]["file_name"],
                "uploader_id": rows[0]["uploader_id"],
                "checklist_processer_id": rows[0]["checklist_processer_id"],
                "uploaded_at": str(rows[0]["uploaded_at"]),
                "checklist_processed": (
                    str(rows[0]["checklist_processed"]) if rows[0]["checklist_processed"] else None
                ),
                "checklist_printable_file_path": rows[0]["checklist_printable_file_path"],
                "current_state": rows[0]["current_state"]
            }

            checklist_results: Dict[int, Dict[str, Any]] = {}

            for row in rows:
                cr_id = row["checklist_result_id"]
                if cr_id is None:
                    continue

                if cr_id not in checklist_results:
                    checklist_results[cr_id] = {
                        "id": cr_id,
                        "memo": row["memo"],
                        "checklist": {
                            "id": row["checklist_id"],
                            "question": row["question"]
                        },
                        "values": []
                    }

                if row["checklist_result_value_id"] is not None:
                    checklist_results[cr_id]["values"].append({
                        "id": row["checklist_result_value_id"],
                        "clause_num": row["clause_num"],
                        "located_page": row["located_page"]
                    })

            return {
                "contract": contract_info,
                "checklist_results": list(checklist_results.values())
            }

    @staticmethod
    def delete_checklist_result_value(value_id: int) -> bool:
        with ChecklistResultRepository.DB() as (cursor, conn):
            cursor.execute('DELETE FROM checklist_result_value WHERE id = %s', (value_id,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete_checklist_result(result_id: int) -> bool:
        with ChecklistResultRepository.DB() as (cursor, conn):
            cursor.execute('DELETE FROM checklist_result WHERE id = %s', (result_id,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def get_value_by_value_id(value_id: int) -> Optional[Dict[str, Any]]:
        with ChecklistResultRepository.DB() as (cursor, _):
            cursor.execute('SELECT * FROM checklist_result_value WHERE id = %s', (value_id,))
            return cursor.fetchone()
