from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, date

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
    id: Optional[int] = None  # 수정: create시에는 ID가 없을 수 있으므로 Optional 추가
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
    created_at: Optional[datetime]
    is_fund_item: Optional[str]
    company_detail: Optional[str]
    other_specs_text: Optional[str]

class TransactionHistory(BaseModel):
    id: Optional[int] = None
    instruction_pef_id: int
    deal_type: str
    deal_object: str
    bank_name: str
    account_number: str
    holder_name: str
    amount: str
    process_date: date

class InstructionSpecial(BaseModel):
    id: Optional[int] = None
    performer_id : int
    file_name: str
    uploaded_at: Optional[datetime]

class InstructionSpecialResult(BaseModel):
    id: Optional[int] = None
    instruction_special_id: int
    result_content: Optional[str]
    created_at: Optional[datetime]
    usability: Optional[str]
    all_qualities: Optional[str]
    average_quality: Optional[str]
    saved_json: Optional[str]

class Attachment(BaseModel):
    id: Optional[int] = None
    instruction_special_id: int
    file_name: str


# ========= OCR Related Models ==================
class Point(BaseModel):
    x: int
    y: int

class OcrBox(BaseModel):
    label: str
    left_top: Point
    right_top: Point
    right_bottom: Point
    left_bottom: Point
    confidence_score: float

class OcrResult(BaseModel):
    fid: str = ""
    total_pages: int = 0
    full_text: str = ""
    page_file_data: str = ""
    rotate: Optional[int] = None
    boxes: List[OcrBox] = []

class WorkerStatus(BaseModel):
    status: str
    workers: int
    busy: int
    pending: int