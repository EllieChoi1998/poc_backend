from typing import Optional, Dict, Any, List
from database import get_db_connection
from base_repository import BaseRepository
class KeypointResultRepository:

    @staticmethod
    def create_result_by_ai(contract_id: int, terms_id: int, match_rate: float) -> bool:
        with BaseRepository.DB() as (cursor, conn):
            try:
                cursor.execute(
                    'INSERT INTO keypoint_result(contract_id, termsNconditions_id, match_rate) VALUES(%s, %s, %s)',
                    (contract_id, terms_id, match_rate)
                )
                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                raise e
            
    @staticmethod
    def create_result_by_user(contract_id: int, terms_id: int) -> bool:
        with BaseRepository.DB() as (cursor, conn):
            try:
                cursor.execute(
                    'SELECT * FROM keypoint_result WHERE contract_id=%s AND termsNconditions_id=%s',
                    (contract_id, terms_id)
                )

                if not cursor.fetchall():

                    cursor.execute(
                        'INSERT INTO keypoint_result(contract_id, termsNconditions_id, match_rate) VALUES(%s, %s, NULL)',
                        (contract_id, terms_id)
                    )

                    conn.commit()
                    return True
                else:
                    raise ValueError
            except Exception as e:
                conn.rollback()
                raise e
            
    @staticmethod
    def find_result_by_contract_id(contract_id: int) -> Optional[Dict[str, Any]]:
        '''
        Returns a dictionary containing contract_id and a list of keypoint results.
        
        returns: dict containing contract_id and list of result dictionaries
            {
                "contract_id": 1,
                "results": [
                    {
                        "termsNconditions_id": 52,
                        "termsNconditions_code": "A2685",
                        "termsNconditions_query": "주식관련사채 투자한도",
                        "keypoint_result_id": 3,
                        "match_rate": 92.33
                    },
                    {
                        "termsNconditions_id": 54,
                        "termsNconditions_code": "A2686",
                        "termsNconditions_query": "주식관련사채-투자한도",
                        "keypoint_result_id": 2,
                        "match_rate": 52.33
                    },
                    ...
                ]
            }
        '''
        
        with BaseRepository.DB() as (cursor, _):
            cursor.execute("""
                SELECT 
                    c.id AS contract_id,
                    t.id AS termsNconditions_id,
                    t.code AS termsNconditions_code,
                    t.query AS termsNconditions_query,
                    kr.id AS keypoint_result_id,
                    kr.match_rate AS match_rate
                FROM contract c
                LEFT JOIN keypoint_result kr ON kr.contract_id = c.id
                LEFT JOIN termsNconditions t ON t.id = kr.termsNconditions_id
                WHERE c.id = %s
                ORDER BY kr.match_rate DESC
            """, (contract_id, ))

            rows = cursor.fetchall()

            if not rows:
                return None
            
            result = {
                "contract_id": contract_id,
                "results": []
            }
            
            for row in rows:
                # Skip rows where there's no valid keypoint_result_id
                if row["keypoint_result_id"] is None:
                    continue
                    
                result["results"].append({
                    "termsNconditions_id": row["termsNconditions_id"],
                    "termsNconditions_code": row["termsNconditions_code"],
                    "termsNconditions_query": row["termsNconditions_query"],
                    "keypoint_result_id": row["keypoint_result_id"],
                    "match_rate": row["match_rate"]
                })
            
            return result

    @staticmethod
    def delete_keypoint_result(result_id: int) -> bool:
        with BaseRepository.DB() as (cursor, conn):
            cursor.execute('DELETE FROM keypoint_result WHERE id= %s', (result_id, ))
            conn.commit()
            return cursor.rowcount > 0
