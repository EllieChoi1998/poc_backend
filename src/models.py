from typing import Optional
from pydantic import BaseModel

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

class Contract(BaseModel):
    document_id: Optional[int] = None # create 시에는 ID가 없을 수 있으므로 Optional 처리
    document_name: str
    file_name: str
    embedding_id: Optional[str] = None # nullable
    doc_type: Optional[str] = None # create 시에는 없을 수 있음
    uploader: Optional[str] = None # create 시 삽입해야 하므로
    keypoint_processer: Optional[str] = None # 핵심사항 추출한 사람 기록 용 (최초엔 없음)
    checklist_processer: Optional[str] = None # 체크리스트 수행한 사람 기록 용 (최초엔 없음)
    uploaded_at: Optional[str] = None # create 시 삽입해야 함
    keypoint_proccessed: Optional[str] = None # 핵심사항 추출한 일자 기록 용 (최초엔 없음)
    checklist_proccessed: Optional[str] = None # 체크리스트 수행한 일자 기록 용 (최초엔 없음)
    current_state: Optional[int] = 0 # Default 0 으로 처리 가능

class TermsNConditions(BaseModel):
    termsNconditions_id: Optional[int] = None  # 수정: create시에는 ID가 없을 수 있으므로 Optional 추가
    code: str
    query: str