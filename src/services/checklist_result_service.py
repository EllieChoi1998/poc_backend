from typing import Optional, Dict, Any, List
from models import Checklist_Result_Value
from repositories.checklist_result_repository import ChecklistResultRepository
from repositories.user_repository import UserRepository


class ChecklistResultService:
    @staticmethod
    def validate_checklist_user(user_id: int) -> None:
        user = UserRepository.find_by_id(user_id=user_id)
        if not user:
            raise ValueError(f"ID {user_id} 사용자가 존재하지 않습니다.")
        if not UserRepository.find_user_activation(user_id=user_id):
            raise PermissionError(f"사용자 ID {user_id} 계정은 비활성화(삭제)된 계정입니다.")

    @staticmethod
    def get_all_results(user_id: int, contract_id: int) -> Optional[Dict[str, Any]]:
        ChecklistResultService.validate_checklist_user(user_id)
        return ChecklistResultRepository.find_all_checklist_results_by_contract(contract_id)

    @staticmethod
    def edit_memo(user_id: int, checklist_result_id: int, memo: str) -> Dict[str, str]:
        ChecklistResultService.validate_checklist_user(user_id)

        success = ChecklistResultRepository.update_memo(checklist_result_id=checklist_result_id, memo=memo)
        if success:
            return {"message": "메모 수정 완료."}
        raise ValueError("메모 수정 중 오류 발생")

    @staticmethod
    def delete_value(user_id: int, value_id: int) -> Dict[str, str]:
        ChecklistResultService.validate_checklist_user(user_id)

        value = ChecklistResultRepository.get_value_by_value_id(value_id=value_id)
        if not value:
            raise ValueError("해당 값이 존재하지 않습니다.")

        success = ChecklistResultRepository.delete_checklist_result_value(value_id=value_id)
        if success:
            return {"message": f"{value['clause_num']}가 삭제되었습니다."}
        raise ValueError("조항 삭제 중 오류 발생.")

    @staticmethod
    def add_checklist_result(contract_id: int, checklist_id: int, returned_value: Optional[Dict[str, Any]]) -> None:
        """
        AI 서버에서 응답 받아와 SQL 데이터베이스에 저장하는 용도의 서비스 함수.
        """
        if not returned_value:
            return

        values: List[Checklist_Result_Value] = []

        for clause_num, located_page in returned_value.items():
            value = Checklist_Result_Value(
                clause_num=clause_num,
                located_page=located_page
            )
            values.append(value)

        ChecklistResultRepository.create_result(
            contract_id=contract_id,
            checklist_id=checklist_id,
            checklist_result_values=values
        )
