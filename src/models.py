from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class User(BaseModel):
    login_id: str
    ibk_id: str
    name: str
    password: str
    hiearchy: str
    system_role: str
    team_id: Optional[int] = None
    activate: str = 'T'
    refresh_token: Optional[str] = None

class LoginModel(BaseModel):
    login_id: str
    password: str

class LogoutRequest(BaseModel):
    user_id: int

class Checklist(BaseModel):
    checklist_id: Optional[int] = None  # 수정: create시에는 ID가 없을 수 있으므로 Optional 추가
    question: str

class TermsNConditions(BaseModel):
    termsNconditions_id: Optional[int] = None  # 수정: create시에는 ID가 없을 수 있으므로 Optional 추가
    code: str
    query: str

class Contract(BaseModel):
    id: Optional[int] = None
    contract_name: str # = 파일 위치, 생성 규칙 : 
    file_name: str
    embedding_id: Optional[str] = None
    uploader_id: int
    keypoint_processer_id: Optional[int] = None
    checklist_processer_id: Optional[int] = None
    uploaded_at: Optional[datetime]
    keypoint_processed: Optional[datetime] = None
    checklist_processed: Optional[datetime] = None
    checklist_printable_file_path: Optional[str] = None
    current_state: int = 0

class Checklist_Result(BaseModel):
    id: Optional[int] = None
    contract_id: int
    checklist_id: int
    memo: Optional[str] = None

class Checklist_Result_Value(BaseModel):
    id: Optional[int] = None
    checklist_result_id: Optional[int] = None
    clause_num: str
    located_page: int

class KeypointResultCreate(BaseModel):
    contract_id: int
    termsNconditions_id: int

class AIKeypointResultCreate(BaseModel):
    contract_id: int
    termsNconditions_id: int
    match_rate: float


class InstructionPEF(BaseModel):
    id: Optional[int] = None
    performer_id: int
    file_name: str
    created_at: Optional[datetime] = None

class InstructionPEFResult(BaseModel):
    id: Optional[int] = None
    instruction_pef_id: int
    is_fund_item: Optional[str] = 'F'
    company_detail: Optional[str] = None

class TransactionHistory(BaseModel):
    id: Optional[int] = None
    instruction_pef_result_id: int
    deal_type: Optional[str] = None
    deal_object: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    holder_name: Optional[str] = None
    amount: Optional[str] = None
    process_date: Optional[datetime] = None

class OtherSpecifications(BaseModel):
    id: Optional[int] = None
    instruction_pef_result_id: int
    other_specs_text: Optional[str] = None
    other_specs_detail: Optional[str] = None

class InstructionSpecial(BaseModel):
    id: Optional[int] = None
    performer_id: int
    file_name: str
    uploaded_at: Optional[datetime] = None

class InstructionSpecialResult(BaseModel):
    id: Optional[int] = None
    instruction_special_id: int
    result_content: Optional[str] = None
    created_at: Optional[datetime] = None
    usability: Optional[str] = 'F'
    average_quality: Optional[str] = None
    saved_json_file_path: Optional[str] = None