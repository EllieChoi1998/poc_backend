from database import get_db_connection
from typing import Optional, Dict, Any, List

class UserRepository:
    @staticmethod
    def find_by_login_id(login_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('SELECT * FROM user WHERE login_id = %s', (login_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def find_by_ibk_id(ibk_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('SELECT * FROM user WHERE ibk_id = %s', (ibk_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        
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
            cursor.close()
            conn.close()
    
    @staticmethod
    def update_refresh_token(user_id: int, refresh_token: Optional[str]) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        
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
            cursor.close()
            conn.close()
    
    @staticmethod
    def find_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('SELECT * FROM user WHERE id = %s', (user_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
            
    @staticmethod
    def find_all() -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('SELECT * FROM user')
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()