from typing import Dict, Any
from repositories.keypoint_result_repository import KeypointResultRepository
from base_service import BaseService

class KeypointResultService:

    @staticmethod
    def add_by_user(user_id: int, contract_id: int, termsNconditions_id: int) -> bool:
        """
        사용자에 의한 키포인트 결과 추가
        
        Args:
            user_id: 요청한 사용자 ID
            contract_id: 계약서 ID
            termsNconditions_id: 약관 ID
            
        Returns:
            bool: 성공 여부
            
        Raises:
            ValueError: 사용자가 존재하지 않거나 키포인트 결과가 이미 존재하는 경우
            PermissionError: 사용자 계정이 비활성화된 경우
        """
        # 사용자 유효성 검증
        BaseService.validate_user(user_id)
        
        # 기본 매치 레이트 (사용자 입력으로 100%)
        match_rate = 100.0
        
        try:
            # 사용자가 직접 추가하는 경우 중복 체크 로직이 있는 메서드 사용
            result = KeypointResultRepository.create_result_by_user(
                contract_id=contract_id,
                terms_id=termsNconditions_id,
                # match_rate=match_rate
            )
            return result
        except ValueError:
            raise ValueError(f"이미 contract_id {contract_id}와 termsNconditions_id {termsNconditions_id}에 대한 결과가 존재합니다.")
        except Exception as e:
            raise e

    @staticmethod
    def add_by_ai(match_rate: float, contract_id: int, termsNconditions_id: int) -> bool:
        """
        AI에 의한 키포인트 결과 추가
        
        Args:
            match_rate: 매치 레이트 (0.0 ~ 100.0)
            contract_id: 계약서 ID
            termsNconditions_id: 약관 ID
            
        Returns:
            bool: 성공 여부
            
        Raises:
            ValueError: 매치 레이트가 유효하지 않은 범위인 경우
            Exception: 데이터베이스 오류 등 기타 예외
        """
        # 매치 레이트 검증
        if not (0.0 <= match_rate <= 100.0):
            raise ValueError("매치 레이트는 0.0에서 100.0 사이의 값이어야 합니다.")
        
        try:
            # AI가 추가하는 경우 중복 체크 없이 추가
            result = KeypointResultRepository.create_result_by_ai(
                contract_id=contract_id,
                terms_id=termsNconditions_id,
                match_rate=match_rate
            )
            return result
        except Exception as e:
            raise e

    @staticmethod
    def get_all_results_by_contract_id(user_id: int, contract_id: int) -> Dict[str, Any]:
        """
        계약서 ID별 모든 키포인트 결과 조회
        
        Args:
            user_id: 요청한 사용자 ID
            contract_id: 계약서 ID
            
        Returns:
            Dict[str, Any]: 계약서 ID와 결과 목록이 포함된 딕셔너리
            
        Raises:
            ValueError: 사용자가 존재하지 않거나 결과가 없는 경우
            PermissionError: 사용자 계정이 비활성화된 경우
        """
        # 사용자 유효성 검증
        BaseService.validate_user(user_id)
        
        # 결과 조회
        results = KeypointResultRepository.find_result_by_contract_id(contract_id=contract_id)
        
        if not results:
            return {"contract_id": contract_id, "results": []}
        
        return results

    @staticmethod
    def delete_keypoint_result(user_id: int, keypoint_result_id: int) -> bool:
        """
        키포인트 결과 삭제
        
        Args:
            user_id: 요청한 사용자 ID
            keypoint_result_id: 삭제할 키포인트 결과 ID
            
        Returns:
            bool: 성공 여부
            
        Raises:
            ValueError: 사용자가 존재하지 않거나 결과를 찾을 수 없는 경우
            PermissionError: 사용자 계정이 비활성화된 경우
        """
        # 사용자 유효성 검증
        BaseService.validate_user(user_id)
        
        # 결과 삭제
        result = KeypointResultRepository.delete_keypoint_result(result_id=keypoint_result_id)
        
        if not result:
            raise ValueError(f"키포인트 결과 ID {keypoint_result_id}를 찾을 수 없습니다.")
        
        return True