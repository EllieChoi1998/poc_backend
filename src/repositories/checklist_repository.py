from base_repository import BaseRepository
from typing import Optional, Dict, Any, List

class ChecklistRepository:
    

    @staticmethod
    def create_question(question: str) -> bool:
        cursor, conn = BaseRepository.open_db()

        try:
            cursor.execute(
                'INSERT INTO checklist(question) VALUES (%s)',
                (question,)  # 수정: 튜플로 변경하여 파라미터 전달 방식 수정
            )

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            BaseRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def update_question(checklist_id: int, question: str) -> bool:
        cursor, conn = BaseRepository.open_db()
        try:
            cursor.execute(
                'UPDATE checklist SET question = %s WHERE id = %s',
                (question, checklist_id)
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            BaseRepository.close_db(conn=conn, cursor=cursor)
    
    @staticmethod
    def get_all_questions() -> List[Dict[str, Any]]:  # 수정: 반환 타입 명확히 지정
        cursor, conn = BaseRepository.open_db()
        try:
            cursor.execute('SELECT * FROM checklist')
            return cursor.fetchall()
        finally:
            BaseRepository.close_db(cursor=cursor, conn=conn)

    @staticmethod
    def delete_question(question_id: int) -> bool:
        cursor, conn = BaseRepository.open_db()
        try:
            cursor.execute('DELETE FROM checklist WHERE id=%s', (question_id,))  # 수정: 튜플로 변경
            conn.commit()
            return cursor.rowcount > 0
        finally:
            BaseRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def find_by_question(question: str) -> Optional[Dict[str, Any]]:  # 수정: 반환 타입 명확히 지정
        cursor, conn = BaseRepository.open_db()
        try:
            cursor.execute('SELECT * FROM checklist WHERE question=%s', (question,))  # 수정: 튜플로 변경
            return cursor.fetchone()  # 수정: 단일 결과 반환으로 변경
        finally:
            BaseRepository.close_db(cursor=cursor, conn=conn)

    @staticmethod
    def find_by_id(id: int) -> Optional[Dict[str, Any]]:  # 수정: 반환 타입 추가
        cursor, conn = BaseRepository.open_db()
        try:
            cursor.execute('SELECT * FROM checklist WHERE id=%s', (id,))  # 수정: 튜플로 변경
            return cursor.fetchone()
        finally:
            BaseRepository.close_db(cursor=cursor, conn=conn)