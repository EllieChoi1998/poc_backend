from typing import Optional, List, Any
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field

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
    created_at: Optional[datetime] = None
    is_fund_item: Optional[str] = "F"
    company_detail: Optional[str] = ""
    other_specs_text: Optional[str] = ""

class TransactionHistory(BaseModel):
    id: Optional[int] = None
    instruction_pef_id: Optional[int] = None
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
    instruction_special_id: int = None
    result_content: Optional[str] = ""
    created_at: Optional[datetime] = datetime.now()
    usability: Optional[str] = "F"
    all_qualities: Optional[str] = "Unknown dpi"
    average_quality: Optional[str] = "Unknown dpi"
    saved_json: Optional[str] = ""

class Attachment(BaseModel):
    id: Optional[int] = None
    instruction_special_id: Optional[int] = None
    file_name: str


# ========= OCR Related Models ==================
class OcrEngineType(str, Enum):
    GMS = "GMS"

class OcrFileStatus(str, Enum):
    READY = "READY"
    PROCESSING = "PROCESSING"
    COMPLETE = "COMPLETE" 
    ERROR = "ERROR"

class OcrStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"

class Point(BaseModel):
    x: int
    y: int

class OcrBox(BaseModel):
    label: str
    left_top: Point
    right_top: Point
    right_bottom: Point
    left_bottom: Point
    confidence_score: float = 0.0

class OcrResult(BaseModel):
    fid: str = ""
    total_pages: int = 0
    rotate: float = 0.0
    full_text: str = ""
    page_file_data: str = ""
    boxes: List[OcrBox] = Field(default_factory=list)

class OcrPageBase(BaseModel):
    page: int
    full_text: str
    executed_at: datetime
    execute_seconds: float
    ocr_status: OcrStatus
    page_file_data: str
    rotate: float = 0.0

class OcrPage(OcrPageBase):
    id: Optional[int] = None
    ocr_file_id: int
    ocr_boxes: List[OcrBox] = Field(default_factory=list)
    
    class Config:
        orm_mode = True

class OcrPageCreate(OcrPageBase):
    ocr_result: OcrResult
    ocr_boxes: List[OcrBox] = Field(default_factory=list)

class OcrFileBase(BaseModel):
    file_name: str
    file_path: str
    engine_type: OcrEngineType
    ocr_file_status: OcrFileStatus = OcrFileStatus.READY
    total_page: int = 0
    fid: str = ""

class OcrFile(OcrFileBase):
    id: Optional[int] = None
    created_date: datetime
    contract_id: Optional[int] = None
    ocr_pages: List[OcrPage] = Field(default_factory=list)
    
    class Config:
        orm_mode = True

class OcrFileCreate(OcrFileBase):
    created_date: datetime
    contract_id: Optional[int] = None

class OcrFileUpdate(BaseModel):
    total_page: Optional[int] = None
    fid: Optional[str] = None
    ocr_file_status: Optional[OcrFileStatus] = None

class OcrBoxCreate(BaseModel):
    ocr_page_id: int
    label: str
    left_top_x: int
    left_top_y: int
    right_top_x: int
    right_top_y: int
    right_bottom_x: int
    right_bottom_y: int
    left_bottom_x: int
    left_bottom_y: int
    confidence_score: float = 0.0

class WorkerDetail(BaseModel):
    worker_id: int
    is_busy: bool

class WorkerStatus(BaseModel):
    total_workers: int
    busy_workers: int
    worker_details: List[WorkerDetail] = Field(default_factory=list)

# API 응답 모델
class OcrProcessResponse(BaseModel):
    success: bool
    message: str
    ocr_status: str
    ocr_file_id: Optional[int] = None
    # 다른 필드들은 Any 타입으로 정의하여 유연하게 처리
    additional_info: Optional[Any] = None
    
    # Pydantic v2 호환 설정
    model_config = {
        "extra": "allow",  # 추가 필드 허용
        "populate_by_name": True,  # 이름으로 매핑
    }
class OcrResultResponse(BaseModel):
    success: bool
    message: str
    ocr_status: str
    file_info: Optional[dict] = None
    ocr_result: Optional[dict] = None