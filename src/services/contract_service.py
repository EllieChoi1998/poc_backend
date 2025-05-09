from repositories.contract_repository import ContractRepository
from repositories.user_repository import UserRepository
from typing import List, Dict, Any
from models import Contract
from base_service import BaseService


class ContractService:

    @staticmethod
    def upload_contract(uploader_id: int, contract_name: str, file_name: str) -> dict:
        """
        새로운 계약서를 업로드 합니다.
        모든 사용자가 업로드 할 수 있습니다.

        Args:
            uploader_id: 현재 로그인하여 파일을 업로드한 사용자 ID
            contract_name: 사용자가 지정한 계약 이름
            file_name: 업로드한 파일 이름
        Returns:
            dict: 파일 저장 경로 (`contracts/{contract_name}_{file_name}`)
        Raises:
            PermissionError: 활성화된 사용자 여부
            ValueError: 파일 저장 경로 (contract_name, file_name이 모두 중복되는 경우) 중복 또는 등록 실패
        """
        BaseService.validate_user(uploader_id)
        
        if ContractRepository.find_by_file_path(contract_name=contract_name, file_name=file_name):
            raise ValueError(f"이미 존재하는 파일 입니다. 삭제 후 다시 업로드 해 주세요.")

        if ContractRepository.create_contract(uploader_id=uploader_id, contract_name=contract_name, file_name=file_name):
            return {"message": "새로운 계약서가 성공적으로 업로드 되었습니다.", 
                    "file_path": f"contracts/original/{contract_name}_{file_name}"}

    @staticmethod
    def get_all_contracts(user_id: int) -> List[Contract]:
        BaseService.validate_user(user_id)
        raw_data = ContractRepository.get_all_contracts()
        
        # ✅ 딕셔너리 형태 그대로 사용
        return [Contract(**row) for row in raw_data]


    @staticmethod
    def get_only_uploaded_contracts(user_id: int) -> List[Contract]:
        BaseService.validate_user(user_id)
        raw_data = ContractRepository.get_only_uploaded_contracts()
        
        # Contract 모델로 객체 생성
        return [Contract(**data) for data in raw_data]
    
    @staticmethod
    def get_on_progress_checklist_contracts(user_id: int) -> List[Contract]:
        BaseService.validate_user(user_id)
        raw_data = ContractRepository.get_on_progress_checklist_contracts()
        
        # Contract 모델로 객체 생성
        return [Contract(**data) for data in raw_data]
    
    @staticmethod
    def get_finished_checklist_contracts(user_id: int) -> List[Contract]:
        BaseService.validate_user(user_id)
        raw_data = ContractRepository.get_finished_checklist_contracts()
        
        # Contract 모델로 객체 생성
        return [Contract(**data) for data in raw_data]
    
    @staticmethod
    def get_on_progress_keypoint_contracts(user_id: int) -> List[Contract]:
        BaseService.validate_user(user_id)
        raw_data = ContractRepository.get_on_progress_keypoint_contracts()
        
        # Contract 모델로 객체 생성
        return [Contract(**data) for data in raw_data]
    
    @staticmethod
    def get_finished_keypoint_contracts(user_id: int) -> List[Contract]:
        BaseService.validate_user(user_id)
        raw_data = ContractRepository.get_finished_keypoint_contracts()

        
        # Contract 모델로 객체 생성
        return [Contract(**data) for data in raw_data]