from database import get_db_connection
from typing import Optional, Dict, Any, List
from base_repository import BaseRepository
class UserRepository:

    @staticmethod
    def find_by_login_id(login_id: str) -> Optional[Dict[str, Any]]:
        cursor, conn = BaseRepository.open_db()
        
        try:
            cursor.execute('SELECT * FROM user WHERE login_id = %s', (login_id,))
            return cursor.fetchone()
        finally:
            BaseRepository.close_db(conn, cursor)
    
    @staticmethod
    def find_by_ibk_id(ibk_id: str) -> Optional[Dict[str, Any]]:
        cursor, conn = BaseRepository.open_db()
        
        try:
            cursor.execute('SELECT * FROM user WHERE ibk_id = %s', (ibk_id,))
            return cursor.fetchone()
        finally:
            BaseRepository.close_db(conn, cursor)
    
    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> bool:
        cursor, conn = BaseRepository.open_db()
        
        try:
            cursor.execute(
                'INSERT INTO user (login_id, ibk_id, name, password, hiearchy, system_role, team_id, activate, refresh_token) '
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                (
                    user_data['login_id'], user_data['ibk_id'], user_data['name'], user_data['password'],
                    user_data['hiearchy'], user_data['system_role'],
                    user_data.get('team_id'), user_data.get('activate', 'T'), None
                )
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            BaseRepository.close_db(conn, cursor)
    
    @staticmethod
    def update_refresh_token(user_id: int, refresh_token: Optional[str]) -> bool:
        cursor, conn = BaseRepository.open_db()
        
        try:
            cursor.execute(
                'UPDATE user SET refresh_token = %s WHERE id = %s',
                (refresh_token, user_id)
            )
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            BaseRepository.close_db(conn, cursor)
    
    @staticmethod
    def find_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        cursor, conn = BaseRepository.open_db()
        
        try:
            cursor.execute('SELECT * FROM user WHERE id = %s', (user_id,))
            return cursor.fetchone()
        finally:
            BaseRepository.close_db(conn, cursor)
            
    @staticmethod
    def find_all() -> List[Dict[str, Any]]:
        cursor, conn = BaseRepository.open_db()
        
        try:
            cursor.execute('SELECT * FROM user WHERE activate = "T"')  # 활성화된 사용자만 조회
            return cursor.fetchall()
        finally:
            BaseRepository.close_db(conn, cursor)

    @staticmethod
    def update(user_id: int, user_data: Dict[str, Any]) -> bool:
        """
        사용자 정보를 업데이트합니다.
        
        Args:
            user_id: 업데이트할 사용자의 ID
            user_data: 업데이트할 사용자 데이터
            
        Returns:
            bool: 업데이트 성공 여부
        """
        cursor, conn = BaseRepository.open_db()
        
        try:
            # 업데이트할 필드와 값을 동적으로 구성
            update_fields = []
            values = []
            
            for key, value in user_data.items():
                if key != 'id':  # ID는 업데이트하지 않음
                    update_fields.append(f"{key} = %s")
                    values.append(value)
            
            # ID는 WHERE 절에서 사용
            values.append(user_id)
            
            # SQL 쿼리 구성
            sql = f"UPDATE user SET {', '.join(update_fields)} WHERE id = %s"
            
            # 쿼리 실행
            cursor.execute(sql, values)
            conn.commit()
            
            # 영향받은 행이 있으면 성공
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            BaseRepository.close_db(conn, cursor)

    @staticmethod
    def delete(user_id: int) -> bool:
        """
        사용자를 삭제합니다(비활성화).
        실제로 삭제하지 않고 activate 필드를 'F'로 설정합니다.
        
        Args:
            user_id: 삭제할 사용자의 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        cursor, conn = BaseRepository.open_db()
        
        try:
            sql = "UPDATE user SET activate = 'F' WHERE id = %s"
            cursor.execute(sql, (user_id,))
            conn.commit()
            
            # 영향받은 행이 있으면 성공
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            BaseRepository.close_db(conn, cursor)

    @staticmethod
    def find_user_activation(user_id: int) -> bool:
        """
        특정 사용자의 활성화 여부를 확인합니다.
        """

        cursor, conn = BaseRepository.open_db()
        try:
            sql = "SELECT * FROM user WHERE id=%s AND activate='T'"
            cursor.execute(sql, (user_id,))
            if cursor.fetchone(): 
                return True
        except Exception as e:
            return False
        finally:
            BaseRepository.close_db(conn=conn, cursor=cursor)