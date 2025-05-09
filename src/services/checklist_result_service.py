from repositories.checklist_result_repository import ChecklistResultRepository
from repositories.user_repository import UserRepository
from typing import List, Dict, Any, Optional
from models import Checklist_Result_Value
from base_service import BaseService

class ChecklistResultService:

    @staticmethod
    def create_result(
        user_id: int,
        contract_id: int,
        checklist_id: int,
        checklist_result_values: Optional[List[Checklist_Result_Value]] = None
    ) -> bool:
        """
        체크리스트 결과를 생성합니다.
        
        Args:
            user_id: 요청한 사용자 ID
            contract_id: 계약서 ID
            checklist_id: 체크리스트 ID
            checklist_result_values: 체크리스트 결과 값 목록 (선택사항)
            
        Returns:
            bool: 성공 여부
            
        Raises:
            ValueError: 사용자가 존재하지 않는 경우
            PermissionError: 사용자 계정이 비활성화된 경우
        """
        # 사용자 유효성 검증
        BaseService.validate_user(user_id)
        
        try:
            result = ChecklistResultRepository.create_result(
                checklist_result_values=checklist_result_values,
                contract_id=contract_id,
                checklist_id=checklist_id
            )
            return result
        except Exception as e:
            raise e

    @staticmethod
    def update_memo(user_id: int, checklist_result_id: int, memo: str) -> bool:
        """
        체크리스트 결과의 메모를 업데이트합니다.
        
        Args:
            user_id: 요청한 사용자 ID
            checklist_result_id: 체크리스트 결과 ID
            memo: 업데이트할 메모 내용
            
        Returns:
            bool: 성공 여부
            
        Raises:
            ValueError: 사용자가 존재하지 않거나 체크리스트 결과가 없는 경우
            PermissionError: 사용자 계정이 비활성화된 경우
        """
        # 사용자 유효성 검증
        BaseService.validate_user(user_id)
        
        try:
            result = ChecklistResultRepository.update_memo(
                checklist_result_id=checklist_result_id,
                memo=memo
            )
            if not result:
                raise ValueError(f"체크리스트 결과 ID {checklist_result_id}를 찾을 수 없습니다.")
            return result
        except Exception as e:
            raise e

    @staticmethod
    def find_all_results_by_contract(user_id: int, contract_id: int) -> Dict[str, Any]:
        """
        계약서 ID별 체크리스트 결과를 조회합니다.
        
        Args:
            user_id: 요청한 사용자 ID
            contract_id: 계약서 ID
            
        Returns:
            Dict[str, Any]: 계약서와 체크리스트 결과 정보
            
        Raises:
            ValueError: 사용자가 존재하지 않는 경우
            PermissionError: 사용자 계정이 비활성화된 경우
        """
        # 사용자 유효성 검증
        BaseService.validate_user(user_id)
        
        try:
            results = ChecklistResultRepository.find_all_checklist_results_by_contract(
                contract_id=contract_id
            )
            return results
        except Exception as e:
            raise e

    @staticmethod
    def delete_result_value(user_id: int, value_id: int) -> bool:
        """
        체크리스트 결과 값을 삭제합니다.
        
        Args:
            user_id: 요청한 사용자 ID
            value_id: 삭제할 체크리스트 결과 값 ID
            
        Returns:
            bool: 성공 여부
            
        Raises:
            ValueError: 사용자가 존재하지 않거나 체크리스트 결과 값이 없는 경우
            PermissionError: 사용자 계정이 비활성화된 경우
        """
        # 사용자 유효성 검증
        BaseService.validate_user(user_id)
        
        # 결과 값 존재 확인
        value = ChecklistResultRepository.get_value_by_value_id(value_id)
        if not value:
            raise ValueError(f"체크리스트 결과 값 ID {value_id}를 찾을 수 없습니다.")
        
        try:
            result = ChecklistResultRepository.delete_checklist_result_value(value_id=value_id)
            if not result:
                raise ValueError(f"체크리스트 결과 값 ID {value_id} 삭제 중 오류가 발생했습니다.")
            return result
        except Exception as e:
            raise e

    @staticmethod
    def delete_result(user_id: int, result_id: int) -> bool:
        """
        체크리스트 결과를 삭제합니다.
        
        Args:
            user_id: 요청한 사용자 ID
            result_id: 삭제할 체크리스트 결과 ID
            
        Returns:
            bool: 성공 여부
            
        Raises:
            ValueError: 사용자가 존재하지 않거나 체크리스트 결과가 없는 경우
            PermissionError: 사용자 계정이 비활성화된 경우
        """
        # 사용자 유효성 검증
        BaseService.validate_user(user_id)
        
        try:
            result = ChecklistResultRepository.delete_checklist_result(result_id=result_id)
            if not result:
                raise ValueError(f"체크리스트 결과 ID {result_id}를 찾을 수 없습니다.")
            return result
        except Exception as e:
            raise e