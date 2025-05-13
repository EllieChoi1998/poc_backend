# src/services/special_service.py

from repositories.special_repository import SpecialRepository
from repositories.user_repository import UserRepository
from typing import Optional, List, Dict, Any
from models import InstructionSpecial, InstructionSpecialResult, Attachment
from base_service import BaseService
from datetime import date

"""
모든 서비스에서 사용자 검증은 필수 항목이다.
    BaseService.validate_user(user_id=user_id)
사용 필수.
"""
class SpecialService(BaseService):
    @staticmethod
    def create_special_instruction_with_result(
        user_id: int,
        special: InstructionSpecial,
        result: Optional[InstructionSpecialResult] = None,
        attachments: Optional[List[Attachment]] = None
    ) -> int:
        # 사용자 검증
        BaseService.validate_user(user_id=user_id)

        # 모든 내역 생성
        instruction_special_id = SpecialRepository.create_with_result(
            performer_id=user_id,
            file_name=special.file_name,
            result=result,
            attachments=attachments
        )

        return instruction_special_id
    
    @staticmethod
    def create_another_result(
        user_id: int,
        instruction_special_id: int,
        result: Optional[InstructionSpecialResult] = None
    ) -> bool:
        # 사용자 검증
        BaseService.validate_user(user_id=user_id)
        
        # 새로운 result 생성
        success = SpecialRepository.create_another_result(
            instruction_special_id=instruction_special_id,
            result=result
        )
        
        return success
    
    @staticmethod
    def update_result_content(
        user_id: int,
        instruction_special_id: int,
        result_id: int,
        new_content: str
    ) -> bool:
        # 사용자 검증
        BaseService.validate_user(user_id=user_id)
        
        # result_content 업데이트
        success = SpecialRepository.update_result_content(
            instruction_special_id=instruction_special_id,
            result_id=result_id,
            new_content=new_content
        )
        
        return success
    
    @staticmethod
    def update_result_usability(
        user_id: int,
        instruction_special_id: int,
        result_id: int,
        usability: str
    ) -> bool:
        # 사용자 검증
        BaseService.validate_user(user_id=user_id)
        
        # usability 업데이트
        success = SpecialRepository.update_result_usability(
            instruction_special_id=instruction_special_id,
            result_id=result_id,
            usability=usability
        )
        
        return success
    
    @staticmethod
    def update_result_json(
        user_id: int,
        instruction_special_id: int,
        result_id: int,
        new_json: str
    ) -> bool:
        # 사용자 검증
        BaseService.validate_user(user_id=user_id)
        
        # saved_json 업데이트
        success = SpecialRepository.update_result_json(
            instruction_special_id=instruction_special_id,
            result_id=result_id,
            new_json=new_json
        )
        
        return success
    
    @staticmethod
    def get_all_special_instructions(user_id: int) -> List[Dict[str, Any]]:
        # 사용자 검증
        BaseService.validate_user(user_id=user_id)
        
        # 모든 special instruction 조회
        instructions = SpecialRepository.get_all_special_instructions()
        
        return instructions
    
    @staticmethod
    def get_all_results_by_special_instruction_id(
        user_id: int,
        instruction_special_id: int
    ) -> List[Dict[str, Any]]:
        # 사용자 검증
        BaseService.validate_user(user_id=user_id)
        
        # 특정 instruction_special_id에 대한 모든 results 조회
        results = SpecialRepository.get_all_results_by_special_instruction_id(
            instruction_special_id=instruction_special_id
        )
        
        return results
    
    @staticmethod
    def get_result_by_id(
        user_id: int,
        result_id: int
    ) -> Dict[str, Any]:
        # 사용자 검증
        BaseService.validate_user(user_id=user_id)
        
        # 특정 result_id에 대한 result 조회
        result = SpecialRepository.get_result_by_id(result_id=result_id)
        
        return result
    
    @staticmethod
    def delete_result_by_id(
        user_id: int,
        result_id: int
    ) -> bool:
        # 사용자 검증
        BaseService.validate_user(user_id=user_id)
        
        # 특정 result_id에 대한 result 삭제
        success = SpecialRepository.delete_result_by_id(result_id=result_id)
        
        return success
    
    @staticmethod
    def delete_special_instruction(
        user_id: int,
        instruction_special_id: int
    ) -> bool:
        # 사용자 검증
        BaseService.validate_user(user_id=user_id)
        
        # 특정 instruction_special_id에 대한 special instruction 삭제
        success = SpecialRepository.delete_special_instruction(
            instruction_special_id=instruction_special_id
        )
        
        return success