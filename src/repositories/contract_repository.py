from base_repository import BaseRepository
from typing import Optional, Dict, Any, List

class ContractRepository:
    @staticmethod
    def create_contract(uploader_id: int, contract_name: str, file_name: str):
        cursor, conn = BaseRepository.open_db()
        try:
            cursor.execute(
                '''
                INSERT INTO contract (contract_name, file_name, uploader_id)
                VALUES (%s, %s, %s)
                ''',
                (contract_name, file_name, uploader_id)
            )
            
            # 삽입된 행의 ID 가져오기
            contract_id = cursor.lastrowid
            
            conn.commit()
            
            # 계약서 ID 반환 (true가 아님)
            return contract_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            BaseRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def get_all_contracts() -> List[Dict[str, Any]]:
        cursor, conn = BaseRepository.open_db()
        try:
            cursor.execute('SELECT * FROM contract')
            return cursor.fetchall()
        finally:
            BaseRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def get_only_uploaded_contracts() -> List[Dict[str, Any]]:
        cursor, conn = BaseRepository.open_db()
        try:
            cursor.execute('SELECT * FROM contract WHERE current_state = 0')
            return cursor.fetchall()
        finally:
            BaseRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def process_checklist(checklist_processer_id: int, contract_id: int) -> bool:
        cursor, conn = BaseRepository.open_db()
        try:
            cursor.execute(
                'UPDATE contract SET checklist_processer_id=%s, checklist_processed_at=NOW(), current_state=1 WHERE id=%s',
                (checklist_processer_id, contract_id)
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            BaseRepository.close_db(conn=conn, cursor=cursor)
    
    @staticmethod
    def get_on_progress_checklist_contracts() -> List[Dict[str, Any]]:
        cursor, conn = BaseRepository.open_db()
        try:
            cursor.execute('SELECT * FROM contract WHERE current_state = 1')
            return cursor.fetchall()
        finally:
            BaseRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def finish_checklist(contract_id: int, checklist_printable_file_path: str) -> bool:
        cursor, conn = BaseRepository.open_db()
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
            BaseRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def get_finished_checklist_contracts() -> List[Dict[str, Any]]:
        cursor, conn = BaseRepository.open_db()
        try:
            cursor.execute('SELECT * FROM contract WHERE current_state = 2')
            return cursor.fetchall()
        finally:
            BaseRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def process_keypoint(keypoint_processer_id: int, contract_id: int) -> bool:
        cursor, conn = BaseRepository.open_db()
        try:
            cursor.execute(
                'UPDATE contract SET keypoint_processer_id=%s, keypoint_processed_at=NOW(), current_state=3 WHERE id=%s',
                (keypoint_processer_id, contract_id)
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            BaseRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def get_on_progress_keypoint_contracts() -> List[Dict[str, Any]]:
        cursor, conn = BaseRepository.open_db()
        try:
            cursor.execute('SELECT * FROM contract WHERE current_state = 3')
            return cursor.fetchall()
        finally:
            BaseRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def finish_keypoint(contract_id: int) -> bool:
        cursor, conn = BaseRepository.open_db()
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
            BaseRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def get_finished_keypoint_contracts() -> List[Dict[str, Any]]:
        cursor, conn = BaseRepository.open_db()
        try:
            cursor.execute('SELECT * FROM contract WHERE current_state = 4')
            return cursor.fetchall()
        finally:
            BaseRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def find_by_id(id: int) -> Optional[Dict[str, Any]]:
        cursor, conn = BaseRepository.open_db()
        try:
            cursor.execute('SELECT * FROM contract WHERE id=%s', (id,))
            return cursor.fetchone()
        finally:
            BaseRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def delete_contract(id: int) -> bool:
        with BaseRepository.DB() as (cursor, conn):
            cursor.execute('DELETE FROM contract WHERE id= %s', (id, ))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def find_by_file_path(contract_name: str, file_name: str) -> Optional[Dict[str, Any]]:
        cursor, conn = BaseRepository.open_db()
        try:
            cursor.execute('SELECT * FROM contract WHERE contract_name=%s AND file_name=%s',
                           (contract_name, file_name))
            return cursor.fetchone()
        finally:
            BaseRepository.close_db(conn=conn, cursor=cursor)