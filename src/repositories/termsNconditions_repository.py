from database import get_db_connection
from typing import Optional, Dict, Any, List

class TermsNConditionsRepository:
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
    def create_query(query: str, code: str) -> bool:
        cursor, conn = TermsNConditionsRepository.open_db()

        try:
            cursor.execute(
                'INSERT INTO termsNconditions(code, query) VALUES (%s, %s)',
                (code, query)  # 수정: 튜플로 변경하여 파라미터 전달 방식 수정
            )

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            TermsNConditionsRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def update_query(termsNconditions_id: int, code:str, query: str) -> bool:
        cursor, conn = TermsNConditionsRepository.open_db()
        try:
            cursor.execute(
                'UPDATE termsNconditions SET query = %s, code = %s WHERE id = %s',
                (query, code, termsNconditions_id)
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            TermsNConditionsRepository.close_db(conn=conn, cursor=cursor)
    
    @staticmethod
    def get_all_querys() -> List[Dict[str, Any]]:  # 수정: 반환 타입 명확히 지정
        cursor, conn = TermsNConditionsRepository.open_db()
        try:
            cursor.execute('SELECT * FROM termsNconditions')
            return cursor.fetchall()
        finally:
            TermsNConditionsRepository.close_db(cursor=cursor, conn=conn)

    @staticmethod
    def delete_query(query_id: int) -> bool:
        cursor, conn = TermsNConditionsRepository.open_db()
        try:
            cursor.execute('DELETE FROM termsNconditions WHERE id=%s', (query_id,))  # 수정: 튜플로 변경
            conn.commit()
            return cursor.rowcount > 0
        finally:
            TermsNConditionsRepository.close_db(conn=conn, cursor=cursor)

    @staticmethod
    def find_by_query(query: str) -> Optional[Dict[str, Any]]:  # 수정: 반환 타입 명확히 지정
        cursor, conn = TermsNConditionsRepository.open_db()
        try:
            cursor.execute('SELECT * FROM termsNconditions WHERE query=%s', (query,))  # 수정: 튜플로 변경
            return cursor.fetchone()  # 수정: 단일 결과 반환으로 변경
        finally:
            TermsNConditionsRepository.close_db(cursor=cursor, conn=conn)

    @staticmethod
    def find_by_code(code: str) -> Optional[Dict[str, Any]]:  # 수정: 반환 타입 명확히 지정
        cursor, conn = TermsNConditionsRepository.open_db()
        try:
            cursor.execute('SELECT * FROM termsNconditions WHERE code=%s', (code,))  # 수정: 튜플로 변경
            return cursor.fetchone()  # 수정: 단일 결과 반환으로 변경
        finally:
            TermsNConditionsRepository.close_db(cursor=cursor, conn=conn)

    @staticmethod
    def find_by_id(id: int) -> Optional[Dict[str, Any]]:  # 수정: 반환 타입 추가
        cursor, conn = TermsNConditionsRepository.open_db()
        try:
            cursor.execute('SELECT * FROM termsNconditions WHERE id=%s', (id,))  # 수정: 튜플로 변경
            return cursor.fetchone()
        finally:
            TermsNConditionsRepository.close_db(cursor=cursor, conn=conn)