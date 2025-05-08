from repositories.checklist_repository import ChecklistRepository
from repositories.user_repository import UserRepository
from models import User, Checklist
from typing import List, Dict, Any


class ChecklistService:
    @staticmethod
    def validate_system_user(current_user_id: int) -> None:  # 수정: 반환 타입 지정
        """
        시스템 관리자 권한을 검증합니다.
        
        Args:
            current_user_id: 현재 로그인한 사용자 ID
        Raises:
            ValueError: 사용자를 찾을 수 없는 경우
            PermissionError: 시스템 관리자 권한이 없는 경우
        """
        # 현재 사용자 정보 조회
        current_user = UserRepository.find_by_id(current_user_id)
        if not current_user:
            raise ValueError(f"사용자 ID {current_user_id}를 찾을 수 없습니다.")
        if current_user.get('system_role') != 'SYSTEM':
            raise PermissionError("시스템 관리자만 체크리스트 항목을 관리할 수 있습니다.")
    
    @staticmethod
    def add_question(current_user_id: int, question: str) -> dict:
        """
        새로운 체크리스트 항목을 등록합니다.
        시스템 관리자 (SYSTEM) 권한을 가진 사용자만 등록할 수 있습니다.

        Args:
            current_user_id: 현재 로그인한 사용자 ID
            question: 추가할 체크리스트 항목 (질문)
        Returns:
            dict: 성공 메시지
        Raises:
            PermissionError: 권한이 없는 경우
            ValueError: 문항 중복 또는 등록 실패
        """
        ChecklistService.validate_system_user(current_user_id=current_user_id)

        # question 중복 확인
        if ChecklistRepository.find_by_question(question=question):
            raise ValueError("이미 등록된 질문입니다.")
        
        if ChecklistRepository.create_question(question=question):
            return {"message": "체크리스트 문항이 성공적으로 등록되었습니다."}
        else:
            raise ValueError("체크리스트 문항 등록 중 오류가 발생했습니다.")
    
    @staticmethod
    def edit_question(current_user_id: int, checklist_id: int, question: str) -> dict:  # 수정: 매개변수 수정
        """
        실존하는 체크리스트 항목을 수정합니다.
        시스템 관리자 (SYSTEM) 권한을 가진 사용자만 수정할 수 있습니다.

        Args:
            current_user_id: 현재 로그인한 사용자 ID
            checklist_id: 수정할 체크리스트 ID
            question: 수정할 체크리스트 내용
        Returns:
            dict: 성공 메시지
        Raises:
            PermissionError: 권한이 없는 경우
            ValueError: 현존하는 문항이 아닌 경우 또는 수정 실패
        """
        ChecklistService.validate_system_user(current_user_id=current_user_id)

        # question 실존 여부 확인
        if not ChecklistRepository.find_by_id(checklist_id):
            raise ValueError(f"{checklist_id}번 문항을 찾을 수 없습니다.")
            
        if ChecklistRepository.update_question(checklist_id, question):
            return {"message": f"{checklist_id}번 문항이 성공적으로 수정되었습니다."}
        else:
            raise ValueError(f"{checklist_id}번 문항 수정 중 오류가 발생했습니다.")
    
    @staticmethod
    def delete_question(current_user_id: int, checklist_id: int) -> dict:  # 수정: 매개변수 수정
        """
        실존하는 체크리스트 항목을 삭제합니다.
        시스템 관리자 (SYSTEM) 권한을 가진 사용자만 삭제할 수 있습니다.

        Args:
            current_user_id: 현재 로그인한 사용자 ID
            checklist_id: 삭제할 체크리스트 ID
        Returns:
            dict: 성공 메시지
        Raises:
            PermissionError: 권한이 없는 경우
            ValueError: 현존하는 문항이 아닌 경우 또는 삭제 실패
        """
        ChecklistService.validate_system_user(current_user_id=current_user_id)
        
        # question 실존 여부 확인
        if not ChecklistRepository.find_by_id(checklist_id):
            raise ValueError(f"{checklist_id}번 문항을 찾을 수 없습니다.")
            
        if ChecklistRepository.delete_question(checklist_id):
            return {"message": f"{checklist_id}번 문항이 성공적으로 삭제되었습니다."}
        else:
            raise ValueError(f"{checklist_id}번 문항 삭제 중 오류가 발생했습니다.")
    
    @staticmethod
    def get_all_questions() -> List[Dict[str, Any]]:
        """
        모든 체크리스트 항목을 조회합니다.
        
        Returns:
            List[Dict[str, Any]]: 모든 체크리스트 항목 목록
        """
        raw_data = ChecklistRepository.get_all_questions()
        # (id, question) 튜플을 딕셔너리로 변환
        return [Checklist(**raw) for raw in raw_data]