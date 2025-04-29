from database import get_db_connection
from typing import Optional, Dict, Any, List
# from datetime import datetime

class ContractRepository:
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
    def create_contract(uploader_id: int, contract_name: str, file_name: str) -> bool:
        cursor, conn = ContractRepository.open_db()
        try:
            cursor.execute(
                '''
                INSERT INTO contract (contract_name, file_name, uploader_id)
                VALUES (%s, %s, %s)
                ''',
                (contract_name, file_name, uploader_id)
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            ContractRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def get_all_contracts() -> List[Dict[str, Any]]:
        cursor, conn = ContractRepository.open_db()
        try:
            cursor.execute('SELECT * FROM contract')
            return cursor.fetchall()
        finally:
            ContractRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def get_only_uploaded_contracts() -> List[Dict[str, Any]]:
        cursor, conn = ContractRepository.open_db()
        try:
            cursor.execute('SELECT * FROM contract WHERE current_state = 0')
            return cursor.fetchall()
        finally:
            ContractRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def process_checklist(checklist_processer_id: int, contract_id: int) -> bool:
        cursor, conn = ContractRepository.open_db()
        try:
            cursor.execute(
                'UPDATE contract SET checklist_processer_id=%s, checklist_processed=NOW(), current_state=1 WHERE id=%s',
                (checklist_processer_id, contract_id)
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            ContractRepository.close_db(conn=conn, cursor=cursor)
    
    @staticmethod
    def get_on_progress_checklist_contracts() -> List[Dict[str, Any]]:
        cursor, conn = ContractRepository.open_db()
        try:
            cursor.execute('SELECT * FROM contract WHERE current_state = 1')
            return cursor.fetchall()
        finally:
            ContractRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def finish_checklist(contract_id: int, checklist_printable_file_path: str) -> bool:
        cursor, conn = ContractRepository.open_db()
        try:
            cursor.execute(
                'UPDATE contract SET checklist_printable_file_path = %s, current_state=2 WHERE id=%s',
                (checklist_printable_file_path, contract_id)
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            ContractRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def get_finished_checklist_contracts() -> List[Dict[str, Any]]:
        cursor, conn = ContractRepository.open_db()
        try:
            cursor.execute('SELECT * FROM contract WHERE current_state = 2')
            return cursor.fetchall()
        finally:
            ContractRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def process_keypoint(keypoint_processer_id: int, contract_id: int) -> bool:
        cursor, conn = ContractRepository.open_db()
        try:
            cursor.execute(
                'UPDATE contract SET keypoint_processer_id=%s, checklist_processed=NOW(), current_state=3 WHERE id=%s',
                (keypoint_processer_id, contract_id)
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            ContractRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def get_on_progress_keypoint_contracts() -> List[Dict[str, Any]]:
        cursor, conn = ContractRepository.open_db()
        try:
            cursor.execute('SELECT * FROM contract WHERE current_state = 3')
            return cursor.fetchall()
        finally:
            ContractRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def finish_keypoint(contract_id: int) -> bool:
        cursor, conn = ContractRepository.open_db()
        try:
            cursor.execute(
                'UPDATE contract SET current_state=4 WHERE id=%s',
                (contract_id)
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            ContractRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def get_finished_keypoint_contracts() -> List[Dict[str, Any]]:
        cursor, conn = ContractRepository.open_db()
        try:
            cursor.execute('SELECT * FROM contract WHERE current_state = 4')
            return cursor.fetchall()
        finally:
            ContractRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def find_by_id(id: int) -> Optional[Dict[str, Any]]:
        cursor, conn = ContractRepository.open_db()
        try:
            cursor.execute('SELECT * FROM contract WHERE id=%s', (id,))
            return cursor.fetchone()
        finally:
            ContractRepository.close_db(conn=conn, cursor=cursor)

    # @staticmethod
    # def delete_contract(id: int) -> bool:
    #     cursor, conn = ContractRepository.open_db()
    #     try:
