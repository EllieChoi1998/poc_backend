# src/services/pef_service.py

from repositories.pef_repository import PEFRepository
from repositories.user_repository import UserRepository
from typing import Optional, List, Dict, Any
from models import TransactionHistory, InstructionPEF
from base_service import BaseService
from datetime import date


class PEFService(BaseService):
    @staticmethod
    def create_pef_with_transactions(
        user_id: int, 
        pef: InstructionPEF,
        transactions: Optional[List[TransactionHistory]] = None
    ) -> int:
        """
        PEF 지시서와 연결된 거래 내역을 함께 생성
        
        Args:
            user_id: 요청하는 사용자 ID
            pef: InstructionPEF 모델 객체
            transactions: 거래 내역 목록
            
        Returns:
            생성된 instruction_pef의 ID
        """
        # 사용자 검증
        BaseService.validate_user(user_id)
        
        # PEF 지시서 및 거래 내역 생성
        instruction_pef_id = PEFRepository.create_with_transactions(
            performer_id=user_id,
            file_name=pef.file_name,
            is_fund_item=pef.is_fund_item,
            company_detail=pef.company_detail,
            other_specs_text=pef.other_specs_text,
            transactions=transactions
        )
        
        return instruction_pef_id

    @staticmethod
    def add_transaction_to_pef(
        user_id: int,
        instruction_pef_id: int,
        transaction: TransactionHistory
    ) -> bool:
        """
        기존 PEF 지시서에 새로운 거래 내역 추가
        
        Args:
            user_id: 요청하는 사용자 ID
            instruction_pef_id: PEF 지시서 ID
            transaction: 거래 내역 객체
            
        Returns:
            성공 여부
        """
        # 사용자 검증
        BaseService.validate_user(user_id)
        
        # 거래 내역 추가
        return PEFRepository.create_transaction_history(
            instruction_pef_id=instruction_pef_id,
            deal_type=transaction.deal_type,
            deal_object=transaction.deal_object,
            bank_name=transaction.bank_name,
            account_number=transaction.account_number,
            holder_name=transaction.holder_name,
            amount=transaction.amount,
            process_date=transaction.process_date
        )

    @staticmethod
    def get_all_pef_instructions(user_id: int) -> List[InstructionPEF]:
        """
        모든 PEF 지시서 목록 조회
        
        Args:
            user_id: 요청하는 사용자 ID
            
        Returns:
            PEF 지시서 목록
        """
        # 사용자 검증
        BaseService.validate_user(user_id)
        
        # 모든 PEF 지시서 조회 및 모델로 변환
        pef_data_list = PEFRepository.get_all_pef_instructions()
        pef_instructions = []
        
        for pef_data in pef_data_list:
            pef_instruction = InstructionPEF(
                id=pef_data.get('id'),
                performer_id=pef_data.get('performer_id'),
                file_name=pef_data.get('file_name'),
                is_fund_item=pef_data.get('is_fund_item'),
                company_detail=pef_data.get('company_detail'),
                other_specs_text=pef_data.get('other_specs_text'),
                created_at=pef_data.get('created_at')
            )
            pef_instructions.append(pef_instruction)
            
        return pef_instructions

    @staticmethod
    def get_pef_instruction_by_id(user_id: int, instruction_pef_id: int) -> Optional[InstructionPEF]:
        """
        특정 ID의 PEF 지시서 조회
        
        Args:
            user_id: 요청하는 사용자 ID
            instruction_pef_id: 조회할 PEF 지시서 ID
            
        Returns:
            InstructionPEF 객체 또는 None
        """
        # 사용자 검증
        BaseService.validate_user(user_id)
        
        # 모든 지시서 중에서 해당 ID의 지시서 찾기
        # 실제로는 리포지토리에 get_by_id 함수가 있으면 좋지만, 현재 예시에서는 모든 지시서를 가져와서 필터링
        pef_data_list = PEFRepository.get_all_pef_instructions()
        
        for pef_data in pef_data_list:
            if pef_data.get('id') == instruction_pef_id:
                return InstructionPEF(
                    id=pef_data.get('id'),
                    performer_id=pef_data.get('performer_id'),
                    file_name=pef_data.get('file_name'),
                    is_fund_item=pef_data.get('is_fund_item'),
                    company_detail=pef_data.get('company_detail'),
                    other_specs_text=pef_data.get('other_specs_text'),
                    created_at=pef_data.get('created_at')
                )
                
        # 해당 ID의 지시서가 없을 경우 None 반환
        return None

    @staticmethod
    def get_transaction_histories_by_pef_id(
        user_id: int,
        instruction_pef_id: int
    ) -> List[TransactionHistory]:
        """
        특정 PEF 지시서의 모든 거래 내역 조회
        
        Args:
            user_id: 요청하는 사용자 ID
            instruction_pef_id: PEF 지시서 ID
            
        Returns:
            거래 내역 목록
        """
        # 사용자 검증
        BaseService.validate_user(user_id)
        
        # 특정 PEF 지시서의 모든 거래 내역 조회 및 모델로 변환
        tx_data_list = PEFRepository.get_transaction_histories_by_pef_instruction_id(instruction_pef_id)
        transaction_histories = []
        
        for tx_data in tx_data_list:
            transaction = TransactionHistory(
                id=tx_data.get('id'),
                instruction_pef_id=tx_data.get('instruction_pef_id'),
                deal_type=tx_data.get('deal_type'),
                deal_object=tx_data.get('deal_object'),
                bank_name=tx_data.get('bank_name'),
                account_number=tx_data.get('account_number'),
                holder_name=tx_data.get('holder_name'),
                amount=tx_data.get('amount'),
                process_date=tx_data.get('process_date')
            )
            transaction_histories.append(transaction)
            
        return transaction_histories
    
    @staticmethod
    def update_transaction_history(
        user_id: int,
        transaction_history: TransactionHistory
    ) -> bool:
        """
        거래 내역 정보 업데이트
        
        Args:
            user_id: 요청하는 사용자 ID
            transaction_history: 업데이트할 거래 내역 객체
            
        Returns:
            성공 여부
        """
        # 사용자 검증
        BaseService.validate_user(user_id)
        
        # 거래 내역 업데이트
        return PEFRepository.update_transaction_history_by_id(transaction_history)

    @staticmethod
    def delete_pef_instruction(
        user_id: int,
        instruction_pef_id: int
    ) -> bool:
        """
        PEF 지시서 삭제
        
        Args:
            user_id: 요청하는 사용자 ID
            instruction_pef_id: 삭제할 PEF 지시서 ID
            
        Returns:
            성공 여부
        """
        # 사용자 검증
        BaseService.validate_user(user_id)
        
        # PEF 지시서 삭제
        return PEFRepository.delete_instruction_pef(instruction_pef_id)

    @staticmethod
    def delete_transaction(
        user_id: int,
        transaction_history_id: int
    ) -> bool:
        """
        거래 내역 삭제
        
        Args:
            user_id: 요청하는 사용자 ID
            transaction_history_id: 삭제할 거래 내역 ID
            
        Returns:
            성공 여부
        """
        # 사용자 검증
        BaseService.validate_user(user_id)
        
        # 거래 내역 삭제
        return PEFRepository.delete_transaction_history(transaction_history_id)