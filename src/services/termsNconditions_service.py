from repositories.termsNconditions_repository import TermsNConditionsRepository
from repositories.user_repository import UserRepository
from models import User, Checklist
from typing import List, Dict, Any
import logging

class TermsNConditionsService:
    @staticmethod
    def validate_system_user(current_user_id: int) -> None:  # 수정: 반환 타입 지정
        """
        유저 검증을 합니다.
        
        Args:
            current_user_id: 현재 로그인한 사용자 ID
        Raises:
            ValueError: 사용자를 찾을 수 없는 경우
            PermissionError: 시스템 관리자 권한이 없는 경우
        """
        # 현재 사용자 정보 조회
        current_user = UserRepository.find_by_id(current_user_id)
        logging.info(current_user)
        if not current_user:
            raise ValueError(f"사용자 ID {current_user_id}를 찾을 수 없습니다.")
        
    
    @staticmethod
    def add_query(current_user_id: int, code: str, query: str) -> dict:
        """
        새로운 약관제한목록 항목을 등록합니다.
        시스템 관리자 (SYSTEM) 권한을 가진 사용자만 등록할 수 있습니다.

        Args:
            current_user_id: 현재 로그인한 사용자 ID
            query: 추가할 약관제한목록 항목 (질문)
        Returns:
            dict: 성공 메시지
        Raises:
            PermissionError: 권한이 없는 경우
            ValueError: 제한명 중복 또는 등록 실패
        """
        TermsNConditionsService.validate_system_user(current_user_id=current_user_id)

        # query 중복 확인
        if TermsNConditionsRepository.find_by_query(query=query):
            raise ValueError("이미 등록된 질문입니다.")
        if TermsNConditionsRepository.find_by_code(code=code):
            raise ValueError("이미 등록된 질문입니다.")
        
        
        if TermsNConditionsRepository.create_query(query=query, code=code):
            return {"message": "약관제한목록 제한명이 성공적으로 등록되었습니다."}
        else:
            raise ValueError("약관제한목록 제한명 등록 중 오류가 발생했습니다.")
    
    @staticmethod
    def edit_query(current_user_id: int, termsNconditions_id: int, query: str, code: str) -> dict:  # 수정: 매개변수 수정
        """
        실존하는 약관제한목록 항목을 수정합니다.

        Args:
            current_user_id: 현재 로그인한 사용자 ID
            termsNconditions_id: 수정할 약관제한목록 ID
            query: 수정할 약관제한목록 내용
        Returns:
            dict: 성공 메시지
        Raises:
            PermissionError: 권한이 없는 경우
            ValueError: 현존하는 제한명이 아닌 경우 또는 수정 실패
        """
        TermsNConditionsService.validate_system_user(current_user_id=current_user_id)
        
        # query 실존 여부 확인
        if not TermsNConditionsRepository.find_by_id(termsNconditions_id):
            raise ValueError(f"{termsNconditions_id}번 제한명을 찾을 수 없습니다.")
        elif TermsNConditionsRepository.exists_by_query_excluding_id(query=query, exclude_id=termsNconditions_id):
            raise ValueError("이미 등록된 질문입니다.")
        elif TermsNConditionsRepository.exists_by_code_excluding_id(code=code, exclude_id=termsNconditions_id):
            raise ValueError("이미 등록된 질문입니다.")
            
        if TermsNConditionsRepository.update_query(termsNconditions_id=termsNconditions_id, query=query, code=code):
            return {"message": f"{termsNconditions_id}번 제한명이 성공적으로 수정되었습니다."}
        else:
            raise ValueError(f"{termsNconditions_id}번 제한명 수정 중 오류가 발생했습니다.")
    
    @staticmethod
    def delete_query(current_user_id: int, termsNconditions_id: int) -> dict:  # 수정: 매개변수 수정
        """
        실존하는 약관제한목록 항목을 삭제합니다.

        Args:
            current_user_id: 현재 로그인한 사용자 ID
            termsNconditions_id: 삭제할 약관제한목록 ID
        Returns:
            dict: 성공 메시지
        Raises:
            PermissionError: 권한이 없는 경우
            ValueError: 현존하는 제한명이 아닌 경우 또는 삭제 실패
        """
        TermsNConditionsService.validate_system_user(current_user_id=current_user_id)
        
        # query 실존 여부 확인
        if not TermsNConditionsRepository.find_by_id(termsNconditions_id):
            raise ValueError(f"{termsNconditions_id}번 제한명을 찾을 수 없습니다.")
            
        if TermsNConditionsRepository.delete_query(termsNconditions_id):
            return {"message": f"{termsNconditions_id}번 제한명이 성공적으로 삭제되었습니다."}
        else:
            raise ValueError(f"{termsNconditions_id}번 제한명 삭제 중 오류가 발생했습니다.")
    
    @staticmethod
    def get_all_querys() -> List[Dict[str, Any]]:
        """
        모든 약관제한목록 항목을 조회합니다.
        
        Returns:
            List[Dict[str, Any]]: 모든 약관제한목록 항목 목록
        """
        raw_data = TermsNConditionsRepository.get_all_querys()
        # (id, query) 튜플을 딕셔너리로 변환
        return raw_data