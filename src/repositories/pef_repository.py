from base_repository import BaseRepository
from typing import Optional, List, Dict, Any
from models import TransactionHistory
from datetime import date

class PEFRepository(BaseRepository):

    @staticmethod
    def create_with_transactions(
        performer_id: int,
        file_name: str,
        is_fund_item: Optional[str],
        company_detail: Optional[str],
        other_specs_text: Optional[str],
        transactions: Optional[List[TransactionHistory]] = None
    ) -> int:
        """
        instruction_pef + 연결된 transaction_history 리스트를 함께 저장
        :return: 생성된 instruction_pef.id
        """
        with BaseRepository.DB() as (cursor, conn):
            try:
                # 1. instruction_pef 저장
                insert_instruction_sql = """
                INSERT INTO instruction_pef (
                    performer_id, file_name, is_fund_item, company_detail, other_specs_text
                ) VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(insert_instruction_sql, (
                    performer_id, file_name, is_fund_item or 'F',
                    company_detail, other_specs_text
                ))
                instruction_pef_id = cursor.lastrowid

                # 2. transaction_history 저장 (조건부)
                if transactions:
                    insert_transaction_sql = """
                    INSERT INTO transaction_history (
                        instruction_pef_id, deal_type, deal_object,
                        bank_name, account_number, holder_name,
                        amount, process_date
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    for tx in transactions:
                        cursor.execute(insert_transaction_sql, (
                            instruction_pef_id,
                            tx.deal_type,
                            tx.deal_object,
                            tx.bank_name,
                            tx.account_number,
                            tx.holder_name,
                            tx.amount,
                            tx.process_date  # type: date
                        ))

                conn.commit()
                return instruction_pef_id

            except Exception as e:
                conn.rollback()
                raise e

    @staticmethod
    def create_transaction_history(
        instruction_pef_id: int,
        deal_type: str,
        deal_object: str,
        bank_name: str,
        account_number: str,
        holder_name: str,
        amount: str,
        process_date: date
    ) -> bool:
        sql = """
        INSERT INTO transaction_history (
            instruction_pef_id, deal_type, deal_object,
            bank_name, account_number, holder_name,
            amount, process_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            with BaseRepository.DB() as (cursor, conn):
                cursor.execute(sql, (
                    instruction_pef_id, deal_type, deal_object,
                    bank_name, account_number, holder_name,
                    amount, process_date
                ))
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            raise e

    @staticmethod
    def get_all_pef_instructions() -> List[Dict[str, Any]]:
        sql = "SELECT * FROM instruction_pef ORDER BY id DESC"
        with BaseRepository.DB() as (cursor, _):
            cursor.execute(sql)
            return cursor.fetchall()

    @staticmethod
    def get_transaction_histories_by_pef_instruction_id(instruction_pef_id: int) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM transaction_history WHERE instruction_pef_id = %s ORDER BY id ASC"
        with BaseRepository.DB() as (cursor, _):
            cursor.execute(sql, (instruction_pef_id,))
            return cursor.fetchall()
    
    @staticmethod
    def update_transaction_history_by_id(
        transaction_history: TransactionHistory
    ) -> bool:
        sql = """
        UPDATE transaction_history
        SET deal_type = %s,
            deal_object = %s,
            bank_name = %s,
            account_number = %s,
            holder_name = %s,
            amount = %s,
            process_date = %s
        WHERE id = %s
        """
        try:
            with BaseRepository.DB() as (cursor, conn):
                cursor.execute(sql, (
                    transaction_history.deal_type,
                    transaction_history.deal_object,
                    transaction_history.bank_name,
                    transaction_history.account_number,
                    transaction_history.holder_name,
                    transaction_history.amount,
                    transaction_history.process_date,
                    transaction_history.id
                ))
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            raise e

    @staticmethod
    def delete_instruction_pef(instruction_pef_id: int) -> bool:
        sql = "DELETE FROM instruction_pef WHERE id = %s"
        try:
            with BaseRepository.DB() as (cursor, conn):
                cursor.execute(sql, (instruction_pef_id,))
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            raise e

        
    @staticmethod
    def delete_transaction_history(transaction_history_id: int) -> bool:
        sql = "DELETE FROM transaction_history WHERE id = %s"
        try:
            with BaseRepository.DB() as (cursor, conn):
                cursor.execute(sql, (transaction_history_id,))
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            raise e

